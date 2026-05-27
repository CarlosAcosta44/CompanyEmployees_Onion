"""
Entidad de dominio: Compania.

Esta clase no conoce FastAPI, SQLAlchemy, Alembic ni la base de datos.
Es parte del nucleo de Onion Architecture y solo expresa estado y reglas
propias del negocio.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from app.domain.validation import ensure_required_text

if TYPE_CHECKING:
    from app.domain.entities.empleado import Empleado


@dataclass(slots=True)
class Compania:
    """Compania registrada en el sistema."""

    nombre: str
    direccion: str
    telefono: str
    id: UUID = field(default_factory=uuid4)
    fecha_creacion: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    empleados: list[Empleado] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.nombre = ensure_required_text(self.nombre, "nombre", max_length=200)
        self.direccion = ensure_required_text(self.direccion, "direccion", max_length=300)
        self.telefono = ensure_required_text(self.telefono, "telefono", min_length=7, max_length=20)

        if self.fecha_creacion.tzinfo is None:
            self.fecha_creacion = self.fecha_creacion.replace(tzinfo=timezone.utc)

    def actualizar(
        self,
        *,
        nombre: str | None = None,
        direccion: str | None = None,
        telefono: str | None = None,
    ) -> None:
        """Actualiza solo los campos entregados y preserva invariantes."""

        if nombre is not None:
            self.nombre = ensure_required_text(nombre, "nombre", max_length=200)
        if direccion is not None:
            self.direccion = ensure_required_text(direccion, "direccion", max_length=300)
        if telefono is not None:
            self.telefono = ensure_required_text(telefono, "telefono", min_length=7, max_length=20)

    def agregar_empleado(self, empleado: Empleado) -> None:
        """Asocia un empleado ya construido a esta compania."""

        if empleado.compania_id != self.id:
            empleado.compania_id = self.id
        self.empleados.append(empleado)
