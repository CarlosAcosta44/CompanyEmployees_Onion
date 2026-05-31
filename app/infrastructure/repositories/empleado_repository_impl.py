"""Implementacion SQLAlchemy del repositorio de empleados."""

from uuid import UUID
from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, desc, asc, delete

from app.domain.entities.empleado import Empleado
from app.domain.interfaces.empleado_repository import IEmpleadoRepository
from app.infrastructure.database.models import EmpleadoModel
from app.infrastructure.repositories.mappers import apply_empleado, empleado_to_domain, empleado_to_model


class EmpleadoRepositoryImpl(IEmpleadoRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(self) -> Sequence[Empleado]:
        result = await self._session.execute(select(EmpleadoModel))
        return [empleado_to_domain(modelo) for modelo in result.scalars().all()]

    async def get_by_id(self, empleado_id: UUID) -> Optional[Empleado]:
        modelo = await self._session.get(EmpleadoModel, empleado_id)
        return empleado_to_domain(modelo) if modelo else None

    async def get_by_correo(self, correo: str) -> Optional[Empleado]:
        stmt = select(EmpleadoModel).where(EmpleadoModel.correo == correo.strip().lower())
        result = await self._session.execute(stmt)
        modelo = result.scalars().first()
        return empleado_to_domain(modelo) if modelo else None

    async def get_by_compania(self, compania_id: UUID) -> Sequence[Empleado]:
        stmt = select(EmpleadoModel).where(EmpleadoModel.compania_id == compania_id)
        result = await self._session.execute(stmt)
        return [empleado_to_domain(modelo) for modelo in result.scalars().all()]

    async def create(self, empleado: Empleado) -> Empleado:
        self._session.add(empleado_to_model(empleado))
        return empleado

    async def update(self, empleado: Empleado) -> Empleado:
        modelo = await self._session.get(EmpleadoModel, empleado.id)
        if modelo:
            apply_empleado(empleado, modelo)
        return empleado

    async def delete(self, empleado_id: UUID) -> None:
        modelo = await self._session.get(EmpleadoModel, empleado_id)
        if modelo:
            await self._session.delete(modelo)

    async def find_by_condition(
        self,
        *,
        compania_id: UUID | None = None,
        correo: str | None = None,
        cargo: str | None = None,
    ) -> Sequence[Empleado]:
        stmt = select(EmpleadoModel)
        if compania_id is not None:
            stmt = stmt.where(EmpleadoModel.compania_id == compania_id)
        if correo is not None:
            stmt = stmt.where(EmpleadoModel.correo == correo.strip().lower())
        if cargo is not None:
            stmt = stmt.where(EmpleadoModel.cargo.ilike(f"%{cargo.strip()}%"))
            
        result = await self._session.execute(stmt)
        return [empleado_to_domain(modelo) for modelo in result.scalars().all()]

    async def create_range(self, empleados: Sequence[Empleado]) -> Sequence[Empleado]:
        modelos = [empleado_to_model(emp) for emp in empleados]
        self._session.add_all(modelos)
        return empleados

    async def delete_range(self, empleado_ids: Sequence[UUID]) -> None:
        stmt = delete(EmpleadoModel).where(EmpleadoModel.id.in_(empleado_ids))
        await self._session.execute(stmt)

    async def get_paged(
        self,
        pagina: int,
        tamano: int,
        orden: str | None = None,
        dir: str | None = None,
        buscar: str | None = None,
        compania_id: UUID | None = None,
    ) -> tuple[Sequence[Empleado], int]:
        
        stmt = select(EmpleadoModel)
        
        if compania_id is not None:
            stmt = stmt.where(EmpleadoModel.compania_id == compania_id)
            
        if buscar:
            termino = f"%{buscar.strip()}%"
            stmt = stmt.where(
                or_(
                    EmpleadoModel.nombre.ilike(termino),
                    EmpleadoModel.apellido.ilike(termino),
                    EmpleadoModel.correo.ilike(termino)
                )
            )
            
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await self._session.scalar(count_stmt) or 0
        
        if orden:
            columna = getattr(EmpleadoModel, orden, None)
            if columna is not None:
                if dir and dir.lower() == 'desc':
                    stmt = stmt.order_by(desc(columna))
                else:
                    stmt = stmt.order_by(asc(columna))
                    
        stmt = stmt.offset((pagina - 1) * tamano).limit(tamano)
        result = await self._session.execute(stmt)
        modelos = result.scalars().all()
        
        return [empleado_to_domain(m) for m in modelos], total

    async def patch_partial(self, empleado_id: UUID, cambios: dict) -> Optional[Empleado]:
        modelo = await self._session.get(EmpleadoModel, empleado_id)
        if not modelo:
            return None
            
        for key, value in cambios.items():
            if hasattr(modelo, key) and key != 'id':
                setattr(modelo, key, value)
                
        return empleado_to_domain(modelo)
