from datetime import date

from pydantic import BaseModel, Field

from app.schemas.rol import RolBorrador
from app.schemas.validacion import ResultadoValidacion


class GenerarRolRequest(BaseModel):
    fecha: date
    turno_id: int | None = Field(
        default=None, description="Si se omite se usa el turno de fin de semana."
    )
    guias_presentes: list[int] = Field(
        min_length=1, description="Ids de los guías que sí asistieron (regla 4)."
    )
    intentos: int = Field(
        default=60,
        ge=1,
        le=500,
        description="Cuántas veces reintentar el solver antes de relajar la regla 1.",
    )


class GenerarRolResponse(BaseModel):
    borrador: RolBorrador
    validacion: ResultadoValidacion


class ValidarRolRequest(BaseModel):
    borrador: RolBorrador
