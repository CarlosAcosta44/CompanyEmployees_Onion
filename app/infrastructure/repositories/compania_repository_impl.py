"""Implementacion SQLAlchemy del repositorio de companias."""

from uuid import UUID
from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, desc, asc

from app.domain.entities.compania import Compania
from app.domain.interfaces.compania_repository import ICompaniaRepository
from app.infrastructure.database.models import CompaniaModel
from app.infrastructure.repositories.mappers import apply_compania, compania_to_domain, compania_to_model


class CompaniaRepositoryImpl(ICompaniaRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(self) -> Sequence[Compania]:
        result = await self._session.execute(select(CompaniaModel))
        modelos = result.scalars().all()
        return [compania_to_domain(modelo) for modelo in modelos]

    async def get_by_id(self, compania_id: UUID) -> Optional[Compania]:
        modelo = await self._session.get(CompaniaModel, compania_id)
        return compania_to_domain(modelo) if modelo else None

    async def create(self, compania: Compania) -> Compania:
        self._session.add(compania_to_model(compania))
        return compania

    async def update(self, compania: Compania) -> Compania:
        modelo = await self._session.get(CompaniaModel, compania.id)
        if modelo:
            apply_compania(compania, modelo)
        return compania

    async def delete(self, compania_id: UUID) -> None:
        modelo = await self._session.get(CompaniaModel, compania_id)
        if modelo:
            await self._session.delete(modelo)

    async def find_by_condition(
        self,
        *,
        nombre: str | None = None,
        telefono: str | None = None,
    ) -> Sequence[Compania]:
        stmt = select(CompaniaModel)
        if nombre is not None:
            stmt = stmt.where(CompaniaModel.nombre.ilike(f"%{nombre.strip()}%"))
        if telefono is not None:
            stmt = stmt.where(CompaniaModel.telefono == telefono.strip())
        
        result = await self._session.execute(stmt)
        return [compania_to_domain(modelo) for modelo in result.scalars().all()]

    async def get_paged(
        self,
        pagina: int,
        tamano: int,
        orden: str | None = None,
        dir: str | None = None,
        buscar: str | None = None,
    ) -> tuple[Sequence[Compania], int]:
        
        stmt = select(CompaniaModel)
        
        if buscar:
            termino = f"%{buscar.strip()}%"
            stmt = stmt.where(
                or_(
                    CompaniaModel.nombre.ilike(termino),
                    CompaniaModel.direccion.ilike(termino),
                    CompaniaModel.telefono.ilike(termino)
                )
            )
            
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await self._session.scalar(count_stmt) or 0
        
        if orden:
            columna = getattr(CompaniaModel, orden, None)
            if columna is not None:
                if dir and dir.lower() == 'desc':
                    stmt = stmt.order_by(desc(columna))
                else:
                    stmt = stmt.order_by(asc(columna))
                    
        stmt = stmt.offset((pagina - 1) * tamano).limit(tamano)
        result = await self._session.execute(stmt)
        modelos = result.scalars().all()
        
        return [compania_to_domain(m) for m in modelos], total
