"""Código compartido con los scripts de scraper-python.

Las reglas de dominio, el acceso al CSV (con su bloqueo entre procesos) y el cliente de
IA viven en el paquete `comun` (app/comun), instalado en el venv con requirements.txt.
"""
from comun import entorno  # noqa: F401  (carga el .env de la raíz: GROQ_API_KEY, LANDING_URL…)
from comun import calibracion, ia, leads_csv, listas
from comun.dominio import ciudad_de, limpiar_dato, nombre_comercial, sector_de, tipo_telefono
from comun.oportunidad import NOMBRES_BLOQUE, PESOS_BASE, cargar_pesos, puntuar

__all__ = ['calibracion', 'ia', 'leads_csv', 'listas', 'NOMBRES_BLOQUE', 'PESOS_BASE', 'cargar_pesos', 'ciudad_de', 'limpiar_dato', 'nombre_comercial', 'puntuar', 'sector_de',
           'tipo_telefono']
