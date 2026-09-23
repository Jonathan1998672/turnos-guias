"""Las cuatro reglas, probadas contra el solver."""

from collections import Counter, defaultdict

import pytest

from app.core.exceptions import RolNoFactible
from app.scheduling.comidas import HORAS_COMIDA
from app.scheduling.dominio import EntradaSolver
from app.scheduling.solver import resolver
from tests.conftest import H20, H21, H22, H23, H25, H26, H27, guia


def entrada(guias, salas, bloques, pares_comida, **extra):
    return EntradaSolver(
        guias=guias, salas=salas, bloques=bloques, pares_comida=pares_comida, **extra
    )


def ocupadas_por_bloque(resultado):
    mapa = defaultdict(dict)
    for slot in resultado.asignaciones:
        if slot.sala_id is not None:
            mapa[slot.bloque_id][slot.sala_id] = slot.guia_id
    return mapa


# --- Regla 1: un guía no repite sala en el turno ---------------------------


def test_con_plantilla_holgada_nadie_repite_sala(plantilla_holgada, salas, bloques, pares_comida):
    resultado = resolver(entrada(plantilla_holgada, salas, bloques, pares_comida, semilla=7))

    repeticiones = Counter(
        (slot.guia_id, slot.sala_id) for slot in resultado.asignaciones if slot.sala_id
    )

    for (guia_id, sala_id), veces in repeticiones.items():
        es_super_en_su_sala = guia_id == 1 and sala_id == H20
        assert veces == 1 or es_super_en_su_sala


def test_las_salas_generales_nunca_se_repiten(plantilla_completa, salas, bloques, pares_comida):
    """Con dos certificados por función, repetir H-21 y H-27 es inevitable.

    Las salas generales, en cambio, tienen gente de sobra y no deben repetirse.
    """
    resultado = resolver(entrada(plantilla_completa, salas, bloques, pares_comida, semilla=7))
    generales = {H22, H23, H25, H26}

    repeticiones = Counter(
        (slot.guia_id, slot.sala_id) for slot in resultado.asignaciones if slot.sala_id in generales
    )

    assert all(veces == 1 for veces in repeticiones.values())


def test_el_super_guia_se_queda_en_h20(plantilla_completa, salas, bloques, pares_comida):
    resultado = resolver(entrada(plantilla_completa, salas, bloques, pares_comida, semilla=3))

    salas_del_super = [s.sala_id for s in resultado.asignaciones if s.guia_id == 1]
    assert salas_del_super == [H20, H20, H20]


# --- Regla 2: las salas emparejadas no empalman comida ---------------------


def test_las_parejas_no_comen_a_la_misma_hora(plantilla_completa, salas, bloques, pares_comida):
    resultado = resolver(entrada(plantilla_completa, salas, bloques, pares_comida, semilla=11))
    ocupadas = ocupadas_por_bloque(resultado)[2]  # bloque del mediodía

    for par in pares_comida:
        guia_a = ocupadas.get(par.sala_a_id)
        guia_b = ocupadas.get(par.sala_b_id)
        if guia_a is None or guia_b is None:
            continue
        assert resultado.comidas[guia_a] != resultado.comidas[guia_b]


# --- Regla 3: solo hay dos horas de comida ---------------------------------


def test_solo_se_usan_las_dos_horas_permitidas(plantilla_completa, salas, bloques, pares_comida):
    resultado = resolver(entrada(plantilla_completa, salas, bloques, pares_comida, semilla=5))

    assert set(resultado.comidas) == {g.id for g in plantilla_completa}
    assert all(hora in HORAS_COMIDA for hora in resultado.comidas.values())


# --- Regla 4: no siempre asisten todos -------------------------------------


def test_con_menos_guias_que_salas_el_rol_igual_sale(salas, bloques, pares_comida):
    presentes = [
        guia(1, "Sofía", es_super=True),
        guia(2, "Bruno", certificadas=(H21,)),
        guia(4, "Diego", certificadas=(H27,)),
        guia(6, "Fer"),
    ]

    resultado = resolver(entrada(presentes, salas, bloques, pares_comida, semilla=2))
    ocupadas = ocupadas_por_bloque(resultado)

    # Cuatro guías, tres bloques: cada bloque acomoda a los cuatro.
    for bloque_id in (1, 2, 3):
        assert len(ocupadas[bloque_id]) == 4
        assert len(set(ocupadas[bloque_id].values())) == 4


