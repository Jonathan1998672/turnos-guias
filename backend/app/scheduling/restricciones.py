"""Una función por regla, para poder probarlas por separado."""

from collections.abc import Collection, Mapping, Sequence

from app.scheduling.dominio import BloqueHorario, GuiaDisponible, SalaDisponible


def salas_permitidas_al_super(
    guias: Sequence[GuiaDisponible],
    salas: Sequence[SalaDisponible],
    bloques: Sequence[BloqueHorario],
) -> set[int]:
    """Dónde puede pararse el Súper Guía.

    Con personal suficiente se queda en su sala exclusiva, igual que en el
    prototipo. Se le abre una sala de función solo si no hay certificados de
    sobra para cubrirla en todos los bloques, y se le abre todo cuando falta
    gente.
    """
    super_guia = next((g for g in guias if g.es_super), None)
    if super_guia is None:
        return set()

    exclusivas = {sala.id for sala in salas if sala.solo_super}
    cubribles = {sala.id for sala in salas if super_guia.cumple_requisito(sala)}

    # Sin sala exclusiva el Súper Guía es un guía más.
    if not exclusivas:
        return cubribles

    # Con menos guías que salas hace falta que ayude donde pueda.
    if len(guias) < len(salas):
        return cubribles

    permitidas = set(exclusivas)

    for sala in salas:
        if not sala.es_funcion or sala.id not in super_guia.salas_certificadas:
            continue

        otros_certificados = sum(
            1 for g in guias if not g.es_super and sala.id in g.salas_certificadas
        )
        if otros_certificados < len(bloques):
            permitidas.add(sala.id)

    return permitidas


def puede_ocupar(
    guia: GuiaDisponible,
    sala: SalaDisponible,
    *,
    permitidas_al_super: Collection[int],
) -> bool:
    """Requisito de la sala más la reserva del Súper Guía."""
    if sala.solo_super:
        return guia.es_super

    if guia.es_super and sala.id not in permitidas_al_super:
        return False

    return guia.cumple_requisito(sala)


def salas_con_repeticion_inevitable(
    guias: Sequence[GuiaDisponible],
    salas: Sequence[SalaDisponible],
    bloques: Sequence[BloqueHorario],
    permitidas_al_super: Collection[int],
) -> set[int]:
    """Salas con menos guías capaces que bloques por cubrir.

    Con dos guías de Planetario y tres bloques, alguien tiene que repetir. No
    tiene caso que el solver se pelee con la regla 1 en esos casos: se permite
    la repetición desde el modo estricto y la validación la reporta como aviso.
    """
    inevitables: set[int] = set()

    for sala in salas:
        capaces = sum(
            1 for guia in guias if puede_ocupar(guia, sala, permitidas_al_super=permitidas_al_super)
        )
        if 0 < capaces < len(bloques):
            inevitables.add(sala.id)

    return inevitables


def respeta_sin_repetir(
    guia: GuiaDisponible,
    sala: SalaDisponible,
    historial: Mapping[int, Collection[int]],
    *,
    estricto: bool,
    repeticion_inevitable: Collection[int] = (),
) -> bool:
    """Regla 1. El Súper Guía sí repite su sala exclusiva en todos los bloques."""
    if sala.id not in historial.get(guia.id, ()):
        return True

    if sala.solo_super and guia.es_super:
        return True

    if sala.id in repeticion_inevitable:
        return True

    return not estricto


def comidas_empalmadas(
    comidas_por_guia: Mapping[int, object],
    ocupantes_por_sala: Mapping[int, int],
    pares: Sequence[tuple[int, int]],
) -> list[tuple[int, int]]:
    """Regla 2. Devuelve las parejas de guías que coinciden en hora de comida."""
    choques: list[tuple[int, int]] = []

    for sala_a, sala_b in pares:
        guia_a = ocupantes_por_sala.get(sala_a)
        guia_b = ocupantes_por_sala.get(sala_b)

        if guia_a is None or guia_b is None:
            continue

        if comidas_por_guia.get(guia_a) == comidas_por_guia.get(guia_b):
            choques.append((guia_a, guia_b))

    return choques
