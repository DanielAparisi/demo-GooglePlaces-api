from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from deps import get_listas_service
from schemas.listas import PedidoLista
from services.listas import ListasService

router = APIRouter(prefix='/api/listas', tags=['listas'])


@router.get('')
def resumen(service: ListasService = Depends(get_listas_service)):
    """Planes de suscripción, agencias con su próxima entrega e historial de listas."""
    return service.resumen()


@router.post('/simular')
def simular(body: PedidoLista, service: ListasService = Depends(get_listas_service)):
    return service.simular(body)


@router.post('')
def crear(body: PedidoLista, service: ListasService = Depends(get_listas_service)):
    return service.crear(body)


@router.get('/archivo/{nombre}')
def descargar(nombre: str, service: ListasService = Depends(get_listas_service)):
    return FileResponse(service.archivo(nombre), media_type='text/csv', filename=nombre)
