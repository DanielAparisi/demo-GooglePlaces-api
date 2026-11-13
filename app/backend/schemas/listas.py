from pydantic import BaseModel, Field


class PedidoLista(BaseModel):
    cliente: str
    plan: str | None = None
    # Si no se indica, la fija el plan
    cantidad: int | None = Field(default=None, gt=0, le=5000)
    sectores: list[str] = []
    ciudades: list[str] = []
    requiere: list[str] = []
    puntuacion_min: int = Field(default=0, ge=0, le=100)
    exclusivo: bool = False
