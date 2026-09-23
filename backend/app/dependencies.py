from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.export_service import ExportService
from app.services.guia_service import GuiaService
from app.services.rol_service import RolService
from app.services.sala_service import SalaService
from app.services.turno_service import TurnoService

SesionDB = Annotated[Session, Depends(get_db)]


def get_sala_service(db: SesionDB) -> SalaService:
    return SalaService(db)


def get_guia_service(db: SesionDB) -> GuiaService:
    return GuiaService(db)


def get_turno_service(db: SesionDB) -> TurnoService:
    return TurnoService(db)


def get_rol_service(db: SesionDB) -> RolService:
    return RolService(db)


def get_export_service(db: SesionDB) -> ExportService:
    return ExportService(db)


ServicioSalas = Annotated[SalaService, Depends(get_sala_service)]
ServicioGuias = Annotated[GuiaService, Depends(get_guia_service)]
ServicioTurnos = Annotated[TurnoService, Depends(get_turno_service)]
ServicioRoles = Annotated[RolService, Depends(get_rol_service)]
ServicioExportacion = Annotated[ExportService, Depends(get_export_service)]
