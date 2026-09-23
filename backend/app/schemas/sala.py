from datetime import time

from pydantic import BaseModel, ConfigDict, Field


class SalaBase(BaseModel):
    codigo: str = Field(max_length=10, examples=["H-21"])
    nombre: str = Field(max_length=120, examples=["Planetario"])
    es_funcion: bool = False
    solo_super: bool = False
    comida_default: time = Field(examples=["13:30:00"])
    orden: int = 0
    activa: bool = True


class SalaCrear(SalaBase):
    pass


class SalaActualizar(BaseModel):
    nombre: str | None = Field(default=None, max_length=120)
    es_funcion: bool | None = None
    solo_super: bool | None = None
    comida_default: time | None = None
    orden: int | None = None
    activa: bool | None = None


class SalaOut(SalaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ParComidaOut(BaseModel):
    """Dos salas cuyos guías no pueden comer a la misma hora."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    sala_a_id: int
    sala_b_id: int
