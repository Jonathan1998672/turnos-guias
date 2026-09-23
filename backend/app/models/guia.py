from sqlalchemy import Boolean, ForeignKey, String, false, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.sala import Sala


class Guia(Base, TimestampMixin):
    __tablename__ = "guias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150))
    es_super: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())

    certificaciones: Mapped[list["GuiaCertificacion"]] = relationship(
        back_populates="guia",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def salas_certificadas(self) -> list[int]:
        return sorted(c.sala_id for c in self.certificaciones)

    def __repr__(self) -> str:
        return f"<Guia {self.id} {self.nombre}>"


class GuiaCertificacion(Base):
    """Habilita a un guía para una sala de función (H-21 Planetario, H-27 Plasma)."""

    __tablename__ = "guia_certificaciones"

    guia_id: Mapped[int] = mapped_column(
        ForeignKey("guias.id", ondelete="CASCADE"), primary_key=True
    )
    sala_id: Mapped[int] = mapped_column(
        ForeignKey("salas.id", ondelete="CASCADE"), primary_key=True
    )

    guia: Mapped[Guia] = relationship(back_populates="certificaciones")
    sala: Mapped[Sala] = relationship(lazy="joined")
