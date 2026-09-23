"""Estructura plana del rol, lista para volcarse a cualquier formato.

Los exportadores no conocen el ORM ni los esquemas de la API: reciben este
`RolExportable` y devuelven bytes.
"""

from dataclasses import dataclass, field
from datetime import date, time
from typing import Protocol


@dataclass(frozen=True, slots=True)
class FilaExportable:
    guia: str
    es_super: bool
    salas: list[str]
    hora_comida: str


@dataclass(frozen=True, slots=True)
class RolExportable:
    fecha: date
    turno: str
    encabezados_bloques: list[str]
    filas: list[FilaExportable] = field(default_factory=list)
    notas: str | None = None

    @property
    def titulo(self) -> str:
        return f"Rol de guías · {self.fecha:%d/%m/%Y}"

    @property
    def encabezados(self) -> list[str]:
        return ["Guía", *self.encabezados_bloques, "Hora de comida"]

    def como_tabla(self) -> list[list[str]]:
        """Encabezados más una lista por fila, que es lo que quieren csv y pdf."""
        return [
            self.encabezados,
            *[
                [
                    f"{fila.guia} (Súper Guía)" if fila.es_super else fila.guia,
                    *fila.salas,
                    fila.hora_comida,
                ]
                for fila in self.filas
            ],
        ]

    def nombre_archivo(self, extension: str) -> str:
        return f"rol_{self.fecha:%Y-%m-%d}.{extension}"


class Exportador(Protocol):
    extension: str
    media_type: str

    def exportar(self, rol: RolExportable) -> bytes: ...


def formatear_hora(hora: time) -> str:
    """13:30 -> "1:30 PM", igual que se lee en la tabla."""
    sufijo = "PM" if hora.hour >= 12 else "AM"
    doce = hora.hour % 12 or 12
    return f"{doce}:{hora.minute:02d} {sufijo}"
