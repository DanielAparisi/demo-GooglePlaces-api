"""Crea listas de leads para vender a agencias (sector + ciudad, por planes).

Algoritmo de `crear_lista(leads, pedido, entregas)`:

1. Candidatos: leads que encajan con el pedido.
   · Sector: el detectado por `sector_de` o el texto de la categoría / nombre
     ("panaderia" encuentra "Panadería"). Sin sectores = todos.
   · Ciudad: cualquier parte de la dirección (barrio, ciudad o provincia), sin
     tildes y con nombres alternativos (Elche = Elx). Sin ciudades = todas.
   · Canales obligatorios (móvil, teléfono, email, redes) y puntuación mínima.
   · Fuera: con web propia o cerrados, los que ya están en tu cartera ("Interesado").
2. Frescura y exclusividad (registro de entregas):
   · Nunca se repite un lead que ya se entregó a ese mismo cliente.
   · Un lead vendido con exclusividad no se vuelve a vender a nadie.
   · Un pedido exclusivo solo lleva leads que no se han vendido nunca.
3. Orden: puntuación de oportunidad, luego datos más completos (más canales de
   contacto), luego los más recientes.
4. Reparto: turno rotatorio entre los grupos sector × ciudad, para que una lista de
   "talleres y reformas en Murcia y Cartagena" no salga entera de un único grupo.
5. Si faltan leads, se sugieren las búsquedas de Google Places que conviene lanzar.
"""
import csv
import json
import re
import unicodedata
from datetime import date
from pathlib import Path

from comun.dominio import ciudad_de, nombre_comercial, sector_de
from comun.ficheros import escribir_atomico, guardar_json
from comun.oportunidad import COLUMNAS_REDES, descartado, puntuar

# Suscripción mensual: cada mes se entrega una lista nueva sin repetir leads.
# Los planes viven en planes.json porque la landing (landing/) también los publica.
PLANES = {k: v for k, v in json.loads((Path(__file__).with_name('planes.json')).read_text(encoding='utf-8')).items()
          if not k.startswith('_')}
CANALES = ('movil', 'telefono', 'email', 'redes')

# Sector de la lista → búsqueda de script.py (TIPOS_NEGOCIO) para sugerir búsquedas
BUSQUEDA_SECTOR = {'reformas': 'empresa de reformas', 'taller': 'taller mecánico', 'fisioterapia': 'fisioterapia'}

# Nombres de ciudad que Google devuelve en otro idioma
_ALIAS_CIUDAD = {
    'elche': 'elx', 'alicante': 'alacant', 'castellon': 'castello', 'gerona': 'girona',
    'lerida': 'lleida', 'la coruna': 'a coruna', 'orense': 'ourense', 'san sebastian': 'donostia',
    'vitoria': 'gasteiz', 'pamplona': 'iruna', 'palma de mallorca': 'palma',
}

_CP = re.compile(r'^\d{5}\s*')

COLUMNAS_ENTREGA = [
    'Negocio', 'Sector', 'Ciudad', 'Dirección', 'Teléfono', 'Tipo teléfono', 'Email',
    *COLUMNAS_REDES, 'Web actual', 'Reseñas', 'Valoración', 'Oportunidad', 'Prioridad', 'Por qué',
]


def normalizar(texto):
    """Minúsculas, sin tildes ni signos: 'Leganés' → 'leganes', "L'Hospitalet" → 'l hospitalet'."""
    texto = unicodedata.normalize('NFKD', str(texto or '')).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', ' ', texto).strip()


def clave(lead):
    """Identifica un negocio igual que leads_csv.anadir: nombre + dirección."""
    return (str(lead.get('Nombre del negocio') or ''), str(lead.get('Ubicación') or ''))


# ── Filtros ───────────────────────────────────────────────────────────────────

_NOMBRE_SECTOR = {'reformas': 'Reformas', 'taller': 'Taller mecánico', 'fisioterapia': 'Fisioterapia'}


def etiqueta_sector(lead):
    """Sector para agrupar y mostrar: el detectado o, si no, la categoría de Google."""
    detectado = sector_de(lead)
    if detectado:
        return _NOMBRE_SECTOR.get(detectado, detectado)
    return str(lead.get('Categoría') or '').strip() or 'Otros'


def encaja_sector(lead, sectores):
    if not sectores:
        return True
    texto = normalizar(f"{lead.get('Categoría', '')} {lead.get('Nombre del negocio', '')}")
    detectado = sector_de(lead)
    for s in sectores:
        s = normalizar(s)
        if s == detectado or (s and s in texto):
            return True
    return False


def zona_de(lead, ciudades):
    """Ciudad pedida en la que está el lead (tal cual se pidió), o None."""
    partes = [normalizar(_CP.sub('', p)) for p in str(lead.get('Ubicación') or '').split(',')]
    partes = [p for p in partes if p]
    for ciudad in ciudades:
        buscadas = {normalizar(ciudad)}
        buscadas.add(_ALIAS_CIUDAD.get(normalizar(ciudad), normalizar(ciudad)))
        if any(b and (b == p or re.search(rf'\b{re.escape(b)}\b', p)) for b in buscadas for p in partes):
            return ciudad
    return None


