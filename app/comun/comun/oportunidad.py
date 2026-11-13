"""Predice qué negocios necesitan (y comprarían) una página web: puntuación 0-100 explicada.

El modelo suma bloques de señales. Cada bloque da una fracción entre 0 y 1 (cuánto cumple
el lead esa señal) que se multiplica por su peso; los pesos suman 100. Los pesos de partida
están puestos con criterio comercial; `comun/calibracion.py` los ajusta con los resultados
reales de las llamadas y los guarda en `pesos_oportunidad.json`.

Bloques y peso de partida:
  web         40  sin web = 1 · solo red social / directorio = 0.75 · web propia = descartado
  demanda     15  nº de reseñas en Google (escala logarítmica, satura en 150)
  reputacion  10  valoración media (un negocio bien valorado cuida su imagen)
  actividad   10  horario publicado (mitad) y fotos (mitad)
  contacto    12  móvil/WhatsApp 2/3, fijo 1/3 · email +1/3
  sector       8  ticket medio y peso de la búsqueda local en el sector
  redes        5  tiene redes pero no web: ya invierte en digital

Una señal *desconocida* (lead antiguo sin ese dato) cuenta como media: así los leads
anteriores a este modelo no quedan injustamente al final. Un 0 explícito sí cuenta 0.
"""
import json
import math
import re
from pathlib import Path

from comun.dominio import sector_de, tipo_telefono

PESOS_BASE = {
    'web': 40, 'demanda': 15, 'reputacion': 10, 'actividad': 10,
    'contacto': 12, 'sector': 8, 'redes': 5,
}
NOMBRES_BLOQUE = {
    'web': 'Presencia web', 'demanda': 'Demanda (reseñas)', 'reputacion': 'Reputación',
    'actividad': 'Ficha de Google', 'contacto': 'Contacto', 'sector': 'Sector', 'redes': 'Redes sociales',
}

# Dominios que Google Maps acepta como "website" pero no son una web del negocio.
# Esos negocios siguen necesitando una web propia: son leads, no descartes.
_WEB_DEBIL = re.compile(
    r'(facebook\.com|fb\.com|instagram\.com|tiktok\.com|twitter\.com|x\.com|linkedin\.com|'
    r'youtube\.com|linktr\.ee|linkin\.bio|wa\.me|whatsapp\.com|business\.site|'
    r'sites\.google\.com|g\.page|maps\.app\.goo\.gl|goo\.gl|bit\.ly|'
    r'paginasamarillas\.es|habitissimo\.es|cronoshare\.com|doctoralia\.es|'
    r'top-doctors\.es|treatwell\.es|booksy\.com|fresha\.com)',
    re.I,
)

FRACCION_SECTOR = {'reformas': 1.0, 'fisioterapia': 1.0, 'taller': 0.75}
FRACCION_SECTOR_OTRO = 0.375
COLUMNAS_REDES = ['Facebook', 'Instagram', 'LinkedIn', 'Twitter', 'TikTok', 'YouTube']

UMBRAL_ALTA = 70
UMBRAL_MEDIA = 45


def tipo_web(url):
    """'' (sin web), 'debil' (red social, directorio, enlace corto...) o 'propia'."""
    url = str(url or '').strip()
    if not url:
        return ''
    return 'debil' if _WEB_DEBIL.search(url) else 'propia'


def necesita_web(url):
    """Filtro del scraper: todo lo que no sea una web propia es candidato."""
    return tipo_web(url) != 'propia'


def _numero(valor):
    """float o None si el dato no se conoce (vacío o no numérico)."""
    try:
        texto = str(valor).strip().replace(',', '.')
        return float(texto) if texto else None
    except (TypeError, ValueError):
        return None


def _si_no(valor):
    """True/False/None a partir de 'True', 'False', '1', '' ..."""
    texto = str(valor or '').strip().lower()
    if texto in ('true', '1', 'si', 'sí', 'yes'):
        return True
    if texto in ('false', '0', 'no'):
        return False
    return None


def nivel(puntuacion):
    if puntuacion >= UMBRAL_ALTA:
        return 'Alta'
    if puntuacion >= UMBRAL_MEDIA:
        return 'Media'
    return 'Baja'


# ── Bloques: cada uno devuelve (fracción 0-1, motivo o None) ──────────────────

def _web(lead):
    if tipo_web(lead.get('Web actual')) == 'debil':
        return 0.75, 'Su "web" es solo una red social o un directorio'
    return 1.0, 'No tiene página web'


def _demanda(lead):
    resenas = _numero(lead.get('Reseñas'))
    if resenas is None:
        return 0.5, None
    fraccion = min(1.0, math.log10(1 + resenas) / math.log10(151))
    if resenas >= 50:
        return fraccion, f'{int(resenas)} reseñas: mucha gente le busca en Google'
    if resenas >= 10:
        return fraccion, f'{int(resenas)} reseñas: negocio con clientela'
    if resenas == 0:
        return fraccion, 'Sin reseñas: poca actividad visible'
    return fraccion, None


