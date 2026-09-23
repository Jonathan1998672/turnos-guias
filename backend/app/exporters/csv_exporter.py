import csv
import io

from app.exporters.base import RolExportable


class CsvExportador:
    extension = "csv"
    media_type = "text/csv; charset=utf-8"

    def exportar(self, rol: RolExportable) -> bytes:
        buffer = io.StringIO(newline="")
        escritor = csv.writer(buffer, lineterminator="\r\n")

        escritor.writerow([rol.titulo])
        escritor.writerow([f"Turno: {rol.turno}"])
        escritor.writerow([])
        escritor.writerows(rol.como_tabla())

        if rol.notas:
            escritor.writerow([])
            escritor.writerow([f"Notas: {rol.notas}"])

        # El BOM es lo que hace que Excel abra los acentos bien al dar doble clic.
        return buffer.getvalue().encode("utf-8-sig")
