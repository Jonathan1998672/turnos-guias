from fastapi import APIRouter, Query
from fastapi.responses import Response

from app.dependencies import ServicioExportacion
from app.schemas.exportacion import ExportarBorradorRequest, FormatoExportacion
from app.services.export_service import ArchivoExportado

router = APIRouter(prefix="/roles", tags=["exportación"])

DESCRIPCION_FORMATO = "xlsx, csv, pdf, png o jpg."


def _descarga(archivo: ArchivoExportado) -> Response:
    return Response(
        content=archivo.contenido,
        media_type=archivo.media_type,
        headers={"Content-Disposition": f'attachment; filename="{archivo.nombre}"'},
    )


@router.post(
    "/exportar",
    summary="Descarga un borrador sin haberlo guardado",
    response_class=Response,
)
def exportar_borrador(peticion: ExportarBorradorRequest, servicio: ServicioExportacion) -> Response:
    return _descarga(servicio.exportar_borrador(peticion.borrador, peticion.formato))


@router.get(
    "/{rol_id}/exportar",
    summary="Descarga un rol ya guardado",
    response_class=Response,
)
def exportar_rol_guardado(
    rol_id: int,
    servicio: ServicioExportacion,
    formato: FormatoExportacion = Query(
        default=FormatoExportacion.XLSX, description=DESCRIPCION_FORMATO
    ),
) -> Response:
    return _descarga(servicio.exportar_guardado(rol_id, formato))
