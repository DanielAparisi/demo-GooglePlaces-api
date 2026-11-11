from fastapi import APIRouter, Depends

from deps import get_oportunidad_service
from services.oportunidad import OportunidadService

router = APIRouter(prefix='/api/oportunidad', tags=['oportunidad'])


@router.get('')
def resumen(service: OportunidadService = Depends(get_oportunidad_service)):
    """Pesos actuales, cuántas llamadas faltan para calibrar y tasa de interés por prioridad."""
    return service.resumen()


@router.post('/calibrar')
def calibrar(service: OportunidadService = Depends(get_oportunidad_service)):
    """Recalcula los pesos con las llamadas marcadas como Interesado / No interesado."""
    return service.calibrar()


@router.delete('/calibrar')
def restablecer(service: OportunidadService = Depends(get_oportunidad_service)):
    """Vuelve a los pesos de partida."""
    return service.restablecer()
