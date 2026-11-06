"""CORS y protección frente a peticiones de otros orígenes."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from core.settings import Settings

METODOS_SEGUROS = {'GET', 'HEAD', 'OPTIONS'}


def install_security(app: FastAPI, settings: Settings) -> None:
    allowed_origins = set(settings.allowed_origins)

    # CORS no impide que otra web dispare un POST (solo le impide leer la respuesta),
    # así que además rechazamos cualquier petición de navegador con un Origin ajeno.
    # Las que cambian estado (lanzan envíos o modifican el CSV) deben traer además un
    # Origin permitido: una petición sin Origin no viene del frontend.
    @app.middleware('http')
    async def bloquear_origenes_desconocidos(request: Request, call_next):
        origin = request.headers.get('origin')
        if origin and origin not in allowed_origins:
            return JSONResponse(status_code=403, content={'detail': 'Origen no permitido'})
        if request.method not in METODOS_SEGUROS and not origin:
            return JSONResponse(status_code=403, content={'detail': 'Falta la cabecera Origin'})
        return await call_next(request)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.allowed_origins),
        allow_methods=['*'],
        allow_headers=['*'],
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(settings.allowed_hosts))
