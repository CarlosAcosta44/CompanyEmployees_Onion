"""
Interfaz abstracta: IUnitOfWork

Define el contrato del patrón Unit of Work. Actúa como Context Manager
de Python (with statement) coordinando los repositorios y garantizando
que todas las operaciones de una transacción se confirmen o reviertan
de forma atómica.

Equivalente en C#: IUnitOfWork con SaveChanges() y el using pattern.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from types import TracebackType
from typing import Optional, Type

from app.domain.interfaces.compania_repository import ICompaniaRepository
from app.domain.interfaces.empleado_repository import IEmpleadoRepository


class IUnitOfWork(ABC):
    """
    Contrato abstracto del Unit of Work.

    Expone los repositorios como propiedades y obliga a implementar
    commit(), rollback() y los métodos del Context Manager.

    Uso esperado:
        with uow:
            uow.companias.create(compania)
            uow.empleados.create(empleado)
            uow.commit()
    """

    # ------------------------------------------------------------------ #
    #  Repositorios expuestos por el UoW                                   #
    # ------------------------------------------------------------------ #

    @property
    @abstractmethod
    def companias(self) -> ICompaniaRepository:
        """Repositorio de compañías dentro de la transacción activa."""
        ...

    @property
    @abstractmethod
    def empleados(self) -> IEmpleadoRepository:
        """Repositorio de empleados dentro de la transacción activa."""
        ...

    # ------------------------------------------------------------------ #
    #  Control de transacción                                              #
    # ------------------------------------------------------------------ #

    @abstractmethod
    async def commit(self) -> None:
        """
        Confirma todos los cambios pendientes de la transacción actual.
        """
        ...

    @abstractmethod
    async def rollback(self) -> None:
        """
        Deshace todos los cambios pendientes de la transacción actual.
        """
        ...

    # ------------------------------------------------------------------ #
    #  Async Context Manager                                               #
    # ------------------------------------------------------------------ #

    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork":
        """
        Inicia la transacción asíncrona y retorna la instancia del UoW.
        """
        ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> bool:
        """
        Finaliza la transacción asíncrona.
        """
        ...
