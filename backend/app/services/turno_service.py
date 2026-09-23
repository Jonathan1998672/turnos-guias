from sqlalchemy.orm import Session

from app.core.exceptions import RecursoNoEncontrado
from app.models import Bloque, Turno
from app.models.turno import CLAVE_FIN_DE_SEMANA
from app.repositories.turno_repository import TurnoRepositorio


class TurnoService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = TurnoRepositorio(db)

    def listar(self) -> list[Turno]:
        return self.repo.listar()

    def obtener(self, turno_id: int) -> Turno:
        turno = self.repo.obtener(turno_id)
        if turno is None:
            raise RecursoNoEncontrado(f"No existe el turno {turno_id}.")
        return turno

    def obtener_por_defecto(self) -> Turno:
        """El de fin de semana, que es el único con interfaz por ahora."""
        turno = self.repo.obtener_por_clave(CLAVE_FIN_DE_SEMANA)
        if turno is None:
            raise RecursoNoEncontrado(
                "No está sembrado el turno de fin de semana.",
                detalles=["Corre `python -m scripts.seed`."],
            )
        return turno

    def listar_bloques(self, turno_id: int) -> list[Bloque]:
        self.obtener(turno_id)
        return self.repo.listar_bloques(turno_id)
