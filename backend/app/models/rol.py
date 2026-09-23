from datetime import date, time

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    String,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.guia import Guia
from app.models.sala import Sala
from app.models.turno import Bloque, Turno

ESTADO_BORRADOR = "borrador"
ESTADO_PUBLICADO = "publicado"
ESTADOS = (ESTADO_BORRADOR, ESTADO_PUBLICADO)


class Rol(Base, TimestampMixin):
    """El rol de un día: quién asistió, dónde estuvo y a qué hora comió."""

    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("fecha", "turno_id", name="uq_rol_fecha_turno"),
        CheckConstraint(
            f"estado IN ('{ESTADO_BORRADOR}', '{ESTADO_PUBLICADO}')",
            name="ck_rol_estado",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    fecha: Mapped[date] = mapped_column(Date, index=True)
    turno_id: Mapped[int] = mapped_column(ForeignKey("turnos.id", ondelete="RESTRICT"))
    estado: Mapped[str] = mapped_column(
        String(20), default=ESTADO_BORRADOR, server_default=ESTADO_BORRADOR
    )
    notas: Mapped[str | None] = mapped_column(String(500), default=None)

    turno: Mapped[Turno] = relationship(lazy="joined")
    participantes: Mapped[list["RolParticipante"]] = relationship(
        back_populates="rol", cascade="all, delete-orphan", lazy="selectin"
    )
    asignaciones: Mapped[list["Asignacion"]] = relationship(
        back_populates="rol", cascade="all, delete-orphan", lazy="selectin"
    )

    @property
    def total_participantes(self) -> int:
        return len(self.participantes)

    def __repr__(self) -> str:
        return f"<Rol {self.fecha} turno={self.turno_id}>"


class RolParticipante(Base):
    """Un guía que sí asistió ese día, con su hora de comida.

    Es la tabla que materializa la regla 4: el rol no asume que todos vinieron.
    """

    __tablename__ = "rol_participantes"

    rol_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    guia_id: Mapped[int] = mapped_column(
        ForeignKey("guias.id", ondelete="CASCADE"), primary_key=True
    )
    hora_comida: Mapped[time] = mapped_column(Time)

    rol: Mapped[Rol] = relationship(back_populates="participantes")
    guia: Mapped[Guia] = relationship(lazy="joined")


class Asignacion(Base):
    """Un guía en una sala durante un bloque."""

    __tablename__ = "asignaciones"
    __table_args__ = (
        # Dos guías no pueden ocupar la misma sala en el mismo bloque.
        UniqueConstraint("rol_id", "bloque_id", "sala_id", name="uq_asignacion_sala"),
        # Un guía no puede estar en dos salas a la vez.
        UniqueConstraint("rol_id", "bloque_id", "guia_id", name="uq_asignacion_guia"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    rol_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"))
    guia_id: Mapped[int] = mapped_column(ForeignKey("guias.id", ondelete="CASCADE"))
    bloque_id: Mapped[int] = mapped_column(ForeignKey("bloques.id", ondelete="RESTRICT"))
    sala_id: Mapped[int] = mapped_column(ForeignKey("salas.id", ondelete="RESTRICT"))

    rol: Mapped[Rol] = relationship(back_populates="asignaciones")
    guia: Mapped[Guia] = relationship(lazy="joined")
    bloque: Mapped[Bloque] = relationship(lazy="joined")
    sala: Mapped[Sala] = relationship(lazy="joined")