def tiene_canal(lead, canal):
    if canal == 'movil':
        return lead.get('Tipo teléfono') == 'Móvil'
    if canal == 'telefono':
        return bool(str(lead.get('Teléfono') or '').strip())
    if canal == 'email':
        return bool(str(lead.get('Email') or '').strip())
    if canal == 'redes':
        return any(str(lead.get(r) or '').strip() for r in COLUMNAS_REDES)
    raise ValueError(f'Canal desconocido: {canal}')


def _n_canales(lead):
    return sum(tiene_canal(lead, c) for c in ('telefono', 'email', 'redes'))


# ── Registro de entregas ──────────────────────────────────────────────────────

def bloqueados(entregas, cliente, exclusivo):
    """Claves que no pueden ir en este pedido y por qué."""
    ya_suyos, exclusivos_ajenos, vendidos = set(), set(), set()
    for e in entregas:
        claves = {tuple(k) for k in e.get('leads', [])}
        vendidos |= claves
        if e.get('cliente') == cliente:
            ya_suyos |= claves
        elif e.get('exclusivo'):
            exclusivos_ajenos |= claves
    return {'ya_entregados': ya_suyos, 'exclusivos': exclusivos_ajenos, 'vendidos': vendidos if exclusivo else set()}


# ── Algoritmo ─────────────────────────────────────────────────────────────────

def crear_lista(leads, pedido, entregas=(), pesos=None, busquedas_hechas=()):
    """Devuelve {'leads': [...], 'pedido', 'resumen', 'sugerencias'}.

    `pedido`: cliente, cantidad, sectores, ciudades, requiere (canales),
    puntuacion_min, exclusivo. Cada lead devuelto lleva `_puntuacion`, `_nivel`,
    `_motivos`, `_sector` y `_zona` para exportarlo.
    """
    cliente = str(pedido.get('cliente') or '').strip()
    if not cliente:
        raise ValueError('Falta el cliente')
    cantidad = int(pedido.get('cantidad') or 0)
    if cantidad <= 0:
        raise ValueError('La cantidad debe ser mayor que 0')
    sectores = [s for s in pedido.get('sectores') or [] if str(s).strip()]
    ciudades = [c for c in pedido.get('ciudades') or [] if str(c).strip()]
    requiere = list(pedido.get('requiere') or [])
    for canal in requiere:
        if canal not in CANALES:
            raise ValueError(f'Canal desconocido: {canal}. Usa: {", ".join(CANALES)}')
    minimo = int(pedido.get('puntuacion_min') or 0)
    exclusivo = bool(pedido.get('exclusivo'))

    bloq = bloqueados(entregas, cliente, exclusivo)
    descartes = {'no_encajan': 0, 'sin_canal': 0, 'puntuacion_baja': 0, 'en_tu_cartera': 0,
                 'ya_entregados': 0, 'exclusivos_de_otro': 0, 'ya_vendidos': 0}
    candidatos = []
    for orden, lead in enumerate(leads):
        if descartado(lead) or not encaja_sector(lead, sectores):
            descartes['no_encajan'] += 1
            continue
        zona = zona_de(lead, ciudades) if ciudades else ciudad_de(lead.get('Ubicación'))
        if ciudades and zona is None:
            descartes['no_encajan'] += 1
            continue
        if not all(tiene_canal(lead, c) for c in requiere):
            descartes['sin_canal'] += 1
            continue
        if str(lead.get('Llamada') or '').strip() == 'Interesado':
            descartes['en_tu_cartera'] += 1
            continue
        k = clave(lead)
        if k in bloq['ya_entregados']:
            descartes['ya_entregados'] += 1
            continue
        if k in bloq['exclusivos']:
            descartes['exclusivos_de_otro'] += 1
            continue
        if k in bloq['vendidos']:
            descartes['ya_vendidos'] += 1
            continue
        o = puntuar(lead, pesos)
        if o['puntuacion'] < minimo:
            descartes['puntuacion_baja'] += 1
            continue
        candidatos.append({**lead, '_puntuacion': o['puntuacion'], '_nivel': o['nivel'], '_motivos': o['motivos'],
                           '_sector': etiqueta_sector(lead), '_zona': zona or '', '_orden': orden})

    # Mejores primero: puntuación, datos más completos, más recientes
    candidatos.sort(key=lambda l: (-l['_puntuacion'], -_n_canales(l), -l['_orden']))

    # Turno rotatorio entre grupos sector × zona (los grupos con mejor lead empiezan)
    grupos = {}
    for l in candidatos:
        grupos.setdefault((normalizar(l['_sector']), normalizar(l['_zona'])), []).append(l)
    colas = list(grupos.values())
    elegidos = []
    while len(elegidos) < cantidad and colas:
        for cola in colas:
            if len(elegidos) < cantidad and cola:
                elegidos.append(cola.pop(0))
        colas = [c for c in colas if c]

    faltan = cantidad - len(elegidos)
    return {
        'leads': elegidos,
        'pedido': {'cliente': cliente, 'plan': pedido.get('plan') or None, 'cantidad': cantidad, 'sectores': sectores, 'ciudades': ciudades,
                   'requiere': requiere, 'puntuacion_min': minimo, 'exclusivo': exclusivo},
        'resumen': {
            'pedidos': cantidad, 'entregados': len(elegidos), 'faltan': faltan, 'disponibles': len(candidatos),
            'descartes': descartes,
            'por_nivel': {n: sum(l['_nivel'] == n for l in elegidos) for n in ('Alta', 'Media', 'Baja')},
            'por_grupo': _por_grupo(elegidos),
            'puntuacion_media': round(sum(l['_puntuacion'] for l in elegidos) / len(elegidos), 1) if elegidos else 0,
        },
        'sugerencias': sugerir_busquedas(sectores, ciudades, busquedas_hechas) if faltan > 0 else [],
    }


