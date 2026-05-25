"""
Implementación concreta del Unit of Work.
Maneja la sesión de SQLAlchemy y coordina los repositorios.
"""

import logging
from types import TracebackType
from typing import Optional, Type

from app.domain.interfaces.unit_of_work import IUnitOfWork
from app.domain.interfaces.compania_repository import ICompaniaRepository
from app.domain.interfaces.empleado_repository import IEmpleadoRepository
from app.infrastructure.database.connection import SessionLocal
from app.infrastructure.repositories.compania_repository_impl import CompaniaRepositoryImpl
from app.infrastructure.repositories.empleado_repository_impl import EmpleadoRepositoryImpl

logger = logging.getLogger(__name__)


class UnitOfWorkImpl(IUnitOfWork):

    def __enter__(self) -> "UnitOfWorkImpl":
        self._session = SessionLocal()
        self._companias = CompaniaRepositoryImpl(self._session)
        self._empleados = EmpleadoRepositoryImpl(self._session)
        logger.info("[UnitOfWork] Sesión iniciada. Transacción abierta.")
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> bool:
        if exc_type is not None:
            logger.warning("[UnitOfWork] Excepción detectada. Ejecutando Rollback...")
            self.rollback()
        self._session.close()
        logger.info("[UnitOfWork] Sesión cerrada.")
        return False

    @property
    def companias(self) -> ICompaniaRepository:
        return self._companias

    @property
    def empleados(self) -> IEmpleadoRepository:
        return self._empleados

    def commit(self) -> None:
        logger.info("[UnitOfWork] Ejecutando Commit...")
        self._session.commit()
        logger.info("[UnitOfWork] Commit exitoso.")

    def rollback(self) -> None:
        logger.info("[UnitOfWork] Ejecutando Rollback...")
        self._session.rollback()
        logger.info("[UnitOfWork] Rollback completado.")

    def flush(self) -> None:
        self._session.flush()