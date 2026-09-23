FECHA = "2026-09-26"


def generar(cliente, turno_id, guias_ids):
    respuesta = cliente.post(
        "/api/v1/roles/generar",
        json={"fecha": FECHA, "turno_id": turno_id, "guias_presentes": guias_ids},
    )
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


def test_generar_devuelve_un_borrador_completo(cliente, turno_id, plantilla):
    datos = generar(cliente, turno_id, plantilla)
    borrador = datos["borrador"]

    assert borrador["fecha"] == FECHA
    assert len(borrador["participantes"]) == len(plantilla)
    # Una celda por guía y bloque, aunque venga vacía.
    assert len(borrador["asignaciones"]) == len(plantilla) * 3


def test_el_borrador_generado_no_trae_errores(cliente, turno_id, plantilla):
    datos = generar(cliente, turno_id, plantilla)

    assert datos["validacion"]["valido"] is True


def test_solo_se_usan_las_dos_horas_de_comida(cliente, turno_id, plantilla):
    datos = generar(cliente, turno_id, plantilla)
    horas = {p["hora_comida"] for p in datos["borrador"]["participantes"]}

    assert horas <= {"13:30:00", "14:00:00"}


def test_generar_con_un_guia_inexistente_falla(cliente, turno_id, plantilla):
    respuesta = cliente.post(
        "/api/v1/roles/generar",
        json={"fecha": FECHA, "turno_id": turno_id, "guias_presentes": [*plantilla, 9999]},
    )

    assert respuesta.status_code == 404


def test_validar_detecta_una_edicion_invalida(cliente, turno_id, plantilla, catalogo):
    borrador = generar(cliente, turno_id, plantilla)["borrador"]

    # Mete a un guía general en el Planetario.
    for asignacion in borrador["asignaciones"]:
        if asignacion["guia_id"] == plantilla[5]:
            asignacion["sala_id"] = catalogo["H-21"]
            break

    respuesta = cliente.post("/api/v1/roles/validar", json={"borrador": borrador})
    datos = respuesta.json()

    assert respuesta.status_code == 200
    assert datos["valido"] is False
    assert any(a["regla"] == "sin_certificacion" for a in datos["advertencias"])


def test_validar_detecta_el_empalme_de_comida(cliente, turno_id, plantilla):
    borrador = generar(cliente, turno_id, plantilla)["borrador"]

    for participante in borrador["participantes"]:
        participante["hora_comida"] = "13:30:00"

    datos = cliente.post("/api/v1/roles/validar", json={"borrador": borrador}).json()

    assert datos["valido"] is False
    assert any(a["regla"] == "comida_empalmada" for a in datos["advertencias"])


def test_guardar_y_recuperar_el_rol(cliente, turno_id, plantilla):
    borrador = generar(cliente, turno_id, plantilla)["borrador"]

    creado = cliente.post("/api/v1/roles", json={**borrador, "estado": "publicado"})
    assert creado.status_code == 201, creado.text
    rol_id = creado.json()["id"]

    recuperado = cliente.get(f"/api/v1/roles/{rol_id}").json()

    assert recuperado["estado"] == "publicado"
    assert len(recuperado["participantes"]) == len(plantilla)
    # Al guardar se descartan las celdas sin sala.
    asignadas = [a for a in borrador["asignaciones"] if a["sala_id"] is not None]
    assert len(recuperado["asignaciones"]) == len(asignadas)


def test_no_se_pueden_guardar_dos_roles_el_mismo_dia(cliente, turno_id, plantilla):
    borrador = generar(cliente, turno_id, plantilla)["borrador"]
    cliente.post("/api/v1/roles", json=borrador)

    segundo = cliente.post("/api/v1/roles", json=borrador)

    assert segundo.status_code == 409


def test_actualizar_reemplaza_las_asignaciones(cliente, turno_id, plantilla):
    borrador = generar(cliente, turno_id, plantilla)["borrador"]
    rol_id = cliente.post("/api/v1/roles", json=borrador).json()["id"]

    borrador["asignaciones"] = borrador["asignaciones"][:3]
    actualizado = cliente.patch(f"/api/v1/roles/{rol_id}", json=borrador).json()

    esperadas = [a for a in borrador["asignaciones"] if a["sala_id"] is not None]
    assert len(actualizado["asignaciones"]) == len(esperadas)


def test_listar_e_eliminar(cliente, turno_id, plantilla):
    borrador = generar(cliente, turno_id, plantilla)["borrador"]
    rol_id = cliente.post("/api/v1/roles", json=borrador).json()["id"]

    listado = cliente.get("/api/v1/roles").json()
    assert len(listado) == 1
    assert listado[0]["total_participantes"] == len(plantilla)

    assert cliente.delete(f"/api/v1/roles/{rol_id}").status_code == 204
    assert cliente.get("/api/v1/roles").json() == []
