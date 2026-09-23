"""Carga el catálogo base: salas, parejas de comida y el turno de fin de semana.

Es idempotente: se puede correr las veces que haga falta.

    python -m scripts.seed
"""

from datetime import time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models import Bloque, ParComida, Sala, Turno
from app.models.turno import CLAVE_FIN_DE_SEMANA

COMIDA_TEMPRANA = time(13, 30)
COMIDA_TARDIA = time(14, 0)

# codigo, nombre, es_funcion, solo_super, comida_default
SALAS: list[tuple[str, str, bool, bool, time]] = [
    ("H-20", "Súper Guía", False, True, COMIDA_TEMPRANA),
    ("H-21", "Planetario", True, False, COMIDA_TEMPRANA),
    ("H-22", "Come bien, juega bien", False, False, COMIDA_TEMPRANA),
    ("H-23", "Física y astronomía", False, False, COMIDA_TARDIA),
    ("H-25", "Jardín de la ciencia", False, False, COMIDA_TEMPRANA),
    ("H-26", "MI-YO", False, False, COMIDA_TARDIA),
    ("H-27", "Plasma", True, False, COMIDA_TARDIA),
]

PARES_COMIDA: list[tuple[str, str]] = [
    ("H-21", "H-27"),
    ("H-22", "H-23"),
    ("H-25", "H-26"),
]

# Solo se siembra el turno de fin de semana. Los de entre semana se agregarán
# cuando estén definidos sus horarios.
BLOQUES_FIN_DE_SEMANA: list[tuple[time, time, str]] = [
    (time(10, 0), time(12, 30), "10:00 - 12:30"),
    (time(12, 30), time(15, 0), "12:30 - 3:00"),
    (time(15, 0), time(17, 0), "3:00 - 5:00"),
]


def _sembrar_salas(db: Session) -> dict[str, Sala]:
    existentes = {s.codigo: s for s in db.scalars(select(Sala))}

    for orden, (codigo, nombre, es_funcion, solo_super, comida) in enumerate(SALAS):
        sala = existentes.get(codigo)
        if sala is None:
            sala = Sala(codigo=codigo)
            db.add(sala)
            existentes[codigo] = sala

        sala.nombre = nombre
        sala.es_funcion = es_funcion
        sala.solo_super = solo_super
        sala.comida_default = comida
        sala.orden = orden
        sala.activa = True

    db.flush()
    return existentes


def _sembrar_pares(db: Session, salas: dict[str, Sala]) -> None:
    ya_registrados = {
        tuple(sorted((par.sala_a_id, par.sala_b_id))) for par in db.scalars(select(ParComida))
    }

    for codigo_a, codigo_b in PARES_COMIDA:
        ids = sorted((salas[codigo_a].id, salas[codigo_b].id))
        if tuple(ids) in ya_registrados:
            continue
        db.add(ParComida(sala_a_id=ids[0], sala_b_id=ids[1]))

    db.flush()


def _sembrar_turno_fin_de_semana(db: Session) -> None:
    turno = db.scalar(select(Turno).where(Turno.clave == CLAVE_FIN_DE_SEMANA))
    if turno is None:
        turno = Turno(clave=CLAVE_FIN_DE_SEMANA, nombre="Fin de semana")
        db.add(turno)
        db.flush()

    bloques_por_orden = {b.orden: b for b in turno.bloques}

    for orden, (inicio, fin, etiqueta) in enumerate(BLOQUES_FIN_DE_SEMANA):
        bloque = bloques_por_orden.get(orden)
        if bloque is None:
            bloque = Bloque(turno_id=turno.id, orden=orden)
            db.add(bloque)

        bloque.hora_inicio = inicio
        bloque.hora_fin = fin
        bloque.etiqueta = etiqueta

    db.flush()


def sembrar(db: Session) -> None:
    salas = _sembrar_salas(db)
    _sembrar_pares(db, salas)
    _sembrar_turno_fin_de_semana(db)
    db.commit()


def main() -> None:
    with SessionLocal() as db:
        sembrar(db)
    print(f"Catálogo base listo: {len(SALAS)} salas, {len(PARES_COMIDA)} parejas de comida.")


if __name__ == "__main__":
    main()
