"""Modelo de oportunidad: cómo está acertando y recalibración con las llamadas."""
from pathlib import Path

from core.domain import NOMBRES_BLOQUE, PESOS_BASE, calibracion, cargar_pesos
from core.errors import BadRequestError
from repositories.leads import LeadsRepository


class OportunidadService:
    def __init__(self, repo: LeadsRepository, pesos_file: Path):
        self.repo = repo
        self.pesos_file = Path(pesos_file)

    def _leads(self) -> list[dict]:
        return self.repo.read().to_dict(orient='records')

    def resumen(self) -> dict:
        leads = self._leads()
        pesos = cargar_pesos(self.pesos_file)
        ultima = calibracion.leer(self.pesos_file)
        return {
            'bloques': [
                {'id': b, 'nombre': NOMBRES_BLOQUE[b], 'peso': pesos[b], 'peso_base': PESOS_BASE[b]}
                for b in PESOS_BASE
            ],
            'calibrado': None if not ultima else {
                k: ultima.get(k) for k in ('fecha', 'resultados', 'interesados', 'confianza')
            },
            'estado': calibracion.estado(leads),
            'rendimiento': calibracion.rendimiento(leads, pesos),
        }

    def calibrar(self) -> dict:
        try:
            nueva = calibracion.calibrar(self._leads())
        except ValueError as e:
            raise BadRequestError(str(e)) from e
        calibracion.guardar(self.pesos_file, nueva)
        return self.resumen()

    def restablecer(self) -> dict:
        self.pesos_file.unlink(missing_ok=True)
        return self.resumen()
