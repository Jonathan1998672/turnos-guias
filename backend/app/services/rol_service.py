"""Orquesta la generación, validación y persistencia del rol.

Es el único punto donde se traduce entre el ORM y las dataclasses puras de
`scheduling`. El solver nunca ve una sesión de base de datos.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictoDeDatos, RecursoNoEncontrado
from app.models import Asignacion, Bloque, Guia, ParComida, Rol, RolParticipante, Sala, Turno
from app.repositories.guia_repository import GuiaRepositorio
from app.repositories.rol_repository import RolRepositorio
from app.repositories.sala_repository import SalaRepositorio
from app.scheduling.comidas import normalizar
from app.scheduling.dominio import (
    BloqueHorario,
    EntradaSolver,
    GuiaDisponible,
    ParDeComida,
    SalaDisponible,
    SlotAsignado,
)
from app.scheduling.solver import resolver
from app.schemas.generacion import GenerarRolRequest, GenerarRolResponse
from app.schemas.rol import AsignacionBorrador, ParticipanteBorrador, RolBorrador, RolGuardar
from app.schemas.validacion import ResultadoValidacion
from app.services.turno_service import TurnoService
from app.services.validacion_service import ValidacionService


@dataclass(slots=True)
class ContextoRol:
    """El catálogo traducido a dataclasses, listo para el solver."""

    turno: Turno
    guias: list[GuiaDisponible]
    salas: list[SalaDisponible]
    bloques: list[BloqueHorario]
    pares_comida: list[ParDeComida]

    @property
    def validador(self) -> ValidacionService:
        return ValidacionService(self.guias, self.salas, self.bloques, self.pares_comida)


class RolService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = RolRepositorio(db)
        self.guias = GuiaRepositorio(db)
        self.salas = SalaRepositorio(db)
        self.turnos = TurnoService(db)

    # --- Generación y validación -----------------------------------------

    def generar(self, peticion: GenerarRolRequest) -> GenerarRolResponse:
        contexto = self._contexto(peticion.turno_id, peticion.guias_presentes)

        resultado = resolver(
            EntradaSolver(
                guias=contexto.guias,
                salas=contexto.salas,
                bloques=contexto.bloques,
                pares_comida=contexto.pares_comida,
                intentos=peticion.intentos,
            )
        )

        borrador = RolBorrador(
            fecha=peticion.fecha,
            turno_id=contexto.turno.id,
            participantes=[
                ParticipanteBorrador(guia_id=guia_id, hora_comida=hora)
                for guia_id, hora in sorted(resultado.comidas.items())
            ],
            asignaciones=[
                AsignacionBorrador(
                    guia_id=slot.guia_id, bloque_id=slot.bloque_id, sala_id=slot.sala_id
                )
                for slot in resultado.asignaciones
            ],
        )

        return GenerarRolResponse(
            borrador=borrador,
            validacion=contexto.validador.validar(resultado.asignaciones, resultado.comidas),
        )

    def validar(self, borrador: RolBorrador) -> ResultadoValidacion:
        guias_ids = _guias_del_borrador(borrador)
        contexto = self._contexto(borrador.turno_id, guias_ids)

        return contexto.validador.validar(
            [
                SlotAsignado(guia_id=a.guia_id, bloque_id=a.bloque_id, sala_id=a.sala_id)
                for a in borrador.asignaciones
            ],
            {p.guia_id: p.hora_comida for p in borrador.participantes},
        )

    # --- Persistencia -----------------------------------------------------

    def listar(self, *, fecha: date | None = None, limite: int = 50) -> list[Rol]:
        return self.repo.listar(fecha=fecha, limite=limite)

    def obtener(self, rol_id: int) -> Rol:
        rol = self.repo.obtener(rol_id)
        if rol is None:
            raise RecursoNoEncontrado(f"No existe el rol {rol_id}.")
        return rol

    def guardar(self, datos: RolGuardar) -> Rol:
        turno = self.turnos.obtener(datos.turno_id)

        if self.repo.obtener_por_fecha_y_turno(datos.fecha, turno.id) is not None:
            raise ConflictoDeDatos(
                f"Ya hay un rol guardado para el {datos.fecha:%d/%m/%Y}.",
                detalles=["Ábrelo desde el historial y edítalo, o bórralo primero."],
            )

        rol = self.repo.agregar(
            Rol(
                fecha=datos.fecha,
                turno_id=turno.id,
                estado=datos.estado,
                notas=datos.notas,
            )
        )

        self._escribir_contenido(rol, datos)
        self.db.commit()
        return rol

    def actualizar(self, rol_id: int, datos: RolBorrador) -> Rol:
        rol = self.obtener(rol_id)

        rol.notas = datos.notas
        self.repo.vaciar_contenido(rol)
        self._escribir_contenido(rol, datos)

        self.db.commit()
        return rol

    def eliminar(self, rol_id: int) -> None:
        self.repo.eliminar(self.obtener(rol_id))
        self.db.commit()

    def a_borrador(self, rol: Rol) -> RolBorrador:
        return RolBorrador.model_validate(rol)

    # --- Interno ----------------------------------------------------------

    def _contexto(self, turno_id: int | None, guias_ids: Sequence[int]) -> ContextoRol:
        turno = (
            self.turnos.obtener(turno_id)
            if turno_id is not None
            else self.turnos.obtener_por_defecto()
        )

        if not turno.bloques:
            raise RecursoNoEncontrado(f"El turno {turno.nombre} no tiene bloques configurados.")

        guias = self.guias.listar_por_ids(list(guias_ids))
        faltantes = set(guias_ids) - {guia.id for guia in guias}
        if faltantes:
            raise RecursoNoEncontrado(
                f"No existen los guías: {', '.join(str(i) for i in sorted(faltantes))}."
            )

        salas = self.salas.listar(solo_activas=True)

        return ContextoRol(
            turno=turno,
            guias=[_a_guia_disponible(guia) for guia in guias],
            salas=[_a_sala_disponible(sala) for sala in salas],
            bloques=[_a_bloque_horario(bloque) for bloque in turno.bloques],
            pares_comida=[_a_par_de_comida(par) for par in self.salas.listar_pares_comida()],
        )

    def _escribir_contenido(self, rol: Rol, datos: RolBorrador) -> None:
        for participante in datos.participantes:
            rol.participantes.append(
                RolParticipante(
                    guia_id=participante.guia_id,
                    hora_comida=normalizar(participante.hora_comida),
                )
            )

        for asignacion in datos.asignaciones:
            if asignacion.sala_id is None:
                continue
            rol.asignaciones.append(
                Asignacion(
                    guia_id=asignacion.guia_id,
                    bloque_id=asignacion.bloque_id,
                    sala_id=asignacion.sala_id,
                )
            )

        self.db.flush()


# --- Traducción ORM -> dataclasses -----------------------------------------


def _a_guia_disponible(guia: Guia) -> GuiaDisponible:
    return GuiaDisponible(
        id=guia.id,
        nombre=guia.nombre,
        es_super=guia.es_super,
        salas_certificadas=frozenset(guia.salas_certificadas),
    )


def _a_sala_disponible(sala: Sala) -> SalaDisponible:
    return SalaDisponible(
        id=sala.id,
        codigo=sala.codigo,
        nombre=sala.nombre,
        es_funcion=sala.es_funcion,
        solo_super=sala.solo_super,
        comida_default=sala.comida_default,
        orden=sala.orden,
    )


def _a_bloque_horario(bloque: Bloque) -> BloqueHorario:
    return BloqueHorario(
        id=bloque.id,
        orden=bloque.orden,
        etiqueta=bloque.etiqueta,
        hora_inicio=bloque.hora_inicio,
        hora_fin=bloque.hora_fin,
    )


def _a_par_de_comida(par: ParComida) -> ParDeComida:
    return ParDeComida(sala_a_id=par.sala_a_id, sala_b_id=par.sala_b_id)


def _guias_del_borrador(borrador: RolBorrador) -> list[int]:
    ids = {p.guia_id for p in borrador.participantes}
    ids |= {a.guia_id for a in borrador.asignaciones}
    return sorted(ids)
