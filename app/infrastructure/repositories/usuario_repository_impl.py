"""
Implementación concreta del repositorio de usuarios usando SQLAlchemy y AsyncSession.
"""

from __future__ import annotations
from uuid import UUID
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.usuario import Usuario
from app.domain.interfaces.usuario_repository import IUsuarioRepository
from app.infrastructure.database.models import UsuarioModel
from app.infrastructure.repositories.mappers import usuario_to_domain, usuario_to_model


class UsuarioRepositoryImpl(IUsuarioRepository):
    """Repositorio de usuarios con persistencia en SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, usuario_id: UUID) -> Optional[Usuario]:
        stmt = select(UsuarioModel).where(UsuarioModel.id == usuario_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return usuario_to_domain(model) if model else None

    async def get_by_username(self, username: str) -> Optional[Usuario]:
        stmt = select(UsuarioModel).where(UsuarioModel.username == username)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return usuario_to_domain(model) if model else None

    async def get_by_correo(self, correo: str) -> Optional[Usuario]:
        stmt = select(UsuarioModel).where(UsuarioModel.correo == correo.strip().lower())
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return usuario_to_domain(model) if model else None

    async def create(self, usuario: Usuario) -> Usuario:
        model = usuario_to_model(usuario)
        self._session.add(model)
        return usuario
