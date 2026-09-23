"""esquema inicial

Revision ID: a61b70fe0ca2
Revises:
Create Date: 2026-09-21 22:34:19.094447

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a61b70fe0ca2"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

FALSO = sa.text("false")
VERDADERO = sa.text("true")
AHORA = sa.text("CURRENT_TIMESTAMP")


def upgrade() -> None:
    op.create_table(
        "guias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=150), nullable=False),
        sa.Column("es_super", sa.Boolean(), server_default=FALSO, nullable=False),
        sa.Column("activo", sa.Boolean(), server_default=VERDADERO, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=AHORA, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=AHORA, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "salas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("codigo", sa.String(length=10), nullable=False),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("es_funcion", sa.Boolean(), server_default=FALSO, nullable=False),
        sa.Column("solo_super", sa.Boolean(), server_default=FALSO, nullable=False),
        sa.Column("comida_default", sa.Time(), nullable=False),
        sa.Column("orden", sa.Integer(), server_default="0", nullable=False),
        sa.Column("activa", sa.Boolean(), server_default=VERDADERO, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_salas_codigo", "salas", ["codigo"], unique=True)

    op.create_table(
        "turnos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("clave", sa.String(length=30), nullable=False),
        sa.Column("nombre", sa.String(length=80), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_turnos_clave", "turnos", ["clave"], unique=True)

    op.create_table(
        "bloques",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("turno_id", sa.Integer(), nullable=False),
        sa.Column("orden", sa.Integer(), nullable=False),
        sa.Column("hora_inicio", sa.Time(), nullable=False),
        sa.Column("hora_fin", sa.Time(), nullable=False),
        sa.Column("etiqueta", sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(["turno_id"], ["turnos.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("turno_id", "orden", name="uq_bloque_turno_orden"),
    )

    op.create_table(
        "guia_certificaciones",
        sa.Column("guia_id", sa.Integer(), nullable=False),
        sa.Column("sala_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["guia_id"], ["guias.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sala_id"], ["salas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("guia_id", "sala_id"),
    )

    op.create_table(
        "pares_comida",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sala_a_id", sa.Integer(), nullable=False),
        sa.Column("sala_b_id", sa.Integer(), nullable=False),
        sa.CheckConstraint("sala_a_id <> sala_b_id", name="ck_par_comida_distintas"),
        sa.ForeignKeyConstraint(["sala_a_id"], ["salas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sala_b_id"], ["salas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sala_a_id", "sala_b_id", name="uq_par_comida"),
    )

    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("turno_id", sa.Integer(), nullable=False),
        sa.Column("estado", sa.String(length=20), server_default="borrador", nullable=False),
        sa.Column("notas", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=AHORA, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=AHORA, nullable=False),
        sa.CheckConstraint("estado IN ('borrador', 'publicado')", name="ck_rol_estado"),
        sa.ForeignKeyConstraint(["turno_id"], ["turnos.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fecha", "turno_id", name="uq_rol_fecha_turno"),
    )
    op.create_index("ix_roles_fecha", "roles", ["fecha"], unique=False)

    op.create_table(
        "asignaciones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("rol_id", sa.Integer(), nullable=False),
        sa.Column("guia_id", sa.Integer(), nullable=False),
        sa.Column("bloque_id", sa.Integer(), nullable=False),
        sa.Column("sala_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["bloque_id"], ["bloques.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["guia_id"], ["guias.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["rol_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sala_id"], ["salas.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("rol_id", "bloque_id", "guia_id", name="uq_asignacion_guia"),
        sa.UniqueConstraint("rol_id", "bloque_id", "sala_id", name="uq_asignacion_sala"),
    )

    op.create_table(
        "rol_participantes",
        sa.Column("rol_id", sa.Integer(), nullable=False),
        sa.Column("guia_id", sa.Integer(), nullable=False),
        sa.Column("hora_comida", sa.Time(), nullable=False),
        sa.ForeignKeyConstraint(["guia_id"], ["guias.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["rol_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("rol_id", "guia_id"),
    )


def downgrade() -> None:
    op.drop_table("rol_participantes")
    op.drop_table("asignaciones")
    op.drop_index("ix_roles_fecha", table_name="roles")
    op.drop_table("roles")
    op.drop_table("pares_comida")
    op.drop_table("guia_certificaciones")
    op.drop_table("bloques")
    op.drop_index("ix_turnos_clave", table_name="turnos")
    op.drop_table("turnos")
    op.drop_index("ix_salas_codigo", table_name="salas")
    op.drop_table("salas")
    op.drop_table("guias")
