"""Errores de negocio. Los servicios los lanzan; la capa HTTP los traduce a respuestas."""


class AppError(Exception):
    status_code = 400

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class BadRequestError(AppError):
    status_code = 400


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


class UpstreamError(AppError):
    """Falla un servicio externo (p. ej. la IA)."""
    status_code = 502
