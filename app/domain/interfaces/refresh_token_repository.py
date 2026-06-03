"""
Interfaz abstracta: IRefreshTokenRepository

Define el contrato para la persistencia de tokens de refresco.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.entities.refresh_token import RefreshToken


class IRefreshTokenRepository(ABC):
    """Contrato del repositorio de refresh tokens."""

    @abstractmethod
    async def create(self, refresh_token: RefreshToken) -> RefreshToken:
        """Persiste un nuevo refresh token."""
        ...

    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """Busca un refresh token por su valor de cadena."""
        ...

    @abstractmethod
    async def revoke_by_usuario(self, usuario_id: UUID) -> None:
        """Revoca todos los tokens activos de un usuario."""
        ...
