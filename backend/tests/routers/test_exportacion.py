import io
import zipfile

import pytest

FECHA = "2026-09-26"

FIRMAS = {
    "pdf": b"%PDF-",
    "png": b"\x89PNG\r\n\x1a\n",
    "jpg": b"\xff\xd8\xff",
}


@pytest.fixture
def borrador(cliente, turno_id, plantilla):
    respuesta = cliente.post(
        "/api/v1/roles/generar",
        json={"fecha": FECHA, "turno_id": turno_id, "guias_presentes": plantilla},
    )
    return respuesta.json()["borrador"]


@pytest.mark.parametrize("formato", ["xlsx", "csv", "pdf", "png", "jpg"])
def test_exportar_un_borrador_devuelve_un_archivo_con_nombre(cliente, borrador, formato):
    respuesta = cliente.post(
        "/api/v1/roles/exportar", json={"formato": formato, "borrador": borrador}
    )

    assert respuesta.status_code == 200, respuesta.text
    assert len(respuesta.content) > 0
    assert f'filename="rol_{FECHA}.{formato}"' in respuesta.headers["content-disposition"]


@pytest.mark.parametrize("formato", ["pdf", "png", "jpg"])
def test_los_binarios_traen_su_firma_correcta(cliente, borrador, formato):
    respuesta = cliente.post(
        "/api/v1/roles/exportar", json={"formato": formato, "borrador": borrador}
    )

    assert respuesta.content.startswith(FIRMAS[formato])


def test_el_xlsx_es_un_libro_de_excel_abrible(cliente, borrador):
    respuesta = cliente.post(
        "/api/v1/roles/exportar", json={"formato": "xlsx", "borrador": borrador}
    )

    with zipfile.ZipFile(io.BytesIO(respuesta.content)) as libro:
        assert "xl/workbook.xml" in libro.namelist()


def test_el_csv_trae_los_encabezados_y_una_fila_por_guia(cliente, borrador, plantilla):
    respuesta = cliente.post(
        "/api/v1/roles/exportar", json={"formato": "csv", "borrador": borrador}
    )
    texto = respuesta.content.decode("utf-8-sig")

    assert "Guía" in texto
    assert "Hora de comida" in texto
    assert "10:00 - 12:30" in texto
    assert "Sofía (Súper Guía)" in texto
    assert texto.count("H-20") >= 1


def test_exportar_un_rol_guardado(cliente, borrador):
    rol_id = cliente.post("/api/v1/roles", json=borrador).json()["id"]

    respuesta = cliente.get(f"/api/v1/roles/{rol_id}/exportar?formato=pdf")

    assert respuesta.status_code == 200
    assert respuesta.content.startswith(b"%PDF-")


def test_un_formato_inventado_se_rechaza(cliente, borrador):
    respuesta = cliente.post(
        "/api/v1/roles/exportar", json={"formato": "docx", "borrador": borrador}
    )

    assert respuesta.status_code == 422
