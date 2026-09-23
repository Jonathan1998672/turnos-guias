"""Reparte guías entre salas y bloques respetando las cuatro reglas.

Heredado del prototipo, pero corregido para el caso de falta de personal: en
vez de exigir que todas las salas queden llenas, cada bloque se resuelve como
un emparejamiento máximo entre guías y salas. Así el rol siempre sale, y las
salas que quedaron vacías se reportan como advertencia.

Se prueban varios repartos con el orden barajado y se conserva el mejor. Si en
modo estricto (regla 1 sin excepciones) no se llena todo lo posible, se
reintenta permitiendo repetir sala y se marca `uso_modo_relajado`.
"""

import random
from collections.abc import Sequence
from datetime import time

from app.core.exceptions import RolNoFactible
from app.scheduling.comidas import asignar_comidas, bloque_de_comida
from app.scheduling.dominio import (
    BloqueHorario,
    EntradaSolver,
    ResultadoSolver,
    SalaDisponible,
    SlotAsignado,
)
from app.scheduling.restricciones import (
    puede_ocupar,
    respeta_sin_repetir,
    salas_con_repeticion_inevitable,
    salas_permitidas_al_super,
)

# sala_id -> guia_id dentro de un bloque
RepartoBloque = dict[int, int]
Plan = list[RepartoBloque]
Elegibles = dict[int, list[int]]


def resolver(entrada: EntradaSolver) -> ResultadoSolver:
    if not entrada.guias:
        raise RolNoFactible("No hay guías presentes para armar el rol.")
    if not entrada.salas:
        raise RolNoFactible("No hay salas activas.")
    if not entrada.bloques:
        raise RolNoFactible("El turno no tiene bloques configurados.")

    rng = random.Random(entrada.semilla)
    permitidas_super = salas_permitidas_al_super(entrada.guias, entrada.salas, entrada.bloques)
    inevitables = salas_con_repeticion_inevitable(
        entrada.guias, entrada.salas, entrada.bloques, permitidas_super
    )
    tope = _tope_alcanzable(entrada, permitidas_super)

    if tope == 0:
        raise RolNoFactible(
            "Ningún guía presente puede cubrir alguna de las salas.",
            detalles=["Revisa las certificaciones de los guías y el catálogo de salas."],
        )

    mejor_plan, mejor_puntaje = _mejor_de_varios(
        entrada, rng, permitidas_super, inevitables, tope, estricto=True
    )
    relajado = False

    if mejor_puntaje < tope:
        plan_relajado, puntaje_relajado = _mejor_de_varios(
            entrada, rng, permitidas_super, inevitables, tope, estricto=False
        )
        if puntaje_relajado > mejor_puntaje:
            mejor_plan, mejor_puntaje, relajado = plan_relajado, puntaje_relajado, True

    return _construir_resultado(entrada, mejor_plan, mejor_puntaje, tope, relajado)


def _mejor_de_varios(
    entrada: EntradaSolver,
    rng: random.Random,
    permitidas_super: set[int],
    inevitables: set[int],
    tope: int,
    *,
    estricto: bool,
) -> tuple[Plan, int]:
    mejor_plan: Plan = []
    mejor_puntaje = -1

    for _ in range(max(1, entrada.intentos)):
        plan = _intentar(entrada, rng, permitidas_super, inevitables, estricto=estricto)
        puntaje = sum(len(reparto) for reparto in plan)

        if puntaje > mejor_puntaje:
            mejor_plan, mejor_puntaje = plan, puntaje

        if mejor_puntaje >= tope:
            break

    return mejor_plan, mejor_puntaje


def _intentar(
    entrada: EntradaSolver,
    rng: random.Random,
    permitidas_super: set[int],
    inevitables: set[int],
    *,
    estricto: bool,
) -> Plan:
    historial: dict[int, set[int]] = {guia.id: set() for guia in entrada.guias}
    plan: Plan = []

    for _ in entrada.bloques:
        salas = _orden_de_salas(entrada.salas, rng)
        elegibles = {
            sala.id: [
                guia.id
                for guia in entrada.guias
                if puede_ocupar(guia, sala, permitidas_al_super=permitidas_super)
                and respeta_sin_repetir(
                    guia,
                    sala,
                    historial,
                    estricto=estricto,
                    repeticion_inevitable=inevitables,
                )
            ]
            for sala in salas
        }

        for candidatos in elegibles.values():
            rng.shuffle(candidatos)

        reparto = _emparejamiento_maximo(salas, elegibles)

        for sala_id, guia_id in reparto.items():
            historial[guia_id].add(sala_id)

        plan.append(reparto)

    return plan


