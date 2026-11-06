"""Logs de envíos (JSON) que escriben los scripts de WhatsApp, email e Instagram."""
import json

from core.settings import Settings


class SendLogsRepository:
    def __init__(self, settings: Settings):
        self._settings = settings

    def enviados(self, canal: str) -> list[dict]:
        ruta = self._settings.log_file(canal)
        if not ruta.exists():
            return []
        try:
            return json.loads(ruta.read_text(encoding='utf-8')).get('enviados', [])
        except json.JSONDecodeError:
            # El script de envío puede estar escribiendo justo ahora: no tumbamos el panel.
            return []

    def emails_enviados(self) -> set[str]:
        return {e['email'].strip() for e in self.enviados('email') if e.get('email')}

    def contar(self, canal: str) -> int:
        return len(self.enviados(canal))
