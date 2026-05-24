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
    def commit(self) -> None:
        """
        Confirma todos los cambios pendientes de la transacción actual.
        Equivalente a SaveChanges() en Entity Framework Core.
        """
        ...

    @abstractmethod
    def rollback(self) -> None:
        """
        Deshace todos los cambios pendientes de la transacción actual.
        Se invoca automáticamente por __exit__ cuando ocurre una excepción.
        """
        ...

    # ------------------------------------------------------------------ #
    #  Context Manager                                                     #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def __enter__(self) -> "IUnitOfWork":
        """
        Inicia la transacción y retorna la instancia del UoW.

        Returns:
            Self, listo para usar dentro del bloque with.
        """
        ...

    @abstractmethod
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> bool:
        """
        Finaliza la transacción.

        Si se produjo una excepción, ejecuta rollback() automáticamente
        y deja que la excepción se propague (retorna False).
        En caso de éxito cierra los recursos (sesión de BD).

        Args:
            exc_type: Tipo de excepción capturada, o None si no hubo error.
            exc_val:  Instancia de la excepción, o None.
            exc_tb:   Traceback de la excepción, o None.

        Returns:
            False para no suprimir la excepción.
        """
        ...
