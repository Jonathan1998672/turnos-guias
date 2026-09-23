from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field

from app.models.rol import ESTADO_BORRADOR


class AsignacionBorrador(BaseModel):
    """Un guía en una sala durante un bloque. `sala_id` nulo es "sin asignar"."""

    model_config = ConfigDict(from_attributes=True)

    guia_id: int
    bloque_id: int
    sala_id: int | None = None


class ParticipanteBorrador(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    guia_id: int
    hora_comida: time


class RolBorrador(BaseModel):
    """El rol tal como se edita en pantalla, todavía sin guardar.

    Va solo con ids: el frontend ya tiene los catálogos de salas, guías y
    bloques para resolver los nombres.
    """

    model_config = ConfigDict(from_attributes=True)

    fecha: date
    turno_id: int
    participantes: list[ParticipanteBorrador] = Field(default_factory=list)
    asignaciones: list[AsignacionBorrador] = Field(default_factory=list)
    notas: str | None = Field(default=None, max_length=500)


class RolGuardar(RolBorrador):
    estado: str = ESTADO_BORRADOR


class RolDetalle(RolBorrador):
    id: int
    estado: str
    created_at: datetime


class RolResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha: date
    turno_id: int
    estado: str
    created_at: datetime
    total_participantes: int
