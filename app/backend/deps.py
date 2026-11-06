"""Contenedor de servicios y dependencias de FastAPI.

`create_app` construye los servicios una vez y los deja en `app.state`; los routers los
reciben por `Depends`. Así los tests pueden montar la app con rutas temporales.
"""
from dataclasses import dataclass

from fastapi import Request

from core.settings import Settings
from repositories.leads import LeadsRepository
from repositories.logs import SendLogsRepository
from services.contacto import ContactoService
from services.leads import LeadsService
from services.outreach import OutreachService
from services.status import StatusService


@dataclass
class Services:
    leads: LeadsService
    outreach: OutreachService
    contacto: ContactoService
    status: StatusService


def build_services(settings: Settings) -> Services:
    repo = LeadsRepository(settings.csv_file)
    logs = SendLogsRepository(settings)
    return Services(
        leads=LeadsService(repo, logs),
        outreach=OutreachService(settings, repo),
        contacto=ContactoService(settings, repo),
        status=StatusService(logs),
    )


def get_leads_service(request: Request) -> LeadsService:
    return request.app.state.services.leads


def get_outreach_service(request: Request) -> OutreachService:
    return request.app.state.services.outreach


def get_contacto_service(request: Request) -> ContactoService:
    return request.app.state.services.contacto


def get_status_service(request: Request) -> StatusService:
    return request.app.state.services.status
