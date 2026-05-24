"""
Entidad de dominio: Compania

Representa la tabla 'companias' en la base de datos PostgreSQL.
Define la estructura de datos de una compañía y su relación uno a muchos
con la entidad Empleado.
"""

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone

from app.infrastructure.database.models import Base


class Compania(Base):
    """
    Modelo SQLAlchemy que representa una compañía registrada en el sistema.

    Atributos:
        id          -- Identificador único universal (UUID v4), llave primaria.
        nombre      -- Nombre oficial de la compañía. Requerido.
        direccion   -- Dirección física de la compañía. Requerido.
        telefono    -- Número de contacto de la compañía. Requerido.
        fecha_creacion -- Fecha y hora UTC de registro. Autogenerada.
        empleados   -- Lista de empleados relacionados (relación 1:N).
    """

    __tablename__ = "companias"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    nombre = Column(String(200), nullable=False)
    direccion = Column(String(300), nullable=False)
    telefono = Column(String(20), nullable=False)
    fecha_creacion = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relación 1:N con Empleado.
    # cascade="all, delete-orphan" garantiza que al eliminar una compañía,
    # todos sus empleados también se eliminen (integridad referencial en cascada).
    empleados = relationship(
        "Empleado",
        back_populates="compania",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Compania id={self.id} nombre='{self.nombre}'>"
