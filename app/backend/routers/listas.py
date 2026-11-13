from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, Response

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


@router.post('/muestra')
def muestra(body: PedidoLista, service: ListasService = Depends(get_listas_service)):
    """CSV de 10 leads para enseñar gratis a una agencia. No registra ninguna entrega."""
    nombre, contenido = service.muestra_gratis(body)
    return Response(contenido, media_type='text/csv; charset=utf-8',
                    headers={'Content-Disposition': f'attachment; filename="{nombre}"'})


@router.get('/archivo/{nombre}')
def descargar(nombre: str, service: ListasService = Depends(get_listas_service)):
    return FileResponse(service.archivo(nombre), media_type='text/csv', filename=nombre)
