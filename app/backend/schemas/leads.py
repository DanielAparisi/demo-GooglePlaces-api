from pydantic import BaseModel


class SelectRequest(BaseModel):
    ids: list[int]
    selected: bool


class SelectAllRequest(BaseModel):
    selected: bool


class LlamadaRequest(BaseModel):
    estado: str
