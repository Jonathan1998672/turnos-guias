"""Convierte el PDF en imagen, que es la que se manda al grupo de WhatsApp.

Se reutiliza el PDF a propósito: así el diseño se mantiene en un solo lugar y
no hay que dibujar la tabla dos veces. La imagen se recorta al contenido para
que no salga media hoja en blanco en el chat.
"""

import pymupdf

from app.exporters.base import RolExportable
from app.exporters.pdf_exporter import PdfExportador

# 2x sobre los 72 dpi del PDF: se lee bien en celular sin pesar de más.
ESCALA = 2.0
MARGEN_PUNTOS = 18


class ImagenExportador:
    def __init__(self, extension: str = "png") -> None:
        self.extension = extension
        self.media_type = "image/jpeg" if extension in ("jpg", "jpeg") else "image/png"
        self._pdf = PdfExportador()

    def exportar(self, rol: RolExportable) -> bytes:
        documento = pymupdf.open(stream=self._pdf.exportar(rol), filetype="pdf")

        try:
            pagina = documento.load_page(0)
            pixmap = pagina.get_pixmap(
                matrix=pymupdf.Matrix(ESCALA, ESCALA),
                clip=_area_con_contenido(pagina),
            )

            if self.media_type == "image/jpeg":
                return pixmap.tobytes("jpeg", jpg_quality=92)
            return pixmap.tobytes("png")
        finally:
            documento.close()


def _area_con_contenido(pagina: pymupdf.Page) -> pymupdf.Rect:
    """Caja que envuelve texto y líneas, más un margen, sin salirse de la hoja."""
    cajas = [pymupdf.Rect(bloque[:4]) for bloque in pagina.get_text("blocks")]
    cajas += [dibujo["rect"] for dibujo in pagina.get_drawings()]

    if not cajas:
        return pagina.rect

    area = cajas[0]
    for caja in cajas[1:]:
        area |= caja

    area += (-MARGEN_PUNTOS, -MARGEN_PUNTOS, MARGEN_PUNTOS, MARGEN_PUNTOS)
    return area & pagina.rect
