import os
import sys
from logging.config import fileConfig
from dotenv import load_dotenv
from sqlalchemy import create_engine, pool
from alembic import context

# Cargar variables de entorno
load_dotenv()

# Agregar el proyecto al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importar Base y todos los modelos para que Alembic los detecte
from app.infrastructure.database.models import Base
from app.domain.entities.compania import Compania
from app.domain.entities.empleado import Empleado

config = context.config

# Inyectar la DATABASE_URL desde .env
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL no está definida en el .env")
config.set_main_option("sqlalchemy.url", database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = create_engine(database_url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()