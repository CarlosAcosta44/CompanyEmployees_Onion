"""
Implementación concreta del repositorio de refresh tokens usando SQLAlchemy AsyncSession.
"""

from __future__ import annotations
from uuid import UUID
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.refresh_token import RefreshToken
from app.domain.interfaces.refresh_token_repository import IRefreshTokenRepository
from app.infrastructure.database.models import RefreshTokenModel
from app.infrastructure.repositories.mappers import refresh_token_to_domain, refresh_token_to_model


class RefreshTokenRepositoryImpl(IRefreshTokenRepository):
    """Repositorio de refresh tokens con persistencia en SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, refresh_token: RefreshToken) -> RefreshToken:
        model = refresh_token_to_model(refresh_token)
        self._session.add(model)
        return refresh_token

    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.token == token)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return refresh_token_to_domain(model) if model else None

    async def revoke_by_usuario(self, usuario_id: UUID) -> None:
        stmt = (
            update(RefreshTokenModel)
            .where(RefreshTokenModel.usuario_id == usuario_id, RefreshTokenModel.is_revoked == False)
            .values(is_revoked=True)
        )
        await self._session.execute(stmt)
