from datetime import date

from fastapi import APIRouter, Query, Response, status

from app.dependencies import ServicioRoles
from app.models import Rol
from app.schemas.generacion import GenerarRolRequest, GenerarRolResponse, ValidarRolRequest
from app.schemas.rol import RolBorrador, RolDetalle, RolGuardar, RolResumen
from app.schemas.validacion import ResultadoValidacion

router = APIRouter(prefix="/roles", tags=["roles"])


@router.post(
    "/generar",
    response_model=GenerarRolResponse,
    summary="Arma un borrador con los guías presentes, sin guardarlo",
)
def generar_rol(peticion: GenerarRolRequest, servicio: ServicioRoles) -> GenerarRolResponse:
    return servicio.generar(peticion)


@router.post(
    "/validar",
    response_model=ResultadoValidacion,
    summary="Revisa un borrador editado a mano, sin tocar la base de datos",
)
def validar_rol(peticion: ValidarRolRequest, servicio: ServicioRoles) -> ResultadoValidacion:
    return servicio.validar(peticion.borrador)


@router.get("", response_model=list[RolResumen], summary="Historial de roles")
def listar_roles(
    servicio: ServicioRoles,
    fecha: date | None = None,
    limite: int = Query(default=50, ge=1, le=200),
) -> list[Rol]:
    return servicio.listar(fecha=fecha, limite=limite)


@router.post("", response_model=RolDetalle, status_code=status.HTTP_201_CREATED)
def guardar_rol(datos: RolGuardar, servicio: ServicioRoles) -> Rol:
    return servicio.guardar(datos)


@router.get("/{rol_id}", response_model=RolDetalle)
def obtener_rol(rol_id: int, servicio: ServicioRoles) -> Rol:
    return servicio.obtener(rol_id)


@router.patch(
    "/{rol_id}",
    response_model=RolDetalle,
    summary="Reemplaza asignaciones y horas de comida del rol",
)
def actualizar_rol(rol_id: int, datos: RolBorrador, servicio: ServicioRoles) -> Rol:
    return servicio.actualizar(rol_id, datos)


@router.delete("/{rol_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_rol(rol_id: int, servicio: ServicioRoles) -> Response:
    servicio.eliminar(rol_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
