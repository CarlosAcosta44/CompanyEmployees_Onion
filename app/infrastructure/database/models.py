"""
Base declarativa de SQLAlchemy.

Este módulo define el objeto Base que todos los modelos de dominio
deben heredar para que SQLAlchemy pueda gestionar sus metadatos,
mapeos y migraciones con Alembic.

IMPORTANTE: Este archivo pertenece a la capa de Infrastructure, no al
Domain. Los modelos del dominio importan Base desde aquí para evitar
dependencias circulares, pero el dominio no conoce los detalles de
implementación de SQLAlchemy más allá de la herencia de Base.
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()
