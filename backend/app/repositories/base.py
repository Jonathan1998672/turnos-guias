from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.base import Base


class RepositorioBase[ModeloT: Base]:
    """CRUD mínimo compartido. Las subclases fijan `modelo`.

    Los repositorios hacen `flush` para que los ids queden disponibles, pero
    nunca `commit`: eso le toca al servicio, que es quien conoce la transacción
    completa.
    """

    modelo: type[ModeloT]

    def __init__(self, db: Session) -> None:
        self.db = db

    def obtener(self, id_: int) -> ModeloT | None:
        return self.db.get(self.modelo, id_)

    def listar(self) -> list[ModeloT]:
        return list(self.db.scalars(select(self.modelo)))

    def agregar(self, instancia: ModeloT) -> ModeloT:
        self.db.add(instancia)
        self.db.flush()
        return instancia

    def eliminar(self, instancia: ModeloT) -> None:
        self.db.delete(instancia)
        self.db.flush()
