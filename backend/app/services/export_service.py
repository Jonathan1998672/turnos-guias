"""Convierte un rol en el archivo que se va a descargar."""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.exceptions import FormatoNoSoportado
from app.exporters import (
    CsvExportador,
    Exportador,
    FilaExportable,
    ImagenExportador,
    PdfExportador,
    RolExportable,
    XlsxExportador,
    formatear_hora,
)
from app.repositories.guia_repository import GuiaRepositorio
from app.repositories.sala_repository import SalaRepositorio
from app.schemas.exportacion import FormatoExportacion
from app.schemas.rol import RolBorrador
from app.services.rol_service import RolService
from app.services.turno_service import TurnoService

SIN_SALA = "—"


@dataclass(frozen=True, slots=True)
class ArchivoExportado:
    contenido: bytes
    nombre: str
    media_type: str


def _exportador(formato: FormatoExportacion) -> Exportador:
    match formato:
        case FormatoExportacion.XLSX:
            return XlsxExportador()
        case FormatoExportacion.CSV:
            return CsvExportador()
        case FormatoExportacion.PDF:
            return PdfExportador()
        case FormatoExportacion.PNG | FormatoExportacion.JPG:
            return ImagenExportador(formato.value)
        case _:
            raise FormatoNoSoportado(f"No se puede exportar a {formato}.")


class ExportService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.guias = GuiaRepositorio(db)
        self.salas = SalaRepositorio(db)
        self.turnos = TurnoService(db)
        self.roles = RolService(db)

    def exportar_borrador(
        self, borrador: RolBorrador, formato: FormatoExportacion
    ) -> ArchivoExportado:
        exportador = _exportador(formato)
        rol = self._armar(borrador)

        return ArchivoExportado(
            contenido=exportador.exportar(rol),
            nombre=rol.nombre_archivo(exportador.extension),
            media_type=exportador.media_type,
        )

    def exportar_guardado(self, rol_id: int, formato: FormatoExportacion) -> ArchivoExportado:
        rol = self.roles.obtener(rol_id)
        borrador = self.roles.a_borrador(rol)
        return self.exportar_borrador(borrador, formato)

    def _armar(self, borrador: RolBorrador) -> RolExportable:
        turno = self.turnos.obtener(borrador.turno_id)
        bloques = sorted(turno.bloques, key=lambda b: b.orden)

        guias_ids = [p.guia_id for p in borrador.participantes]
        guias = {g.id: g for g in self.guias.listar_por_ids(guias_ids)}
        salas = {s.id: s for s in self.salas.listar()}

        # (guia_id, bloque_id) -> sala_id
        asignadas = {(a.guia_id, a.bloque_id): a.sala_id for a in borrador.asignaciones}

        filas = []
        for participante in borrador.participantes:
            guia = guias.get(participante.guia_id)
            if guia is None:
                continue

            filas.append(
                FilaExportable(
                    guia=guia.nombre,
                    es_super=guia.es_super,
                    salas=[
                        self._texto_sala(salas.get(asignadas.get((guia.id, bloque.id))))
                        for bloque in bloques
                    ],
                    hora_comida=formatear_hora(participante.hora_comida),
                )
            )

        # El Súper Guía encabeza la tabla, igual que en la pantalla.
        filas.sort(key=lambda fila: (not fila.es_super, fila.guia.lower()))

        return RolExportable(
            fecha=borrador.fecha,
            turno=turno.nombre,
            encabezados_bloques=[bloque.etiqueta for bloque in bloques],
            filas=filas,
            notas=borrador.notas,
        )

    def _texto_sala(self, sala) -> str:
        return f"{sala.codigo} · {sala.nombre}" if sala else SIN_SALA
