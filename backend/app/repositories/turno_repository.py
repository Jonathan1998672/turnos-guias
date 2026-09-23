from sqlalchemy import select

from app.models import Bloque, Turno
from app.repositories.base import RepositorioBase


class TurnoRepositorio(RepositorioBase[Turno]):
    modelo = Turno

    def listar(self) -> list[Turno]:
        return list(self.db.scalars(select(Turno).order_by(Turno.id)))

    def obtener_por_clave(self, clave: str) -> Turno | None:
        return self.db.scalar(select(Turno).where(Turno.clave == clave))

    def listar_bloques(self, turno_id: int) -> list[Bloque]:
        return list(
            self.db.scalars(
                select(Bloque).where(Bloque.turno_id == turno_id).order_by(Bloque.orden)
            )
        )
