"""Modelos de SQLAlchemy.

Se importan todos aquí para que `Base.metadata` esté completo cuando Alembic
autogenere una migración.
"""

from app.models.base import Base, TimestampMixin
from app.models.guia import Guia, GuiaCertificacion
from app.models.rol import (
    ESTADO_BORRADOR,
    ESTADO_PUBLICADO,
    ESTADOS,
    Asignacion,
    Rol,
    RolParticipante,
)
from app.models.sala import ParComida, Sala
from app.models.turno import (
    CLAVE_FIN_DE_SEMANA,
    CLAVE_MATUTINO,
    CLAVE_VESPERTINO,
    Bloque,
    Turno,
)

__all__ = [
    "CLAVE_FIN_DE_SEMANA",
    "CLAVE_MATUTINO",
    "CLAVE_VESPERTINO",
    "ESTADOS",
    "ESTADO_BORRADOR",
    "ESTADO_PUBLICADO",
    "Asignacion",
    "Base",
    "Bloque",
    "Guia",
    "GuiaCertificacion",
    "ParComida",
    "Rol",
    "RolParticipante",
    "Sala",
    "TimestampMixin",
    "Turno",
]
