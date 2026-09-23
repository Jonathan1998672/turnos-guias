from fastapi import APIRouter, status

from app.dependencies import ServicioSalas
from app.models import ParComida, Sala
from app.schemas.sala import ParComidaOut, SalaActualizar, SalaCrear, SalaOut

router = APIRouter(prefix="/salas", tags=["salas"])


@router.get("", response_model=list[SalaOut], summary="Catálogo de salas")
def listar_salas(servicio: ServicioSalas, solo_activas: bool = False) -> list[Sala]:
    return servicio.listar(solo_activas=solo_activas)


# Va antes que cualquier ruta con parámetro para que no la capture.
@router.get(
    "/pares-comida",
    response_model=list[ParComidaOut],
    summary="Parejas de salas que no pueden empalmar la comida",
)
def listar_pares_comida(servicio: ServicioSalas) -> list[ParComida]:
    return servicio.listar_pares_comida()


@router.post("", response_model=SalaOut, status_code=status.HTTP_201_CREATED)
def crear_sala(datos: SalaCrear, servicio: ServicioSalas) -> Sala:
    return servicio.crear(datos)


@router.patch("/{sala_id}", response_model=SalaOut)
def actualizar_sala(sala_id: int, datos: SalaActualizar, servicio: ServicioSalas) -> Sala:
    return servicio.actualizar(sala_id, datos)
