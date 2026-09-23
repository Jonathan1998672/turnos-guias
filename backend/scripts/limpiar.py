"""Borra el catálogo de guías y todo lo que cuelga de él.

Por defecto solo muestra lo que borraría. Para ejecutarlo de verdad:

    python -m scripts.limpiar --si

Ojo: las asignaciones y los participantes de los roles guardados apuntan a
`guias.id` con ON DELETE CASCADE, así que borrar guías borra también su
historial. Con --con-roles se eliminan además los roles que quedan vacíos.
"""

import argparse

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models import Asignacion, Guia, GuiaCertificacion, Rol, RolParticipante

# El orden importa: primero lo que apunta a guias, al final guias. Así funciona
# igual en PostgreSQL y en SQLite, que ignora ON DELETE CASCADE salvo que se
# active el PRAGMA foreign_keys.
DEPENDIENTES = (Asignacion, RolParticipante, GuiaCertificacion)


def _contar(db: Session, modelo: type) -> int:
    return db.scalar(select(func.count()).select_from(modelo)) or 0


def limpiar(db: Session, *, con_roles: bool = False) -> dict[str, int]:
    borrados: dict[str, int] = {}

    for modelo in (*DEPENDIENTES, Guia):
        resultado = db.execute(delete(modelo))
        borrados[modelo.__tablename__] = resultado.rowcount

    if con_roles:
        # Sin participantes ni asignaciones, el encabezado del rol ya no dice nada.
        borrados[Rol.__tablename__] = db.execute(delete(Rol)).rowcount

    db.commit()
    return borrados


def main() -> None:
    parser = argparse.ArgumentParser(description="Vacía el catálogo de guías.")
    parser.add_argument("--si", action="store_true", help="Ejecuta el borrado de verdad.")
    parser.add_argument(
        "--con-roles",
        action="store_true",
        help="Borra también los roles que quedarían vacíos.",
    )
    args = parser.parse_args()

    with SessionLocal() as db:
        modelos = (*DEPENDIENTES, Guia, Rol) if args.con_roles else (*DEPENDIENTES, Guia)
        actual = {modelo.__tablename__: _contar(db, modelo) for modelo in modelos}

        if not args.si:
            print("Simulacro. Se borrarían estas filas:")
            for tabla, cuantas in actual.items():
                print(f"  {tabla:24} {cuantas}")
            print("\nVuelve a correrlo con --si para confirmar.")
            return

        borrados = limpiar(db, con_roles=args.con_roles)

    print("Listo. Filas borradas:")
    for tabla, cuantas in borrados.items():
        print(f"  {tabla:24} {cuantas}")


if __name__ == "__main__":
    main()