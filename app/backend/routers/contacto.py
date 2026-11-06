from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from deps import get_contacto_service
from services.contacto import ContactoService

router = APIRouter(tags=['contacto'])


@router.post('/api/leads/{lead_id}/guion')
def crear_guion(lead_id: int, service: ContactoService = Depends(get_contacto_service)):
    return service.crear_guion(lead_id)


@router.post('/api/leads/{lead_id}/maqueta')
def crear_maqueta(lead_id: int, service: ContactoService = Depends(get_contacto_service)):
    return service.crear_maqueta(lead_id)


@router.get('/maquetas/{archivo}')
def ver_maqueta(archivo: str, service: ContactoService = Depends(get_contacto_service)):
    return FileResponse(service.ruta_maqueta(archivo), media_type='text/html')
