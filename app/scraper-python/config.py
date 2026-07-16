"""Carga de credenciales desde el .env de la raíz del proyecto (sin dependencias)."""
import os

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
