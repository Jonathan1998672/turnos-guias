from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import engine
from app.core.exception_handlers import registrar_manejadores
from app.routers import api_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="API para armar el rol de guías del Museo Universitario de Ciencias.",
    version="0.1.0",
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Sin esto el navegador no puede leer el nombre del archivo al exportar.
    expose_headers=["Content-Disposition"],
)

registrar_manejadores(app)
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/health", tags=["salud"])
def health() -> dict[str, str]:
    try:
        with engine.connect() as conexion:
            conexion.execute(text("SELECT 1"))
        base_de_datos = "ok"
    except Exception as exc:  # noqa: BLE001 - el health check reporta, no propaga
        base_de_datos = f"error: {exc.__class__.__name__}"

    return {"estado": "ok", "base_de_datos": base_de_datos}
