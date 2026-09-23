from fastapi import APIRouter

from app.routers import exportacion, guias, roles, salas, turnos

api_router = APIRouter()
api_router.include_router(salas.router)
api_router.include_router(guias.router)
api_router.include_router(turnos.router)
api_router.include_router(roles.router)
api_router.include_router(exportacion.router)