def test_sin_certificados_las_salas_de_funcion_quedan_vacias(salas, bloques, pares_comida):
    presentes = [guia(1, "Sofía", es_super=True), guia(6, "Fer"), guia(7, "Gabi")]

    resultado = resolver(entrada(presentes, salas, bloques, pares_comida, semilla=1))
    ocupadas = ocupadas_por_bloque(resultado)

    for bloque_id in (1, 2, 3):
        assert H21 not in ocupadas[bloque_id]
        assert H27 not in ocupadas[bloque_id]


def test_un_solo_certificado_cubre_su_sala_los_tres_bloques(salas, bloques, pares_comida):
    """Con un único guía de planetario, repetir es la única salida posible."""
    presentes = [
        guia(1, "Sofía", es_super=True),
        guia(2, "Bruno", certificadas=(H21,)),
        guia(4, "Diego", certificadas=(H27,)),
        guia(6, "Fer"),
        guia(7, "Gabi"),
        guia(8, "Hugo"),
        guia(9, "Ivón"),
    ]

    resultado = resolver(entrada(presentes, salas, bloques, pares_comida, semilla=4))
    ocupadas = ocupadas_por_bloque(resultado)

    for bloque_id in (1, 2, 3):
        assert ocupadas[bloque_id][H21] == 2
        assert ocupadas[bloque_id][H27] == 4


# --- Reglas estructurales --------------------------------------------------


def test_nadie_ajeno_entra_a_h20(plantilla_completa, salas, bloques, pares_comida):
    resultado = resolver(entrada(plantilla_completa, salas, bloques, pares_comida, semilla=9))

    for slot in resultado.asignaciones:
        if slot.sala_id == H20:
            assert slot.guia_id == 1


def test_solo_los_certificados_dan_funciones(plantilla_completa, salas, bloques, pares_comida):
    resultado = resolver(entrada(plantilla_completa, salas, bloques, pares_comida, semilla=13))
    por_id = {g.id: g for g in plantilla_completa}

    for slot in resultado.asignaciones:
        if slot.sala_id in (H21, H27):
            assert slot.sala_id in por_id[slot.guia_id].salas_certificadas


def test_sin_guias_presentes_falla(salas, bloques, pares_comida):
    with pytest.raises(RolNoFactible):
        resolver(entrada([], salas, bloques, pares_comida))


def test_cada_guia_aparece_en_todos_los_bloques(plantilla_completa, salas, bloques, pares_comida):
    """El borrador trae una celda por guía y bloque, aunque venga vacía."""
    resultado = resolver(entrada(plantilla_completa, salas, bloques, pares_comida, semilla=6))

    assert len(resultado.asignaciones) == len(plantilla_completa) * len(bloques)


def test_un_guia_no_esta_en_dos_salas_a_la_vez(plantilla_completa, salas, bloques, pares_comida):
    resultado = resolver(entrada(plantilla_completa, salas, bloques, pares_comida, semilla=8))

    for _, ocupadas in ocupadas_por_bloque(resultado).items():
        guias_ids = list(ocupadas.values())
        assert len(guias_ids) == len(set(guias_ids))


def test_la_generacion_es_reproducible_con_la_misma_semilla(
    plantilla_completa, salas, bloques, pares_comida
):
    primera = resolver(entrada(plantilla_completa, salas, bloques, pares_comida, semilla=42))
    segunda = resolver(entrada(plantilla_completa, salas, bloques, pares_comida, semilla=42))

    assert primera.asignaciones == segunda.asignaciones
    assert primera.comidas == segunda.comidas


@pytest.mark.parametrize("semilla", range(15))
def test_la_plantilla_completa_siempre_llena_las_siete_salas(
    plantilla_completa, salas, bloques, pares_comida, semilla
):
    resultado = resolver(entrada(plantilla_completa, salas, bloques, pares_comida, semilla=semilla))

    assert resultado.salas_cubiertas == len(salas) * len(bloques)
    assert resultado.uso_modo_relajado is False
