"""
Modelos ORM de SQLAlchemy.

Estos modelos pertenecen a Infrastructure. El dominio usa entidades puras
y los repositorios son responsables de mapear entre ambos mundos.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class CompaniaModel(Base):
    __tablename__ = "companias"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    direccion: Mapped[str] = mapped_column(String(300), nullable=False)
    telefono: Mapped[str] = mapped_column(String(20), nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    empleados: Mapped[list[EmpleadoModel]] = relationship(
        "EmpleadoModel",
        back_populates="compania",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class EmpleadoModel(Base):
    __tablename__ = "empleados"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    correo: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    cargo: Mapped[str] = mapped_column(String(100), nullable=False)
    salario: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    compania_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companias.id", ondelete="CASCADE"),
        nullable=False,
    )

    compania: Mapped[CompaniaModel] = relationship("CompaniaModel", back_populates="empleados")
