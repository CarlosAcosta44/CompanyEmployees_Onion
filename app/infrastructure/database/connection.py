"""Configuracion de conexion para PostgreSQL o SQLite."""

import logging
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.infrastructure.config.settings import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()
DATABASE_URL = settings.database_url

if not DATABASE_URL:
    raise ValueError("La variable de entorno DATABASE_URL no está definida.")

engine_args = {"echo": settings.debug}
if DATABASE_URL.startswith("sqlite"):
    DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
    engine_args["connect_args"] = {"check_same_thread": False}
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    engine_args["pool_pre_ping"] = True

engine = create_async_engine(
    DATABASE_URL,
    **engine_args
)

if DATABASE_URL.startswith("sqlite"):

    @event.listens_for(engine.sync_engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)

logger.info("[Database] Engine configurado correctamente para %s.", engine.url.get_backend_name())
