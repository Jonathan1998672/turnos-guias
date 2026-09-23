from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PUERTO_POOLER_TRANSACCIONAL = "6543"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Turnos y Salas — Museo Universitario de Ciencias"
    api_prefix: str = "/api/v1"
    debug: bool = False

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/turnos"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _separar_origenes(cls, valor: object) -> object:
        if isinstance(valor, str):
            return [origen.strip() for origen in valor.split(",") if origen.strip()]
        return valor

    @field_validator("database_url", mode="after")
    @classmethod
    def _usar_driver_psycopg3(cls, valor: str) -> str:
        # Supabase entrega la URI como postgresql://... y SQLAlchemy resolvería
        # eso a psycopg2, que no está instalado.
        if valor.startswith("postgresql://"):
            return valor.replace("postgresql://", "postgresql+psycopg://", 1)
        if valor.startswith("postgres://"):
            return valor.replace("postgres://", "postgresql+psycopg://", 1)
        return valor

    @property
    def usa_pooler_transaccional(self) -> bool:
        return f":{PUERTO_POOLER_TRANSACCIONAL}" in self.database_url

    @property
    def es_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()
