"""Lanzamiento de los envíos masivos (WhatsApp, email, Instagram).

Cada canal es un proceso externo. Solo se permite uno por canal a la vez: lanzar dos
manda mensajes duplicados (ambos leen el mismo log de enviados) y corrompe el log.
"""
import subprocess
from dataclasses import dataclass

from core.errors import BadRequestError, ConflictError, NotFoundError
from core.settings import Settings
from repositories.leads import LeadsRepository, selected_mask


@dataclass(frozen=True)
class Canal:
    nombre: str
    comando: list[str]
    # Columna que debe tener contenido para poder contactar por este canal (None = basta con estar seleccionado)
    columna_requerida: str | None = None
    etiqueta: str = ''


class OutreachService:
    def __init__(self, settings: Settings, repo: LeadsRepository):
        self._settings = settings
        self._repo = repo
        self._procesos: dict[str, subprocess.Popen] = {}

    def _canales(self) -> dict[str, Canal]:
        s = self._settings
        py = str(s.python_bin)
        return {
            'whatsapp': Canal('whatsapp', ['node', str(s.send_whatsapp_script), '--selected-only']),
            'email': Canal('email', [py, str(s.send_email_script), '--selected-only'], 'Email', 'email'),
            'instagram': Canal('instagram', [py, str(s.send_instagram_script), '--selected-only'], 'Instagram', 'Instagram'),
        }

    def lanzar(self, nombre: str) -> dict:
        canal = self._canales()[nombre]
        df = self._repo.read()
        marcados = df[selected_mask(df)]
        if marcados.empty:
            raise BadRequestError('No hay leads seleccionados')

        destinatarios = len(marcados)
        if canal.columna_requerida:
            destinatarios = int((marcados[canal.columna_requerida] != '').sum())
            if destinatarios == 0:
                raise BadRequestError(f'Ningún lead seleccionado tiene {canal.etiqueta}')

        proc = self._procesos.get(nombre)
        if proc and proc.poll() is None:
            raise ConflictError(f'Ya hay un envío de {nombre} en curso (PID {proc.pid})')
        self._procesos[nombre] = proc = subprocess.Popen(canal.comando, cwd=self._settings.root)
        return {'ok': True, 'pid': proc.pid, 'selected': destinatarios}

    def ruta_qr(self):
        """Último QR generado por send_whatsapp.js (se regenera cada ~30 s)."""
        if not self._settings.qr_file.exists():
            raise NotFoundError('Aún no hay QR: lanza el envío de WhatsApp primero')
        return self._settings.qr_file
