"""Preparar contacto: guion de llamada y maqueta de web para un lead."""
import re
from pathlib import Path

from core.domain import sector_de
from core.errors import BadRequestError, NotFoundError, UpstreamError
from core.settings import Settings
from repositories.leads import LeadsRepository
from services import guion, maqueta

_NOMBRE_MAQUETA = re.compile(r'[a-z0-9-]+\.html')


class ContactoService:
    def __init__(self, settings: Settings, repo: LeadsRepository):
        self._settings = settings
        self._repo = repo

    # La generación (lenta) ocurre fuera del candado del CSV: solo se escribe el campo
    # resultante, así no se pisan cambios hechos mientras tanto (p. ej. selecciones).

    def crear_guion(self, lead_id: int) -> dict:
        lead = self._repo.get(lead_id)
        try:
            texto = guion.generar_guion(lead)
        except Exception as e:
            raise UpstreamError(f'No se pudo generar el guion: {e}') from e
        self._repo.set_fields(lead_id, Guion=texto)
        return {'guion': texto, 'sector': sector_de(lead)}

    def crear_maqueta(self, lead_id: int) -> dict:
        lead = self._repo.get(lead_id)
        try:
            archivo = maqueta.generar_maqueta(lead, lead_id, self._settings.maquetas_dir)
        except ValueError as e:
            raise BadRequestError(str(e)) from e
        self._repo.set_fields(lead_id, Maqueta=archivo)
        return {'maqueta': archivo, 'url': f'/maquetas/{archivo}'}

    def ruta_maqueta(self, archivo: str) -> Path:
        # Solo nombres generados por maqueta._slug: nada de rutas ni ../
        if not _NOMBRE_MAQUETA.fullmatch(archivo):
            raise NotFoundError('Maqueta no encontrada')
        ruta = self._settings.maquetas_dir / archivo
        if not ruta.exists():
            raise NotFoundError('Maqueta no encontrada')
        return ruta
