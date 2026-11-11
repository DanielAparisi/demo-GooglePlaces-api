"""Código compartido con los scripts de scraper-python.

Las reglas de dominio, el acceso al CSV (con su bloqueo entre procesos) y el cliente de
IA viven en scraper-python/comun/ porque los scripts también los usan. Este módulo es el
único punto del backend que ajusta sys.path para importarlos.
"""
import sys

from core.settings import ROOT

_SCRAPER_DIR = str(ROOT / 'app' / 'scraper-python')
if _SCRAPER_DIR not in sys.path:
    sys.path.insert(0, _SCRAPER_DIR)

from comun import calibracion, ia, leads_csv  # noqa: E402
from comun.dominio import ciudad_de, limpiar_dato, nombre_comercial, sector_de, tipo_telefono  # noqa: E402
from comun.oportunidad import NOMBRES_BLOQUE, PESOS_BASE, cargar_pesos, puntuar  # noqa: E402

__all__ = ['calibracion', 'ia', 'leads_csv', 'NOMBRES_BLOQUE', 'PESOS_BASE', 'cargar_pesos', 'ciudad_de', 'limpiar_dato', 'nombre_comercial', 'puntuar', 'sector_de',
           'tipo_telefono']
