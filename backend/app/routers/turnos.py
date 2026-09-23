from fastapi import APIRouter

from app.dependencies import ServicioTurnos
from app.models import Bloque, Turno
from app.schemas.turno import BloqueOut, TurnoOut

router = APIRouter(prefix="/turnos", tags=["turnos"])


@router.get("", response_model=list[TurnoOut], summary="Turnos disponibles")
def listar_turnos(servicio: ServicioTurnos) -> list[Turno]:
    return servicio.listar()


@router.get("/{turno_id}/bloques", response_model=list[BloqueOut])
def listar_bloques(turno_id: int, servicio: ServicioTurnos) -> list[Bloque]:
    return servicio.listar_bloques(turno_id)
