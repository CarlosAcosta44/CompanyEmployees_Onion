"""
Entidad de dominio: RefreshToken.

Pertenece al núcleo de la Onion Architecture. No conoce el ORM ni FastAPI.
Define la estructura e invariantes del token de refresco de sesión.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass(slots=True)
class RefreshToken:
    """Token de refresco para renovar sesiones sin volver a autenticarse."""

    token: str
    expires_at: datetime
    usuario_id: UUID
    is_revoked: bool = False
    id: UUID = field(default_factory=uuid4)

    @property
    def is_expired(self) -> bool:
        """Retorna True si el token ya expiró."""
        from datetime import timezone
        return datetime.now(timezone.utc) > self.expires_at.replace(tzinfo=datetime.now(timezone.utc).tzinfo if self.expires_at.tzinfo is None else self.expires_at.tzinfo)

    @property
    def is_valid(self) -> bool:
        """Retorna True si el token es activo y no ha expirado."""
        from datetime import timezone
        now = datetime.now(timezone.utc)
        exp = self.expires_at if self.expires_at.tzinfo else self.expires_at.replace(tzinfo=timezone.utc)
        return not self.is_revoked and now < exp

    def revocar(self) -> None:
        """Revoca el token de refresco."""
        self.is_revoked = True
