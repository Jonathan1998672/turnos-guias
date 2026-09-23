from collections.abc import Iterator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import get_settings

settings = get_settings()

connect_args: dict[str, Any] = {}
engine_kwargs: dict[str, Any] = {}

if settings.usa_pooler_transaccional:
    # PgBouncer en modo transacción no soporta los prepared statements que
    # psycopg3 crea por su cuenta, y tampoco tiene sentido mantener un pool
    # local encima de un pool remoto.
    connect_args["prepare_threshold"] = None
    engine_kwargs["poolclass"] = NullPool
elif not settings.es_sqlite:
    engine_kwargs.update(pool_size=5, max_overflow=10, pool_pre_ping=True)

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args=connect_args,
    **engine_kwargs,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """Sesión por petición. Los servicios son los que hacen commit."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
