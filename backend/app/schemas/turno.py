from datetime import time

from pydantic import BaseModel, ConfigDict, Field


class BloqueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    orden: int
    hora_inicio: time
    hora_fin: time
    etiqueta: str


class TurnoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    clave: str
    nombre: str
    bloques: list[BloqueOut] = Field(default_factory=list)
