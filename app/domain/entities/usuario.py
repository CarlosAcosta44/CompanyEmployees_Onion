"""
Entidad de dominio: Usuario.

Pertenece al núcleo de la Onion Architecture. No conoce el ORM ni FastAPI.
Define la estructura, invariantes y reglas de negocio del usuario.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from app.domain.validation import ensure_email, ensure_required_text


@dataclass(slots=True)
class Usuario:
    """Usuario del sistema para autenticación y autorización."""

    username: str
    correo: str
    hashed_password: str
    rol: str
    first_name: str = ""
    last_name: str = ""
    phone_number: str = ""
    ciudad: str = ""
    compania_id: UUID | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.username = ensure_required_text(self.username, "username", max_length=100)
        self.correo = ensure_email(self.correo)
        self.hashed_password = ensure_required_text(self.hashed_password, "hashed_password", max_length=200)
        self.rol = ensure_required_text(self.rol, "rol", max_length=50)

    def actualizar_rol(self, nuevo_rol: str) -> None:
        """Actualiza el rol del usuario manteniendo invariants."""
        self.rol = ensure_required_text(nuevo_rol, "rol", max_length=50)

    def asociar_compania(self, compania_id: UUID | None) -> None:
        """Vincula o desvincula al usuario de una compañía específica."""
        self.compania_id = compania_id
