from datetime import time

from app.scheduling.comidas import (
    COMIDA_TARDIA,
    COMIDA_TEMPRANA,
    asignar_comidas,
    bloque_de_comida,
    es_hora_valida,
    normalizar,
    otra_hora,
)
from tests.conftest import H21, H22, H23, H27, guia


def test_solo_hay_dos_horas_validas():
    assert es_hora_valida(COMIDA_TEMPRANA)
    assert es_hora_valida(COMIDA_TARDIA)
    assert not es_hora_valida(time(15, 0))


def test_otra_hora_alterna_entre_las_dos():
    assert otra_hora(COMIDA_TEMPRANA) == COMIDA_TARDIA
    assert otra_hora(COMIDA_TARDIA) == COMIDA_TEMPRANA


def test_normalizar_cae_en_la_temprana_ante_cualquier_basura():
    assert normalizar(None) == COMIDA_TEMPRANA
    assert normalizar(time(9, 15)) == COMIDA_TEMPRANA
    assert normalizar(COMIDA_TARDIA) == COMIDA_TARDIA


def test_el_bloque_de_comida_es_el_del_mediodia(bloques):
    assert bloque_de_comida(bloques).etiqueta == "12:30 - 3:00"


def test_sin_bloque_que_contenga_la_comida_devuelve_nada(bloques):
    assert bloque_de_comida([bloques[0], bloques[2]]) is None


def test_cada_guia_hereda_la_hora_de_su_sala(salas, pares_comida):
    salas_por_id = {sala.id: sala for sala in salas}
    guias = [guia(2, "Bruno"), guia(4, "Diego")]
    ocupantes = {H21: 2, H27: 4}

    comidas = asignar_comidas(guias, salas_por_id, ocupantes, pares_comida)

    assert comidas[2] == COMIDA_TEMPRANA  # H-21
    assert comidas[4] == COMIDA_TARDIA  # H-27


def test_quien_no_tiene_sala_come_temprano(salas, pares_comida):
    salas_por_id = {sala.id: sala for sala in salas}
    guias = [guia(6, "Fer")]

    comidas = asignar_comidas(guias, salas_por_id, {}, pares_comida)

    assert comidas[6] == COMIDA_TEMPRANA


def test_una_pareja_mal_configurada_se_corrige_sola(salas, pares_comida):
    """Si H-22 y H-23 tuvieran la misma hora sugerida, se separa a una de las dos."""
    salas_por_id = {sala.id: sala for sala in salas}
    salas_por_id[H23] = salas_por_id[H23].__class__(
        H23, "H-23", "Física y astronomía", False, False, COMIDA_TEMPRANA, 3
    )

    guias = [guia(6, "Fer"), guia(7, "Gabi")]
    comidas = asignar_comidas(guias, salas_por_id, {H22: 6, H23: 7}, pares_comida)

    assert comidas[6] != comidas[7]
