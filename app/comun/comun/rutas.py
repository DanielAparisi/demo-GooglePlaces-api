"""Rutas de los ficheros que comparten scripts y backend."""
from pathlib import Path

# El paquete se instala en modo editable (pip install -e app/comun), así que __file__
# sigue apuntando a app/comun/comun/rutas.py dentro del repositorio.
ROOT = Path(__file__).resolve().parents[3]          # raíz del repositorio
DIR_SCRAPER = ROOT / 'app' / 'scraper-python'

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
