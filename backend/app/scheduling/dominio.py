from dataclasses import dataclass, field
from datetime import time


@dataclass(frozen=True, slots=True)
class SalaDisponible:
    id: int
    codigo: str
    nombre: str
    es_funcion: bool
    solo_super: bool
    comida_default: time
    orden: int = 0

    @property
    def etiqueta(self) -> str:
        return f"{self.codigo} · {self.nombre}"


@dataclass(frozen=True, slots=True)
class GuiaDisponible:
    id: int
    nombre: str
    es_super: bool
    salas_certificadas: frozenset[int] = frozenset()

    def cumple_requisito(self, sala: SalaDisponible) -> bool:
        """Solo mira el requisito de la sala, no el resto de las reglas."""
        if sala.solo_super:
            return self.es_super
        if sala.es_funcion:
            return sala.id in self.salas_certificadas
        return True


@dataclass(frozen=True, slots=True)
class BloqueHorario:
    id: int
    orden: int
    etiqueta: str
    hora_inicio: time
    hora_fin: time

    def contiene(self, momento: time) -> bool:
        return self.hora_inicio <= momento < self.hora_fin


@dataclass(frozen=True, slots=True)
class ParDeComida:
    sala_a_id: int
    sala_b_id: int


@dataclass(frozen=True, slots=True)
class SlotAsignado:
    """Un guía en un bloque. `sala_id` nulo significa que quedó sin sala."""

    guia_id: int
    bloque_id: int
    sala_id: int | None


@dataclass(slots=True)
class EntradaSolver:
    guias: list[GuiaDisponible]
    salas: list[SalaDisponible]
    bloques: list[BloqueHorario]
    pares_comida: list[ParDeComida] = field(default_factory=list)
    intentos: int = 60
    semilla: int | None = None


@dataclass(slots=True)
class ResultadoSolver:
    asignaciones: list[SlotAsignado]
    comidas: dict[int, time]
    uso_modo_relajado: bool
    salas_cubiertas: int
    salas_posibles: int
