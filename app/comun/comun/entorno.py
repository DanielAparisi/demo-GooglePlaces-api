"""Carga de credenciales desde el .env de la raíz del proyecto (sin dependencias).

Se carga al importar el módulo, así que basta con `from comun.entorno import requerir`
para tener GROQ_API_KEY, LANDING_URL… en `os.environ`.
"""
import os

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