def _reputacion(lead):
    resenas, valoracion = _numero(lead.get('Reseñas')), _numero(lead.get('Valoración'))
    if resenas == 0:
        return 0.0, None
    if valoracion is None:
        return 0.5, None
    if valoracion >= 4.5:
        return 1.0, f'Valoración {valoracion:.1f}★: cuida a sus clientes'
    if valoracion >= 4.0:
        return 0.7, None
    if valoracion >= 3.5:
        return 0.3, None
    return 0.0, f'Valoración baja ({valoracion:.1f}★)'


def _actividad(lead):
    horario, fotos = _si_no(lead.get('Horario')), _numero(lead.get('Fotos'))
    fraccion = {True: 0.5, False: 0.0, None: 0.2}[horario]
    fraccion += 0.3 if fotos is None else (0.5 if fotos >= 3 else 0.2 if fotos >= 1 else 0.0)
    motivo = 'Ficha de Google cuidada (horario y fotos)' if horario and fotos and fotos >= 3 else None
    return fraccion, motivo


def _contacto(lead):
    tipo_tel = lead.get('Tipo teléfono') or tipo_telefono(lead.get('Teléfono'))
    fraccion = {'Móvil': 2 / 3, 'Fijo': 1 / 3}.get(tipo_tel, 0.0)
    if str(lead.get('Email') or '').strip():
        fraccion += 1 / 3
    return fraccion, 'Móvil: contactable por WhatsApp' if tipo_tel == 'Móvil' else None


def _sector(lead):
    sector = sector_de(lead)
    motivo = {
        'fisioterapia': 'Sector donde la reserva online vende sola',
        'reformas': 'Sector de ticket alto: la web se amortiza rápido',
    }.get(sector)
    return FRACCION_SECTOR.get(sector, FRACCION_SECTOR_OTRO), motivo


def _redes(lead):
    if any(str(lead.get(r) or '').strip() for r in COLUMNAS_REDES):
        return 1.0, 'Tiene redes sociales pero no web'
    return 0.0, None


_BLOQUES = {
    'web': _web, 'demanda': _demanda, 'reputacion': _reputacion, 'actividad': _actividad,
    'contacto': _contacto, 'sector': _sector, 'redes': _redes,
}


def descartado(lead):
    """Motivo por el que no es un lead (ya tiene web, cerrado) o None."""
    estado = str(lead.get('Estado negocio') or '').upper()
    if estado in ('CLOSED_PERMANENTLY', 'CLOSED_TEMPORARILY'):
        return 'Negocio cerrado en Google Maps'
    if tipo_web(lead.get('Web actual')) == 'propia':
        return 'Ya tiene web propia'
    return None


def bloques(lead):
    """{bloque: (fracción 0-1, motivo o None)}. Lo usa también la calibración."""
    return {nombre: fn(lead) for nombre, fn in _BLOQUES.items()}


def puntuar(lead, pesos=None):
    """{'puntuacion': 0-100, 'nivel': 'Alta'|'Media'|'Baja', 'motivos': [str, ...]}

    `lead` es una fila del CSV (claves en español). `pesos` son los calibrados
    (ver `cargar_pesos`); sin ellos se usan los de partida.
    """
    motivo = descartado(lead)
    if motivo:
        return {'puntuacion': 0, 'nivel': 'Baja', 'motivos': [motivo]}

    pesos = pesos or PESOS_BASE
    total, motivos = 0.0, []
    for nombre, (fraccion, motivo) in bloques(lead).items():
        total += fraccion * pesos.get(nombre, 0)
        if motivo:
            motivos.append(motivo)
    puntuacion = max(0, min(100, int(round(100 * total / (sum(pesos.values()) or 1)))))
    return {'puntuacion': puntuacion, 'nivel': nivel(puntuacion), 'motivos': motivos}


# ── Pesos calibrados en disco ─────────────────────────────────────────────────

_cache = {}


def cargar_pesos(ruta):
    """Pesos de `ruta` si existe y es válida; si no, los de partida.

    Se cachea por fecha de modificación: el panel ve una recalibración sin reiniciarse.
    """
    ruta = Path(ruta)
    try:
        mtime = ruta.stat().st_mtime
    except OSError:
        return dict(PESOS_BASE)
    if _cache.get(ruta, (None,))[0] != mtime:
        try:
            leidos = json.loads(ruta.read_text(encoding='utf-8')).get('pesos', {})
            pesos = {b: float(leidos.get(b, PESOS_BASE[b])) for b in PESOS_BASE}
            if any(p < 0 for p in pesos.values()) or sum(pesos.values()) <= 0:
                raise ValueError('pesos no válidos')
        except (ValueError, TypeError, AttributeError):
            pesos = dict(PESOS_BASE)
        _cache[ruta] = (mtime, pesos)
    return dict(_cache[ruta][1])
