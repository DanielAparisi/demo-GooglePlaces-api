"""Carga de credenciales desde el .env de la raíz del proyecto (sin dependencias)."""
import os
import re

_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
ENV_FILE = os.path.join(_ROOT, '.env')


def _cargar_env():
    if not os.path.exists(ENV_FILE):
        return
    with open(ENV_FILE) as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith('#') or '=' not in linea:
                continue
            clave, valor = linea.split('=', 1)
            os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


_cargar_env()


def requerir(nombre):
    valor = os.environ.get(nombre, '')
    if not valor:
        raise SystemExit(
            f"Falta la variable {nombre}. Añádela al archivo .env de la raíz "
            f"(copia .env.example) o expórtala como variable de entorno."
        )
    return valor


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
