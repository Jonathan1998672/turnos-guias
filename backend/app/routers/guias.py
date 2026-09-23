from fastapi import APIRouter, Response, status

from app.dependencies import ServicioGuias
from app.models import Guia
from app.schemas.guia import CertificacionesActualizar, GuiaActualizar, GuiaCrear, GuiaOut

router = APIRouter(prefix="/guias", tags=["guias"])


@router.get("", response_model=list[GuiaOut], summary="Catálogo de guías")
def listar_guias(servicio: ServicioGuias, solo_activos: bool = False) -> list[Guia]:
    return servicio.listar(solo_activos=solo_activos)


@router.post("", response_model=GuiaOut, status_code=status.HTTP_201_CREATED)
def crear_guia(datos: GuiaCrear, servicio: ServicioGuias) -> Guia:
    return servicio.crear(datos)


@router.patch("/{guia_id}", response_model=GuiaOut)
def actualizar_guia(guia_id: int, datos: GuiaActualizar, servicio: ServicioGuias) -> Guia:
    return servicio.actualizar(guia_id, datos)


@router.put(
    "/{guia_id}/certificaciones",
    response_model=GuiaOut,
    summary="Reemplaza las salas de función que el guía puede dar",
)
def reemplazar_certificaciones(
    guia_id: int, datos: CertificacionesActualizar, servicio: ServicioGuias
) -> Guia:
    return servicio.reemplazar_certificaciones(guia_id, datos.salas_certificadas)


@router.delete(
    "/{guia_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Baja lógica: el guía deja de aparecer pero conserva su historial",
)
def dar_de_baja(guia_id: int, servicio: ServicioGuias) -> Response:
    servicio.dar_de_baja(guia_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
