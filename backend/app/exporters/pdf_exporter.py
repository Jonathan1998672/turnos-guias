import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.exporters.base import RolExportable

AZUL_OSCURO = colors.HexColor("#1e293b")
GRIS_CLARO = colors.HexColor("#f1f5f9")
GRIS_BORDE = colors.HexColor("#94a3b8")


class PdfExportador:
    extension = "pdf"
    media_type = "application/pdf"

    def exportar(self, rol: RolExportable) -> bytes:
        buffer = io.BytesIO()
        documento = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            leftMargin=14 * mm,
            rightMargin=14 * mm,
            topMargin=14 * mm,
            bottomMargin=14 * mm,
            title=rol.titulo,
        )

        documento.build(self._contenido(rol, documento.width))
        return buffer.getvalue()

    def _contenido(self, rol: RolExportable, ancho: float) -> list:
        estilos = getSampleStyleSheet()
        titulo = ParagraphStyle("titulo", parent=estilos["Title"], fontSize=17, spaceAfter=2)
        subtitulo = ParagraphStyle(
            "subtitulo", parent=estilos["Normal"], fontSize=10, alignment=1, textColor=GRIS_BORDE
        )
        celda = ParagraphStyle("celda", parent=estilos["Normal"], fontSize=8.5, leading=11)

        elementos = [
            Paragraph(rol.titulo, titulo),
            Paragraph(f"Turno: {rol.turno}", subtitulo),
            Spacer(1, 7 * mm),
            self._tabla(rol, ancho, celda),
        ]

        if rol.notas:
            elementos += [Spacer(1, 5 * mm), Paragraph(f"<b>Notas:</b> {rol.notas}", celda)]

        return elementos

    def _tabla(self, rol: RolExportable, ancho: float, estilo_celda: ParagraphStyle) -> Table:
        filas = rol.como_tabla()
        columnas = len(rol.encabezados)

        # La columna del guía es más ancha; el resto se reparte lo que sobra.
        ancho_guia = ancho * 0.22
        ancho_resto = (ancho - ancho_guia) / (columnas - 1)

        datos = [
            filas[0],
            *[[Paragraph(str(valor), estilo_celda) for valor in fila] for fila in filas[1:]],
        ]

        tabla = Table(
            datos,
            colWidths=[ancho_guia, *[ancho_resto] * (columnas - 1)],
            repeatRows=1,
        )
        tabla.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), AZUL_OSCURO),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("BACKGROUND", (-1, 1), (-1, -1), GRIS_CLARO),
                    ("ALIGN", (-1, 1), (-1, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -1), 0.5, GRIS_BORDE),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("ROWBACKGROUNDS", (0, 1), (-2, -1), [colors.white, GRIS_CLARO]),
                ]
            )
        )

        return tabla
