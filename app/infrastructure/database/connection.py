"""
Configuración de la conexión a la base de datos PostgreSQL.

Crea el engine de SQLAlchemy y el generador de sesiones (SessionLocal)
que será usado por el Unit of Work para manejar transacciones.
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("La variable de entorno DATABASE_URL no está definida.")

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

logger.info("[Database] Engine configurado correctamente.")