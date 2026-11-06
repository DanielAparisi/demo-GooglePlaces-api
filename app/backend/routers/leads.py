from fastapi import APIRouter, Depends

from deps import get_leads_service
from schemas.leads import LlamadaRequest, SelectAllRequest, SelectRequest
from services.leads import LeadsService

router = APIRouter(prefix='/api/leads', tags=['leads'])


@router.get('')
def listar(service: LeadsService = Depends(get_leads_service)):
    return service.listar()


@router.patch('/select')
def seleccionar(body: SelectRequest, service: LeadsService = Depends(get_leads_service)):
    service.seleccionar(body.ids, body.selected)
    return {'ok': True}


@router.patch('/select-all')
def seleccionar_todos(body: SelectAllRequest, service: LeadsService = Depends(get_leads_service)):
    service.seleccionar_todos(body.selected)
    return {'ok': True}


@router.patch('/select-not-emailed')
def seleccionar_sin_email_previo(service: LeadsService = Depends(get_leads_service)):
    """Selecciona solo los leads cuyo email nunca ha sido enviado."""
    return {'ok': True, 'selected': service.seleccionar_sin_email_previo()}


@router.patch('/{lead_id}/llamada')
def actualizar_llamada(lead_id: int, body: LlamadaRequest, service: LeadsService = Depends(get_leads_service)):
    service.actualizar_llamada(lead_id, body.estado)
    return {'ok': True}
