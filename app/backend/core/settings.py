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
