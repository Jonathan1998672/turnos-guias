from sqlalchemy import select

from app.models import Guia, GuiaCertificacion
from app.repositories.base import RepositorioBase


class GuiaRepositorio(RepositorioBase[Guia]):
    modelo = Guia

    def listar(self, *, solo_activos: bool = False) -> list[Guia]:
        consulta = select(Guia).order_by(Guia.es_super.desc(), Guia.nombre)
        if solo_activos:
            consulta = consulta.where(Guia.activo.is_(True))
        return list(self.db.scalars(consulta))

    def listar_por_ids(self, ids: list[int]) -> list[Guia]:
        if not ids:
            return []
        return list(self.db.scalars(select(Guia).where(Guia.id.in_(ids))))

    def obtener_super_activo(self, *, excluir_id: int | None = None) -> Guia | None:
        consulta = select(Guia).where(Guia.es_super.is_(True), Guia.activo.is_(True))
        if excluir_id is not None:
            consulta = consulta.where(Guia.id != excluir_id)
        return self.db.scalars(consulta).first()

    def reemplazar_certificaciones(self, guia: Guia, salas_ids: list[int]) -> None:
        # dict.fromkeys quita duplicados sin perder el orden en que llegaron.
        guia.certificaciones = [
            GuiaCertificacion(guia_id=guia.id, sala_id=sala_id)
            for sala_id in dict.fromkeys(salas_ids)
        ]
        self.db.flush()
