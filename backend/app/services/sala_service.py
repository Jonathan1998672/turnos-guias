from sqlalchemy.orm import Session

from app.core.exceptions import ConflictoDeDatos, RecursoNoEncontrado
from app.models import ParComida, Sala
from app.repositories.sala_repository import SalaRepositorio
from app.schemas.sala import SalaActualizar, SalaCrear


class SalaService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = SalaRepositorio(db)

    def listar(self, *, solo_activas: bool = False) -> list[Sala]:
        return self.repo.listar(solo_activas=solo_activas)

    def obtener(self, sala_id: int) -> Sala:
        sala = self.repo.obtener(sala_id)
        if sala is None:
            raise RecursoNoEncontrado(f"No existe la sala {sala_id}.")
        return sala

    def crear(self, datos: SalaCrear) -> Sala:
        if self.repo.obtener_por_codigo(datos.codigo) is not None:
            raise ConflictoDeDatos(f"Ya existe una sala con el código {datos.codigo}.")

        sala = self.repo.agregar(Sala(**datos.model_dump()))
        self.db.commit()
        return sala

    def actualizar(self, sala_id: int, datos: SalaActualizar) -> Sala:
        sala = self.obtener(sala_id)

        for campo, valor in datos.model_dump(exclude_unset=True).items():
            setattr(sala, campo, valor)

        self.db.flush()
        self.db.commit()
        return sala

    def listar_pares_comida(self) -> list[ParComida]:
        return self.repo.listar_pares_comida()
