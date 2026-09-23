from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import ErrorDeDominio


async def manejar_error_de_dominio(_: Request, exc: ErrorDeDominio) -> JSONResponse:
    return JSONResponse(
        status_code=exc.codigo_http,
        content={
            "error": exc.__class__.__name__,
            "mensaje": exc.mensaje,
            "detalles": exc.detalles,
        },
    )


def registrar_manejadores(app: FastAPI) -> None:
    app.add_exception_handler(ErrorDeDominio, manejar_error_de_dominio)
