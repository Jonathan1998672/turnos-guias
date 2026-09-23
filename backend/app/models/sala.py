from datetime import time

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    String,
    Time,
    UniqueConstraint,
    false,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Sala(Base):
    """Una sala del museo.

    El requisito de quién puede cubrirla no se guarda como un campo aparte, se
    deriva: `solo_super` exige al Súper Guía, `es_funcion` exige certificación y
    en cualquier otro caso sirve cualquier guía activo.
    """

    __tablename__ = "salas"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120))
    es_funcion: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    solo_super: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    comida_default: Mapped[time] = mapped_column(Time)
    orden: Mapped[int] = mapped_column(default=0, server_default="0")
    activa: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())

    def __repr__(self) -> str:
        return f"<Sala {self.codigo} {self.nombre}>"


class ParComida(Base):
    """Dos salas cuyos guías no pueden comer a la misma hora.

    Cada pareja se guarda una sola vez, con el id menor en `sala_a_id`.
    """

    __tablename__ = "pares_comida"
    __table_args__ = (
        UniqueConstraint("sala_a_id", "sala_b_id", name="uq_par_comida"),
        CheckConstraint("sala_a_id <> sala_b_id", name="ck_par_comida_distintas"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sala_a_id: Mapped[int] = mapped_column(ForeignKey("salas.id", ondelete="CASCADE"))
    sala_b_id: Mapped[int] = mapped_column(ForeignKey("salas.id", ondelete="CASCADE"))

    sala_a: Mapped[Sala] = relationship(foreign_keys=[sala_a_id], lazy="joined")
    sala_b: Mapped[Sala] = relationship(foreign_keys=[sala_b_id], lazy="joined")

    def __repr__(self) -> str:
        return f"<ParComida {self.sala_a_id}-{self.sala_b_id}>"
