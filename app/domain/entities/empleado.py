"""
Entidad de dominio: Empleado.

La entidad es deliberadamente independiente del ORM. Las restricciones
persistentes se configuran en Infrastructure; aqui viven las invariantes
del negocio.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4

from app.domain.validation import ensure_email, ensure_positive_decimal, ensure_required_text


@dataclass(slots=True)
class Empleado:
    """Empleado perteneciente a una compania."""

    nombre: str
    apellido: str
    correo: str
    cargo: str
    salario: Decimal
    compania_id: UUID
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.nombre = ensure_required_text(self.nombre, "nombre", max_length=100)
        self.apellido = ensure_required_text(self.apellido, "apellido", max_length=100)
        self.correo = ensure_email(self.correo)
        self.cargo = ensure_required_text(self.cargo, "cargo", max_length=100)
        self.salario = ensure_positive_decimal(self.salario, "salario", max_digits=10, decimal_places=2)

    def actualizar(
        self,
        *,
        nombre: str | None = None,
        apellido: str | None = None,
        correo: str | None = None,
        cargo: str | None = None,
        salario: Decimal | None = None,
    ) -> None:
        """Actualiza solo los campos entregados y preserva invariantes."""

        if nombre is not None:
            self.nombre = ensure_required_text(nombre, "nombre", max_length=100)
        if apellido is not None:
            self.apellido = ensure_required_text(apellido, "apellido", max_length=100)
        if correo is not None:
            self.correo = ensure_email(correo)
        if cargo is not None:
            self.cargo = ensure_required_text(cargo, "cargo", max_length=100)
        if salario is not None:
            self.salario = ensure_positive_decimal(salario, "salario", max_digits=10, decimal_places=2)
