from typing import Literal

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from deps import get_outreach_service
from services.outreach import OutreachService

router = APIRouter(prefix='/api', tags=['envíos'])


@router.post('/{canal}/launch')
def lanzar(canal: Literal['whatsapp', 'email', 'instagram'], service: OutreachService = Depends(get_outreach_service)):
    return service.lanzar(canal)


@router.get('/whatsapp/qr')
def qr_whatsapp(service: OutreachService = Depends(get_outreach_service)):
    return FileResponse(service.ruta_qr(), media_type='image/png', headers={'Cache-Control': 'no-store'})
