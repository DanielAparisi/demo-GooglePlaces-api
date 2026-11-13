"""Reglas de negocio sobre los datos de un lead. Las usan los scripts y el backend."""
import re


def limpiar_dato(valor, maximo=100):
    """Deja un dato externo (p. ej. el nombre de un negocio de Google Maps) listo para
    meterlo en un prompt: una sola línea, sin comillas y con longitud acotada, para
    que no pueda colar instrucciones al modelo."""
    valor = re.sub(r'[\x00-\x1f\x7f"`]', ' ', str(valor or ''))
    return re.sub(r'\s+', ' ', valor).strip()[:maximo]


def tipo_telefono(telefono):
    """'Móvil' (6xx/7xx, tiene WhatsApp), 'Fijo' (9xx/8xx, solo llamada) o '' si no hay número."""
    limpio = re.sub(r'[^\d+]', '', str(telefono or ''))
    if limpio.startswith('+34'):
        limpio = limpio[3:]
    elif limpio.startswith('34') and len(limpio) == 11:
        limpio = limpio[2:]
    if not limpio:
        return ''
    return 'Móvil' if limpio[0] in '67' else 'Fijo'


# Palabras clave buscadas en categoría + nombre. Google suele devolver "Negocio"
# como categoría, así que el nombre ("Reformas X", "Taller Y") es la pista principal.
_SECTORES = {
    'reformas':     ['reforma', 'contratista', 'construcc', 'albañil', 'obras'],
    'taller':       ['taller', 'mecánic', 'mecanic', 'automoci', 'chapa'],
    'fisioterapia': ['fisio', 'osteopat', 'rehabilitaci', 'fisioterap'],
}


def sector_de(lead):
    texto = f"{lead.get('Categoría', '')} {lead.get('Nombre del negocio', '')}".lower()
    for sector, claves in _SECTORES.items():
        if any(c in texto for c in claves):
            return sector
    return None


_PARTE_CON_CP = re.compile(r'^\d{5}\s+(.+)$')


def ciudad_de(ubicacion):
    """Ciudad de una dirección de Google Maps.

    La ciudad va justo detrás del código postal, sea cual sea el número de partes:
      "C. Mayor, 1, 30201 Cartagena, Murcia, Spain"      → "Cartagena"
      "C. Delicias, 5, Arganzuela, 28005 Madrid, Spain"  → "Madrid"
    Sin código postal ("Madrid, Spain") se usa la penúltima parte.
    """
    partes = [p.strip() for p in str(ubicacion or '').split(',') if p.strip()]
    for parte in reversed(partes):
        m = _PARTE_CON_CP.match(parte)
        if m:
            return m.group(1)
    if len(partes) >= 2:
        return partes[-2]
    return partes[0] if partes else ''


def nombre_comercial(nombre):
    """"REFORMAS DE LEVANTE - Reformas en Cartagena" → "Reformas De Levante"."""
    corto = str(nombre or '').split(' - ')[0].strip()
    return corto.title() if corto.isupper() else corto
