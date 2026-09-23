from datetime import time

import pytest

from app.scheduling.comidas import COMIDA_TARDIA, COMIDA_TEMPRANA
from app.scheduling.dominio import EntradaSolver, SlotAsignado
from app.scheduling.solver import resolver
from app.schemas.validacion import Nivel, Regla
from app.services.validacion_service import ValidacionService
from tests.conftest import H20, H21, H22, H25, H26, H27


@pytest.fixture
def validador(plantilla_completa, salas, bloques, pares_comida):
    return ValidacionService(plantilla_completa, salas, bloques, pares_comida)


def reglas(resultado) -> set[Regla]:
    return {advertencia.regla for advertencia in resultado.advertencias}


def errores(resultado) -> list:
    return [a for a in resultado.advertencias if a.nivel is Nivel.ERROR]


def test_un_rol_generado_no_tiene_errores(
    plantilla_completa, salas, bloques, pares_comida, validador
):
    generado = resolver(
        EntradaSolver(
            guias=plantilla_completa,
            salas=salas,
            bloques=bloques,
            pares_comida=pares_comida,
            semilla=21,
        )
    )

    resultado = validador.validar(generado.asignaciones, generado.comidas)

    assert errores(resultado) == []
    assert resultado.valido is True


def test_detecta_a_un_no_super_en_la_sala_exclusiva(validador):
    asignaciones = [SlotAsignado(guia_id=6, bloque_id=1, sala_id=H20)]

    resultado = validador.validar(asignaciones, {6: COMIDA_TEMPRANA})

    assert Regla.SOLO_SUPER in reglas(resultado)
    assert resultado.valido is False


def test_detecta_una_funcion_sin_certificacion(validador):
    asignaciones = [SlotAsignado(guia_id=6, bloque_id=1, sala_id=H21)]

    resultado = validador.validar(asignaciones, {6: COMIDA_TEMPRANA})

    assert Regla.SIN_CERTIFICACION in reglas(resultado)
    assert resultado.valido is False


def test_detecta_dos_guias_en_la_misma_sala(validador):
    asignaciones = [
        SlotAsignado(guia_id=6, bloque_id=1, sala_id=H22),
        SlotAsignado(guia_id=7, bloque_id=1, sala_id=H22),
    ]

    resultado = validador.validar(asignaciones, {6: COMIDA_TEMPRANA, 7: COMIDA_TARDIA})

    assert Regla.SALA_DUPLICADA in reglas(resultado)


def test_detecta_a_un_guia_en_dos_salas_a_la_vez(validador):
    asignaciones = [
        SlotAsignado(guia_id=6, bloque_id=1, sala_id=H22),
        SlotAsignado(guia_id=6, bloque_id=1, sala_id=H25),
    ]

    resultado = validador.validar(asignaciones, {6: COMIDA_TEMPRANA})

    assert Regla.GUIA_DUPLICADO in reglas(resultado)


def test_la_repeticion_de_sala_es_aviso_no_error(validador):
    asignaciones = [
        SlotAsignado(guia_id=6, bloque_id=1, sala_id=H22),
        SlotAsignado(guia_id=6, bloque_id=2, sala_id=H22),
    ]

    resultado = validador.validar(asignaciones, {6: COMIDA_TEMPRANA})
    repeticiones = [a for a in resultado.advertencias if a.regla is Regla.SALA_REPETIDA]

    assert len(repeticiones) == 1
    assert repeticiones[0].nivel is Nivel.AVISO


def test_el_super_en_su_sala_los_tres_bloques_no_cuenta_como_repeticion(validador):
    asignaciones = [SlotAsignado(guia_id=1, bloque_id=b, sala_id=H20) for b in (1, 2, 3)]

    resultado = validador.validar(asignaciones, {1: COMIDA_TEMPRANA})

    assert Regla.SALA_REPETIDA not in reglas(resultado)


def test_detecta_el_empalme_de_comida_entre_salas_vecinas(validador):
    asignaciones = [
        SlotAsignado(guia_id=6, bloque_id=2, sala_id=H25),
        SlotAsignado(guia_id=7, bloque_id=2, sala_id=H26),
    ]

    resultado = validador.validar(asignaciones, {6: COMIDA_TEMPRANA, 7: COMIDA_TEMPRANA})
    choques = [a for a in resultado.advertencias if a.regla is Regla.COMIDA_EMPALMADA]

    assert len(choques) == 1
    assert choques[0].nivel is Nivel.ERROR


def test_horas_distintas_en_salas_vecinas_no_generan_choque(validador):
    asignaciones = [
        SlotAsignado(guia_id=6, bloque_id=2, sala_id=H25),
        SlotAsignado(guia_id=7, bloque_id=2, sala_id=H26),
    ]

    resultado = validador.validar(asignaciones, {6: COMIDA_TEMPRANA, 7: COMIDA_TARDIA})

    assert Regla.COMIDA_EMPALMADA not in reglas(resultado)


def test_el_empalme_solo_importa_en_el_bloque_de_la_comida(validador):
    asignaciones = [
        SlotAsignado(guia_id=6, bloque_id=1, sala_id=H25),
        SlotAsignado(guia_id=7, bloque_id=1, sala_id=H26),
    ]

    resultado = validador.validar(asignaciones, {6: COMIDA_TEMPRANA, 7: COMIDA_TEMPRANA})

    assert Regla.COMIDA_EMPALMADA not in reglas(resultado)


def test_rechaza_una_hora_de_comida_inventada(validador):
    resultado = validador.validar([], {6: time(16, 0)})

    assert Regla.HORA_COMIDA_INVALIDA in reglas(resultado)
    assert resultado.valido is False


def test_reporta_las_salas_que_quedaron_vacias(validador, salas, bloques):
    resultado = validador.validar([], {})
    vacias = [a for a in resultado.advertencias if a.regla is Regla.SALA_VACIA]

    assert len(vacias) == len(salas) * len(bloques)


def test_una_funcion_vacia_es_error_y_una_general_es_aviso(validador):
    resultado = validador.validar([], {})
    por_sala = {a.sala_id: a.nivel for a in resultado.advertencias if a.regla is Regla.SALA_VACIA}

    assert por_sala[H21] is Nivel.ERROR  # Planetario sin guía cancela la función
    assert por_sala[H27] is Nivel.ERROR
    assert por_sala[H20] is Nivel.ERROR
    assert por_sala[H22] is Nivel.AVISO
    assert por_sala[H25] is Nivel.AVISO


def test_reporta_a_los_guias_sin_sala(validador):
    asignaciones = [SlotAsignado(guia_id=6, bloque_id=1, sala_id=None)]

    resultado = validador.validar(asignaciones, {6: COMIDA_TEMPRANA})
    sin_asignar = [a for a in resultado.advertencias if a.regla is Regla.SIN_ASIGNAR]

    assert len(sin_asignar) == 1
    assert sin_asignar[0].nivel is Nivel.AVISO  # no bloquea por sí solo
