"""Rutas de los ficheros que comparten scripts y backend."""
from pathlib import Path

DIR_SCRAPER = Path(__file__).resolve().parents[1]   # app/scraper-python
ROOT = DIR_SCRAPER.parents[1]                       # raíz del repositorio

ENV_FILE = ROOT / '.env'
CSV_FILE = ROOT / 'Leads Google Maps.csv'
BAJAS_FILE = ROOT / 'bajas.txt'
PESOS_FILE = ROOT / 'pesos_oportunidad.json'   # modelo de oportunidad calibrado (calibrar.py)
ENTREGAS_FILE = ROOT / 'entregas.json'         # listas vendidas a agencias (crear_lista.py)
LISTAS_DIR = ROOT / 'listas'                   # CSV entregados a agencias
IG_SESSION_FILE = ROOT / '.ig_session.json'

LOG_WHATSAPP = ROOT / 'whatsapp_log.json'
LOG_EMAIL = ROOT / 'email_log.json'
LOG_INSTAGRAM = ROOT / 'instagram_log.json'

# Estado del buscador de Google Places
USAGE_FILE = DIR_SCRAPER / 'usage.json'
SEARCH_STATE_FILE = DIR_SCRAPER / 'search_state.json'
