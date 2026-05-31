"""
Implementación concreta del Unit of Work.
Maneja la sesión de SQLAlchemy y coordina los repositorios.
"""

import logging
from types import TracebackType
from collections.abc import Callable
from typing import Optional, Type

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions import ConflictError, PersistenceError
from app.domain.interfaces.unit_of_work import IUnitOfWork
from app.domain.interfaces.compania_repository import ICompaniaRepository
from app.domain.interfaces.empleado_repository import IEmpleadoRepository
from app.infrastructure.database.connection import SessionLocal
from app.infrastructure.repositories.compania_repository_impl import CompaniaRepositoryImpl
from app.infrastructure.repositories.empleado_repository_impl import EmpleadoRepositoryImpl

logger = logging.getLogger(__name__)


class UnitOfWorkImpl(IUnitOfWork):

    def __init__(self, session_factory: Callable[[], AsyncSession] = SessionLocal) -> None:
        self._session_factory = session_factory
        self._committed = False

    async def __aenter__(self) -> "UnitOfWorkImpl":
        self._session = self._session_factory()
        self._companias = CompaniaRepositoryImpl(self._session)
        self._empleados = EmpleadoRepositoryImpl(self._session)
        self._committed = False
        logger.info("[UnitOfWork] Sesión iniciada. Transacción abierta.")
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> bool:
        if exc_type is not None and not self._committed:
            logger.warning("[UnitOfWork] Excepción detectada. Ejecutando Rollback...")
            await self.rollback()
        elif not self._committed:
            logger.info("[UnitOfWork] Sin commit explícito. Cerrando con rollback preventivo.")
            await self.rollback()
        await self._session.close()
        logger.info("[UnitOfWork] Sesión cerrada.")
        return False

    @property
    def companias(self) -> ICompaniaRepository:
        return self._companias

    @property
    def empleados(self) -> IEmpleadoRepository:
        return self._empleados

    async def commit(self) -> None:
        logger.info("[UnitOfWork] Ejecutando Commit...")
        try:
            await self._session.commit()
            self._committed = True
            logger.info("[UnitOfWork] Commit exitoso.")
        except IntegrityError as exc:
            logger.warning("[UnitOfWork] Conflicto de integridad. Ejecutando rollback.")
            await self.rollback()
            raise ConflictError("La operacion viola una restriccion de integridad.") from exc
        except SQLAlchemyError as exc:
            logger.exception("[UnitOfWork] Error de persistencia. Ejecutando rollback.")
            await self.rollback()
            raise PersistenceError("No fue posible persistir los cambios.") from exc

    async def rollback(self) -> None:
        logger.info("[UnitOfWork] Ejecutando Rollback...")
        await self._session.rollback()
        self._committed = False
        logger.info("[UnitOfWork] Rollback completado.")
