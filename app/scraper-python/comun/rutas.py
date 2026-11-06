"""Rutas de los ficheros que comparten scripts y backend."""
from pathlib import Path

DIR_SCRAPER = Path(__file__).resolve().parents[1]   # app/scraper-python
ROOT = DIR_SCRAPER.parents[1]                       # raíz del repositorio

ENV_FILE = ROOT / '.env'
CSV_FILE = ROOT / 'Leads Google Maps.csv'
BAJAS_FILE = ROOT / 'bajas.txt'
IG_SESSION_FILE = ROOT / '.ig_session.json'

LOG_WHATSAPP = ROOT / 'whatsapp_log.json'
LOG_EMAIL = ROOT / 'email_log.json'
LOG_INSTAGRAM = ROOT / 'instagram_log.json'

# Estado del buscador de Google Places
USAGE_FILE = DIR_SCRAPER / 'usage.json'
SEARCH_STATE_FILE = DIR_SCRAPER / 'search_state.json'
