from datetime import time

from sqlalchemy import ForeignKey, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

CLAVE_FIN_DE_SEMANA = "fin_de_semana"
CLAVE_MATUTINO = "matutino"
CLAVE_VESPERTINO = "vespertino"


class Turno(Base):
    __tablename__ = "turnos"

    id: Mapped[int] = mapped_column(primary_key=True)
    clave: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(80))

    bloques: Mapped[list["Bloque"]] = relationship(
        back_populates="turno",
        cascade="all, delete-orphan",
        order_by="Bloque.orden",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Turno {self.clave}>"


class Bloque(Base):
    """Una franja horaria dentro de un turno, por ejemplo 12:30-15:00."""

    __tablename__ = "bloques"
    __table_args__ = (UniqueConstraint("turno_id", "orden", name="uq_bloque_turno_orden"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    turno_id: Mapped[int] = mapped_column(ForeignKey("turnos.id", ondelete="CASCADE"))
    orden: Mapped[int]
    hora_inicio: Mapped[time] = mapped_column(Time)
    hora_fin: Mapped[time] = mapped_column(Time)
    etiqueta: Mapped[str] = mapped_column(String(40))

    turno: Mapped[Turno] = relationship(back_populates="bloques")

    def contiene(self, momento: time) -> bool:
        return self.hora_inicio <= momento < self.hora_fin

    def __repr__(self) -> str:
        return f"<Bloque {self.etiqueta}>"
