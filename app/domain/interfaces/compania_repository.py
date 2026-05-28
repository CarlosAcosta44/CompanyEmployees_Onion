"""
Interfaz abstracta: ICompaniaRepository

Define el contrato de persistencia para la entidad Compania.
Ninguna implementación concreta de base de datos debe conocerse aquí;
este módulo pertenece 100% al núcleo del dominio.
"""

from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, Sequence

from app.domain.entities.compania import Compania


class ICompaniaRepository(ABC):
    """
    Contrato abstracto que deben cumplir todas las implementaciones
    concretas del repositorio de Compania (e.g. SQLAlchemy, en memoria).
    """

    @abstractmethod
    def get_all(self) -> Sequence[Compania]:
        """Retorna todas las compañías registradas."""
        ...

    @abstractmethod
    def get_by_id(self, compania_id: UUID) -> Optional[Compania]:
        """
        Retorna una compañía por su UUID, o None si no existe.

        Args:
            compania_id: Identificador único de la compañía.
        """
        ...

    @abstractmethod
    def create(self, compania: Compania) -> Compania:
        """
        Persiste una nueva compañía en el repositorio.

        Args:
            compania: Instancia de Compania a guardar.

        Returns:
            La misma instancia con los datos persistidos (e.g. id generado).
        """
        ...

    @abstractmethod
    def update(self, compania: Compania) -> Compania:
        """
        Actualiza los datos de una compañía existente.

        Args:
            compania: Instancia de Compania con los campos modificados.

        Returns:
            La instancia actualizada.
        """
        ...

    @abstractmethod
    def delete(self, compania_id: UUID) -> None:
        """
        Elimina una compañía por su UUID.

        Args:
            compania_id: Identificador de la compañía a eliminar.
        """
        ...

    @abstractmethod
    def find_by_condition(
        self,
        *,
        nombre: str | None = None,
        telefono: str | None = None,
    ) -> Sequence[Compania]:
        """Busca compañías que cumplan los filtros indicados (AND)."""
        ...
