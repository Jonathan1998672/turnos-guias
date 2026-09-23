"""Cliente de pruebas con una base SQLite en memoria, sembrada desde cero."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.main import app
from app.models import Base
from scripts.seed import sembrar


@pytest.fixture
def sesion():
    motor = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(motor)
    Sesion = sessionmaker(bind=motor, autoflush=False, expire_on_commit=False)

    with Sesion() as db:
        sembrar(db)

    yield Sesion

    Base.metadata.drop_all(motor)
    motor.dispose()


@pytest.fixture
def cliente(sesion):
    def get_db_de_prueba():
        db = sesion()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = get_db_de_prueba
    with TestClient(app) as cliente:
        yield cliente
    app.dependency_overrides.clear()


@pytest.fixture
def catalogo(cliente):
    """Ids de las salas del seed, por código."""
    salas = cliente.get("/api/v1/salas").json()
    return {sala["codigo"]: sala["id"] for sala in salas}


@pytest.fixture
def turno_id(cliente):
    return cliente.get("/api/v1/turnos").json()[0]["id"]


@pytest.fixture
def plantilla(cliente, catalogo):
    """Da de alta la plantilla típica de un sábado y devuelve sus ids."""
    altas = [
        {"nombre": "Sofía", "es_super": True, "salas_certificadas": []},
        {"nombre": "Bruno", "salas_certificadas": [catalogo["H-21"]]},
        {"nombre": "Carla", "salas_certificadas": [catalogo["H-21"]]},
        {"nombre": "Diego", "salas_certificadas": [catalogo["H-27"]]},
        {"nombre": "Elena", "salas_certificadas": [catalogo["H-27"]]},
        {"nombre": "Fer", "salas_certificadas": []},
        {"nombre": "Gabi", "salas_certificadas": []},
    ]

    return [cliente.post("/api/v1/guias", json=alta).json()["id"] for alta in altas]
