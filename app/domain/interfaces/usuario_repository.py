"""
Interfaz abstracta: IUsuarioRepository

Define el contrato de persistencia para la entidad Usuario.
Pertenece al núcleo del dominio de Onion Architecture.
"""

from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional
from app.domain.entities.usuario import Usuario


class IUsuarioRepository(ABC):
    """Contrato que deben cumplir todos los repositorios concretos para Usuario."""

    @abstractmethod
    async def get_by_id(self, usuario_id: UUID) -> Optional[Usuario]:
        """Busca un usuario por su identificador único."""
        ...

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[Usuario]:
        """Busca un usuario por su nombre de usuario (username)."""
        ...

    @abstractmethod
    async def get_by_correo(self, correo: str) -> Optional[Usuario]:
        """Busca un usuario por su correo electrónico."""
        ...

    @abstractmethod
    async def create(self, usuario: Usuario) -> Usuario:
        """Registra un nuevo usuario en la base de datos."""
        ...
