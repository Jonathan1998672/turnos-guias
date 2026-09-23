from datetime import date

from sqlalchemy import select

from app.models import Rol
from app.repositories.base import RepositorioBase


class RolRepositorio(RepositorioBase[Rol]):
    modelo = Rol

    def listar(self, *, fecha: date | None = None, limite: int = 50) -> list[Rol]:
        consulta = select(Rol).order_by(Rol.fecha.desc(), Rol.id.desc()).limit(limite)
        if fecha is not None:
            consulta = consulta.where(Rol.fecha == fecha)
        return list(self.db.scalars(consulta))

    def obtener_por_fecha_y_turno(self, fecha: date, turno_id: int) -> Rol | None:
        return self.db.scalar(select(Rol).where(Rol.fecha == fecha, Rol.turno_id == turno_id))

    def vaciar_contenido(self, rol: Rol) -> None:
        """Borra participantes y asignaciones para volver a escribirlos."""
        rol.participantes.clear()
        rol.asignaciones.clear()
        self.db.flush()
