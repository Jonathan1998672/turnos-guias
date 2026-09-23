"""Pruebas del catálogo de guías: altas, ediciones, certificaciones y bajas."""

BASE = "/api/v1/guias"


def test_el_catalogo_arranca_vacio(cliente):
    respuesta = cliente.get(BASE)

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_da_de_alta_un_guia_con_certificaciones(cliente, catalogo):
    respuesta = cliente.post(
        BASE,
        json={"nombre": "Bruno", "salas_certificadas": [catalogo["H-21"]]},
    )

    assert respuesta.status_code == 201
    guia = respuesta.json()
    assert guia["nombre"] == "Bruno"
    assert guia["es_super"] is False
    assert guia["activo"] is True
    assert guia["salas_certificadas"] == [catalogo["H-21"]]


def test_recorta_los_espacios_del_nombre(cliente):
    guia = cliente.post(BASE, json={"nombre": "  Carla  "}).json()

    assert guia["nombre"] == "Carla"


def test_rechaza_un_nombre_vacio(cliente):
    respuesta = cliente.post(BASE, json={"nombre": ""})

    assert respuesta.status_code == 422


def test_solo_admite_un_super_guia_activo(cliente):
    cliente.post(BASE, json={"nombre": "Sofía", "es_super": True})

    respuesta = cliente.post(BASE, json={"nombre": "Otro", "es_super": True})

    assert respuesta.status_code == 409
    assert "Sofía" in respuesta.json()["mensaje"]


def test_permite_un_nuevo_super_si_el_anterior_esta_de_baja(cliente):
    anterior = cliente.post(BASE, json={"nombre": "Sofía", "es_super": True}).json()
    cliente.delete(f"{BASE}/{anterior['id']}")

    respuesta = cliente.post(BASE, json={"nombre": "Nadia", "es_super": True})

    assert respuesta.status_code == 201


def test_rechaza_certificar_una_sala_general(cliente, catalogo):
    respuesta = cliente.post(
        BASE,
        json={"nombre": "Bruno", "salas_certificadas": [catalogo["H-22"]]},
    )

    assert respuesta.status_code == 409
    assert "H-22" in respuesta.json()["mensaje"]


def test_rechaza_certificar_una_sala_inexistente(cliente):
    respuesta = cliente.post(BASE, json={"nombre": "Bruno", "salas_certificadas": [9999]})

    assert respuesta.status_code == 404


def test_actualiza_el_nombre_sin_tocar_las_certificaciones(cliente, catalogo):
    guia = cliente.post(
        BASE,
        json={"nombre": "Bruno", "salas_certificadas": [catalogo["H-21"]]},
    ).json()

    respuesta = cliente.patch(f"{BASE}/{guia['id']}", json={"nombre": "Bruno Díaz"})

    assert respuesta.status_code == 200
    actualizado = respuesta.json()
    assert actualizado["nombre"] == "Bruno Díaz"
    assert actualizado["salas_certificadas"] == [catalogo["H-21"]]


def test_reemplaza_las_certificaciones(cliente, catalogo):
    guia = cliente.post(
        BASE,
        json={"nombre": "Bruno", "salas_certificadas": [catalogo["H-21"]]},
    ).json()

    respuesta = cliente.put(
        f"{BASE}/{guia['id']}/certificaciones",
        json={"salas_certificadas": [catalogo["H-27"]]},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["salas_certificadas"] == [catalogo["H-27"]]


def test_vacia_las_certificaciones(cliente, catalogo):
    guia = cliente.post(
        BASE,
        json={"nombre": "Bruno", "salas_certificadas": [catalogo["H-21"], catalogo["H-27"]]},
    ).json()

    respuesta = cliente.put(f"{BASE}/{guia['id']}/certificaciones", json={"salas_certificadas": []})

    assert respuesta.json()["salas_certificadas"] == []


def test_la_baja_es_logica_y_el_guia_sigue_consultable(cliente):
    guia = cliente.post(BASE, json={"nombre": "Fer"}).json()

    assert cliente.delete(f"{BASE}/{guia['id']}").status_code == 204

    todos = cliente.get(BASE).json()
    assert [g["activo"] for g in todos if g["id"] == guia["id"]] == [False]


def test_filtra_por_guias_activos(cliente):
    activo = cliente.post(BASE, json={"nombre": "Gabi"}).json()
    baja = cliente.post(BASE, json={"nombre": "Fer"}).json()
    cliente.delete(f"{BASE}/{baja['id']}")

    ids = [g["id"] for g in cliente.get(BASE, params={"solo_activos": True}).json()]

    assert ids == [activo["id"]]


def test_404_al_editar_un_guia_inexistente(cliente):
    assert cliente.patch(f"{BASE}/9999", json={"nombre": "Nadie"}).status_code == 404
    assert cliente.delete(f"{BASE}/9999").status_code == 404


def test_la_plantilla_de_ejemplo_queda_completa(cliente, plantilla, catalogo):
    guias = {g["nombre"]: g for g in cliente.get(BASE).json()}

    assert len(plantilla) == 7
    assert guias["Sofía"]["es_super"] is True
    assert guias["Bruno"]["salas_certificadas"] == [catalogo["H-21"]]
    assert guias["Elena"]["salas_certificadas"] == [catalogo["H-27"]]
    assert guias["Gabi"]["salas_certificadas"] == []
