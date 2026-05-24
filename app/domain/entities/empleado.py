"""
Entidad de dominio: Empleado

Representa la tabla 'empleados' en la base de datos PostgreSQL.
Define la estructura de datos de un empleado y su relación muchos a uno
con la entidad Compania.
"""

from sqlalchemy import Column, String, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.infrastructure.database.models import Base


class Empleado(Base):
    """
    Modelo SQLAlchemy que representa un empleado registrado en el sistema.

    Atributos:
        id          -- Identificador único universal (UUID v4), llave primaria.
        nombre      -- Nombre del empleado. Requerido.
        apellido    -- Apellido del empleado. Requerido.
        correo      -- Correo electrónico único del empleado. Requerido.
        cargo       -- Cargo o rol del empleado dentro de la compañía. Requerido.
        salario     -- Salario asignado al empleado (precisión decimal). Requerido.
        compania_id -- Llave foránea hacia la compañía a la que pertenece.
        compania    -- Referencia a la instancia de Compania relacionada.
    """

    __tablename__ = "empleados"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    correo = Column(String(150), nullable=False, unique=True, index=True)
    cargo = Column(String(100), nullable=False)

    # Numeric(10, 2) garantiza precisión financiera: hasta 10 dígitos totales
    # con 2 decimales. Evita errores de redondeo propios de Float.
    salario = Column(Numeric(10, 2), nullable=False)

    compania_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companias.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relación N:1 con Compania.
    compania = relationship("Compania", back_populates="empleados")

    def __repr__(self) -> str:
        return (
            f"<Empleado id={self.id} nombre='{self.nombre} {self.apellido}' "
            f"cargo='{self.cargo}'>"
        )
