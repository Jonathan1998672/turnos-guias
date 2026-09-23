from enum import StrEnum

from pydantic import BaseModel, Field


class Nivel(StrEnum):
    ERROR = "error"
    AVISO = "aviso"


class Regla(StrEnum):
    """Identificador estable de cada regla, para que el frontend pueda agrupar."""

    SALA_REPETIDA = "sala_repetida"
    COMIDA_EMPALMADA = "comida_empalmada"
    SALA_VACIA = "sala_vacia"
    SALA_DUPLICADA = "sala_duplicada"
    GUIA_DUPLICADO = "guia_duplicado"
    SIN_CERTIFICACION = "sin_certificacion"
    SOLO_SUPER = "solo_super"
    SIN_ASIGNAR = "sin_asignar"
    HORA_COMIDA_INVALIDA = "hora_comida_invalida"


class Advertencia(BaseModel):
    nivel: Nivel
    regla: Regla
    mensaje: str
    guia_id: int | None = None
    bloque_id: int | None = None
    sala_id: int | None = None


class ResultadoValidacion(BaseModel):
    """`valido` es falso solo si hay advertencias de nivel error.

    Los avisos (salas vacías, repeticiones toleradas por falta de personal) no
    bloquean: el rol se puede guardar y exportar igual.
    """

    valido: bool
    advertencias: list[Advertencia] = Field(default_factory=list)

    @classmethod
    def desde(cls, advertencias: list[Advertencia]) -> "ResultadoValidacion":
        hay_errores = any(a.nivel is Nivel.ERROR for a in advertencias)
        return cls(valido=not hay_errores, advertencias=advertencias)
