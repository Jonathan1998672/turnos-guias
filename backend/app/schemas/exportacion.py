from enum import StrEnum

from pydantic import BaseModel

from app.schemas.rol import RolBorrador


class FormatoExportacion(StrEnum):
    XLSX = "xlsx"
    CSV = "csv"
    PDF = "pdf"
    PNG = "png"
    JPG = "jpg"


class ExportarBorradorRequest(BaseModel):
    formato: FormatoExportacion = FormatoExportacion.XLSX
    borrador: RolBorrador
