from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core.errors import AppError
from core.security import install_security
from core.settings import Settings
from deps import build_services
from routers import contacto, leads, outreach, status


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(title='Lead Generator API')
    app.state.settings = settings
    app.state.services = build_services(settings)

    @app.exception_handler(AppError)
    async def manejar_error_de_negocio(_: Request, exc: AppError):
        return JSONResponse(status_code=exc.status_code, content={'detail': exc.detail})

    install_security(app, settings)
    for router in (leads.router, outreach.router, contacto.router, status.router):
        app.include_router(router)
    return app


app = create_app()
