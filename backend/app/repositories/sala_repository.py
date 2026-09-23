from sqlalchemy import select

from app.models import ParComida, Sala
from app.repositories.base import RepositorioBase


class SalaRepositorio(RepositorioBase[Sala]):
    modelo = Sala

    def listar(self, *, solo_activas: bool = False) -> list[Sala]:
        consulta = select(Sala).order_by(Sala.orden, Sala.codigo)
        if solo_activas:
            consulta = consulta.where(Sala.activa.is_(True))
        return list(self.db.scalars(consulta))

    def obtener_por_codigo(self, codigo: str) -> Sala | None:
        return self.db.scalar(select(Sala).where(Sala.codigo == codigo))

    def listar_por_ids(self, ids: list[int]) -> list[Sala]:
        if not ids:
            return []
        return list(self.db.scalars(select(Sala).where(Sala.id.in_(ids))))

    def listar_pares_comida(self) -> list[ParComida]:
        return list(self.db.scalars(select(ParComida).order_by(ParComida.id)))
