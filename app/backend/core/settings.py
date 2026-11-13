"""Configuración y rutas del backend, en un único sitio."""
from dataclasses import dataclass
from pathlib import Path

# app/backend/core/settings.py → raíz del repositorio
ROOT = Path(__file__).resolve().parents[3]

LOGS_ENVIOS = {
    'whatsapp': 'whatsapp_log.json',
    'email': 'email_log.json',
    'instagram': 'instagram_log.json',
}


@dataclass(frozen=True)
class Settings:
    root: Path = ROOT

    # Solo el frontend local puede llamar a la API: estos endpoints lanzan envíos
    # reales de WhatsApp/email, así que nunca deben quedar abiertos a cualquier origen.
    allowed_origins: tuple[str, ...] = ('http://localhost:4321', 'http://127.0.0.1:4321')
    # Rechaza cualquier Host que no sea local: evita DNS rebinding.
    allowed_hosts: tuple[str, ...] = ('localhost', '127.0.0.1')

    @property
    def csv_file(self) -> Path:
        return self.root / 'Leads Google Maps.csv'

    @property
    def pesos_file(self) -> Path:
        """Pesos calibrados del modelo de oportunidad (los escribe calibrar.py o el panel)."""
        return self.root / 'pesos_oportunidad.json'

    @property
    def entregas_file(self) -> Path:
        """Registro de listas vendidas a agencias (también lo usa crear_lista.py)."""
        return self.root / 'entregas.json'

    @property
    def listas_dir(self) -> Path:
        """CSV entregados a agencias."""
        return self.root / 'listas'

    @property
    def search_state_file(self) -> Path:
        """Búsquedas de Google Places ya hechas (para no sugerir repetirlas)."""
        return self.root / 'app' / 'scraper-python' / 'search_state.json'

    @property
    def maquetas_dir(self) -> Path:
        return self.root / 'maquetas'

    @property
    def qr_file(self) -> Path:
        return self.root / 'qr.png'

    @property
    def send_whatsapp_script(self) -> Path:
        return self.root / 'app' / 'whatsApp_node' / 'send_whatsapp.js'

    @property
    def send_email_script(self) -> Path:
        return self.root / 'app' / 'scraper-python' / 'send_emails.py'

    @property
    def send_instagram_script(self) -> Path:
        return self.root / 'app' / 'scraper-python' / 'send_instagram.py'

    @property
    def python_bin(self) -> Path:
        return self.root / 'app' / 'backend' / '.venv' / 'bin' / 'python3'

    def log_file(self, canal: str) -> Path:
        return self.root / LOGS_ENVIOS[canal]
