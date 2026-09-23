"""Catálogo de prueba que reproduce el museo real, sin base de datos."""

from datetime import time

import pytest

from app.scheduling.dominio import (
    BloqueHorario,
    GuiaDisponible,
    ParDeComida,
    SalaDisponible,
)

TEMPRANA = time(13, 30)
TARDIA = time(14, 0)

H20, H21, H22, H23, H25, H26, H27 = 1, 2, 3, 4, 5, 6, 7


@pytest.fixture
def salas() -> list[SalaDisponible]:
    return [
        SalaDisponible(H20, "H-20", "Súper Guía", False, True, TEMPRANA, 0),
        SalaDisponible(H21, "H-21", "Planetario", True, False, TEMPRANA, 1),
        SalaDisponible(H22, "H-22", "Come bien, juega bien", False, False, TEMPRANA, 2),
        SalaDisponible(H23, "H-23", "Física y astronomía", False, False, TARDIA, 3),
        SalaDisponible(H25, "H-25", "Jardín de la ciencia", False, False, TEMPRANA, 4),
        SalaDisponible(H26, "H-26", "MI-YO", False, False, TARDIA, 5),
        SalaDisponible(H27, "H-27", "Plasma", True, False, TARDIA, 6),
    ]


@pytest.fixture
def bloques() -> list[BloqueHorario]:
    return [
        BloqueHorario(1, 0, "10:00 - 12:30", time(10, 0), time(12, 30)),
        BloqueHorario(2, 1, "12:30 - 3:00", time(12, 30), time(15, 0)),
        BloqueHorario(3, 2, "3:00 - 5:00", time(15, 0), time(17, 0)),
    ]


@pytest.fixture
def pares_comida() -> list[ParDeComida]:
    return [ParDeComida(H21, H27), ParDeComida(H22, H23), ParDeComida(H25, H26)]


def guia(
    id_: int, nombre: str, *, es_super: bool = False, certificadas: tuple[int, ...] = ()
) -> GuiaDisponible:
    return GuiaDisponible(id_, nombre, es_super, frozenset(certificadas))


@pytest.fixture
def plantilla_completa() -> list[GuiaDisponible]:
    """Siete guías: un súper, dos de planetario, dos de plasma y dos generales.

    Es el escenario normal de un sábado. Con solo dos certificados por sala de
    función y tres bloques, repetir H-21 y H-27 es inevitable.
    """
    return [
        guia(1, "Sofía", es_super=True),
        guia(2, "Bruno", certificadas=(H21,)),
        guia(3, "Carla", certificadas=(H21,)),
        guia(4, "Diego", certificadas=(H27,)),
        guia(5, "Elena", certificadas=(H27,)),
        guia(6, "Fer"),
        guia(7, "Gabi"),
    ]


@pytest.fixture
def plantilla_holgada() -> list[GuiaDisponible]:
    """Tres certificados por sala de función: alcanza para no repetir nada."""
    return [
        guia(1, "Sofía", es_super=True),
        guia(2, "Bruno", certificadas=(H21,)),
        guia(3, "Carla", certificadas=(H21,)),
        guia(8, "Hugo", certificadas=(H21,)),
        guia(4, "Diego", certificadas=(H27,)),
        guia(5, "Elena", certificadas=(H27,)),
        guia(9, "Ivón", certificadas=(H27,)),
    ]
