from fastapi import APIRouter, Depends

from deps import get_status_service
from services.status import StatusService

router = APIRouter(prefix='/api', tags=['estado'])


@router.get('/status')
def status(service: StatusService = Depends(get_status_service)):
    return service.resumen()