def _por_grupo(elegidos):
    conteo = {}
    for l in elegidos:
        k = f"{l['_sector']} · {l['_zona'] or '—'}"
        conteo[k] = conteo.get(k, 0) + 1
    return dict(sorted(conteo.items(), key=lambda kv: -kv[1]))


def sugerir_busquedas(sectores, ciudades, hechas=(), maximo=10):
    """Búsquedas para script.py que darían más leads de este pedido, sin repetir las ya hechas."""
    hechas = {normalizar(h) for h in hechas}
    tipos = []
    for s in sectores or BUSQUEDA_SECTOR:
        tipos.append(BUSQUEDA_SECTOR.get(normalizar(s), str(s).strip()))
    sugerencias = []
    for tipo in tipos:
        for ciudad in ciudades or ['<ciudad>']:
            busqueda = f'{tipo} en {ciudad}'
            if normalizar(busqueda) not in hechas and busqueda not in sugerencias:
                sugerencias.append(busqueda)
    return sugerencias[:maximo]


# ── Exportación y registro ────────────────────────────────────────────────────

def filas_entrega(lista):
    """Filas para el CSV que recibe la agencia: sin columnas internas (selección, guiones...)."""
    filas = []
    for l in lista['leads']:
        filas.append({
            'Negocio': nombre_comercial(l.get('Nombre del negocio')),
            'Sector': l['_sector'],
            'Ciudad': ciudad_de(l.get('Ubicación')),
            'Dirección': l.get('Ubicación') or '',
            'Teléfono': l.get('Teléfono') or '',
            'Tipo teléfono': l.get('Tipo teléfono') or '',
            'Email': l.get('Email') or '',
            **{r: l.get(r) or '' for r in COLUMNAS_REDES},
            'Web actual': l.get('Web actual') or '',
            'Reseñas': l.get('Reseñas') or '',
            'Valoración': l.get('Valoración') or '',
            'Oportunidad': l['_puntuacion'],
            'Prioridad': l['_nivel'],
            'Por qué': ' · '.join(l['_motivos']),
        })
    return filas


def exportar(lista, carpeta):
    """Escribe el CSV de la entrega en `carpeta` sin pisar otros. Devuelve su ruta."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    nombre = f"{normalizar(lista['pedido']['cliente']).replace(' ', '-')}-{len(lista['leads'])}-leads"
    ruta = carpeta / f"{nombre}.csv"
    n = 2
    while ruta.exists():
        ruta = carpeta / f"{nombre}-{n}.csv"
        n += 1

    escribir_atomico(ruta, lambda f: escribir_csv(f, lista), encoding='utf-8-sig')  # utf-8-sig: Excel abre bien las tildes
    return ruta


def escribir_csv(f, lista):
    w = csv.DictWriter(f, fieldnames=COLUMNAS_ENTREGA)
    w.writeheader()
    w.writerows(filas_entrega(lista))


def leer_entregas(ruta):
    ruta = Path(ruta)
    if not ruta.exists():
        return []
    try:
        return json.loads(ruta.read_text(encoding='utf-8')).get('entregas', [])
    except ValueError as e:
        # Mejor parar que vender dos veces un lead exclusivo por un registro ilegible
        raise ValueError(f"El registro de entregas '{ruta.name}' está dañado: {e}") from e


def registrar_entrega(ruta, lista, archivo='', hoy=None):
    """Apunta la entrega para no repetir leads ni romper exclusividades. Devuelve su id."""
    entregas = leer_entregas(ruta)
    hoy = str(hoy or date.today())
    cliente = lista['pedido']['cliente']
    n = sum(1 for e in entregas if e.get('cliente') == cliente) + 1
    entrega = {
        'id': f"{normalizar(cliente).replace(' ', '-')}-{hoy}-{n}",
        'cliente': cliente,
        'fecha': hoy,
        'exclusivo': lista['pedido']['exclusivo'],
        'pedido': lista['pedido'],
        'archivo': archivo,
        'leads': [list(clave(l)) for l in lista['leads']],
    }
    guardar_json(Path(ruta), {'entregas': [*entregas, entrega]})
    return entrega['id']
