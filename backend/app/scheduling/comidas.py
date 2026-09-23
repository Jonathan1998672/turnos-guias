"""Regla 3: solo existen dos horas de comida, de 30 minutos cada una."""

from collections.abc import Mapping, Sequence
from datetime import time

from app.scheduling.dominio import (
    BloqueHorario,
    GuiaDisponible,
    ParDeComida,
    SalaDisponible,
)

COMIDA_TEMPRANA = time(13, 30)
COMIDA_TARDIA = time(14, 0)
HORAS_COMIDA: tuple[time, time] = (COMIDA_TEMPRANA, COMIDA_TARDIA)
DURACION_MINUTOS = 30


def es_hora_valida(hora: time) -> bool:
    return hora in HORAS_COMIDA


def otra_hora(hora: time) -> time:
    return COMIDA_TARDIA if hora == COMIDA_TEMPRANA else COMIDA_TEMPRANA


def normalizar(hora: time | None) -> time:
    return hora if hora in HORAS_COMIDA else COMIDA_TEMPRANA


def bloque_de_comida(bloques: Sequence[BloqueHorario]) -> BloqueHorario | None:
    """El bloque donde cae la comida, normalmente el del mediodía."""
    for bloque in bloques:
        if all(bloque.contiene(hora) for hora in HORAS_COMIDA):
            return bloque

    for bloque in bloques:
        if any(bloque.contiene(hora) for hora in HORAS_COMIDA):
            return bloque

    return None


def asignar_comidas(
    guias: Sequence[GuiaDisponible],
    salas_por_id: Mapping[int, SalaDisponible],
    ocupantes_por_sala: Mapping[int, int],
    pares: Sequence[ParDeComida],
) -> dict[int, time]:
    """Reparte las horas de comida a partir del bloque del mediodía.

    Cada sala trae su hora sugerida y las salas emparejadas vienen con horas
    opuestas, así que casi siempre la regla 2 se cumple sola. El ajuste final
    cubre el caso de una pareja mal configurada.
    """
    sala_de_guia = {guia_id: sala_id for sala_id, guia_id in ocupantes_por_sala.items()}
    comidas: dict[int, time] = {}

    for guia in guias:
        sala = salas_por_id.get(sala_de_guia.get(guia.id, -1))
        comidas[guia.id] = sala.comida_default if sala else COMIDA_TEMPRANA

    for par in pares:
        guia_a = ocupantes_por_sala.get(par.sala_a_id)
        guia_b = ocupantes_por_sala.get(par.sala_b_id)

        if guia_a is None or guia_b is None:
            continue

        if comidas[guia_a] == comidas[guia_b]:
            comidas[guia_b] = otra_hora(comidas[guia_a])

    return comidas
