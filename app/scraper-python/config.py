"""Carga de credenciales desde el .env de la raíz del proyecto (sin dependencias).

Las reglas de dominio viven en comun/dominio.py; se reexportan aquí para que
`from config import sector_de` siga funcionando.
"""
import os

from comun.dominio import ciudad_de, limpiar_dato, nombre_comercial, sector_de, tipo_telefono  # noqa: F401
from comun.rutas import ENV_FILE


def _cargar_env():
    if not ENV_FILE.exists():
        return
    for linea in ENV_FILE.read_text().splitlines():
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
