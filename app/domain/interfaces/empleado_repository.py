"""
Interfaz abstracta: IEmpleadoRepository

Define el contrato de persistencia para la entidad Empleado.
Incluye el método especializado get_by_compania para consultas filtradas
por compañía, requerido por los casos de uso del negocio.
"""

from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, Sequence

from app.domain.entities.empleado import Empleado


class IEmpleadoRepository(ABC):
    """
    Contrato abstracto que deben cumplir todas las implementaciones
    concretas del repositorio de Empleado (e.g. SQLAlchemy, en memoria).
    """

    @abstractmethod
    def get_all(self) -> Sequence[Empleado]:
        """Retorna todos los empleados registrados en el sistema."""
        ...

    @abstractmethod
    def get_by_id(self, empleado_id: UUID) -> Optional[Empleado]:
        """
        Retorna un empleado por su UUID, o None si no existe.

        Args:
            empleado_id: Identificador único del empleado.
        """
        ...

    @abstractmethod
    def get_by_compania(self, compania_id: UUID) -> Sequence[Empleado]:
        """
        Retorna todos los empleados que pertenecen a una compañía.

        Args:
            compania_id: Identificador único de la compañía.

        Returns:
            Lista (posiblemente vacía) de empleados de esa compañía.
        """
        ...

    @abstractmethod
    def create(self, empleado: Empleado) -> Empleado:
        """
        Persiste un nuevo empleado en el repositorio.

        Args:
            empleado: Instancia de Empleado a guardar.

        Returns:
            La misma instancia con los datos persistidos.
        """
        ...

    @abstractmethod
    def update(self, empleado: Empleado) -> Empleado:
        """
        Actualiza los datos de un empleado existente.

        Args:
            empleado: Instancia de Empleado con los campos modificados.

        Returns:
            La instancia actualizada.
        """
        ...

    @abstractmethod
    def delete(self, empleado_id: UUID) -> None:
        """
        Elimina un empleado por su UUID.

        Args:
            empleado_id: Identificador del empleado a eliminar.
        """
        ...