def _orden_de_salas(salas: Sequence[SalaDisponible], rng: random.Random) -> list[SalaDisponible]:
    """Primero las salas difíciles: exclusivas, luego funciones, luego generales."""
    exclusivas = [s for s in salas if s.solo_super]
    funciones = [s for s in salas if s.es_funcion and not s.solo_super]
    generales = [s for s in salas if not s.es_funcion and not s.solo_super]

    rng.shuffle(funciones)
    rng.shuffle(generales)

    return [*exclusivas, *funciones, *generales]


def _emparejamiento_maximo(salas: Sequence[SalaDisponible], elegibles: Elegibles) -> RepartoBloque:
    """Algoritmo de Kuhn: llena la mayor cantidad de salas posible.

    Cada sala admite un guía y cada guía una sala. Cuando una sala no encuentra
    hueco libre intenta desplazar a un guía ya colocado hacia otra sala suya,
    que es lo que garantiza que el resultado sea el máximo y no solo el primero
    que salga.
    """
    sala_de_guia: dict[int, int] = {}

    def acomodar(sala_id: int, visitados: set[int]) -> bool:
        for guia_id in elegibles[sala_id]:
            if guia_id in visitados:
                continue
            visitados.add(guia_id)

            ocupada = sala_de_guia.get(guia_id)
            if ocupada is None or acomodar(ocupada, visitados):
                sala_de_guia[guia_id] = sala_id
                return True

        return False

    for sala in salas:
        acomodar(sala.id, set())

    return {sala_id: guia_id for guia_id, sala_id in sala_de_guia.items()}


def _tope_alcanzable(entrada: EntradaSolver, permitidas_super: set[int]) -> int:
    """Cota superior: el mejor bloque posible ignorando la regla 1, por bloque."""
    elegibles = {
        sala.id: [
            guia.id
            for guia in entrada.guias
            if puede_ocupar(guia, sala, permitidas_al_super=permitidas_super)
        ]
        for sala in entrada.salas
    }

    return len(_emparejamiento_maximo(entrada.salas, elegibles)) * len(entrada.bloques)


def _construir_resultado(
    entrada: EntradaSolver,
    plan: Plan,
    puntaje: int,
    tope: int,
    relajado: bool,
) -> ResultadoSolver:
    asignaciones: list[SlotAsignado] = []

    for bloque, reparto in zip(entrada.bloques, plan, strict=True):
        sala_de_guia = {guia_id: sala_id for sala_id, guia_id in reparto.items()}
        for guia in entrada.guias:
            asignaciones.append(
                SlotAsignado(
                    guia_id=guia.id,
                    bloque_id=bloque.id,
                    sala_id=sala_de_guia.get(guia.id),
                )
            )

    return ResultadoSolver(
        asignaciones=asignaciones,
        comidas=_calcular_comidas(entrada, plan),
        uso_modo_relajado=relajado,
        salas_cubiertas=puntaje,
        salas_posibles=tope,
    )


def _calcular_comidas(entrada: EntradaSolver, plan: Plan) -> dict[int, time]:
    salas_por_id = {sala.id: sala for sala in entrada.salas}
    bloque_comida = bloque_de_comida(entrada.bloques)
    reparto_comida = _reparto_del_bloque(entrada.bloques, plan, bloque_comida)

    return asignar_comidas(entrada.guias, salas_por_id, reparto_comida, entrada.pares_comida)


def _reparto_del_bloque(
    bloques: Sequence[BloqueHorario], plan: Plan, bloque: BloqueHorario | None
) -> RepartoBloque:
    if bloque is None:
        return {}

    for indice, candidato in enumerate(bloques):
        if candidato.id == bloque.id and indice < len(plan):
            return plan[indice]

    return {}
