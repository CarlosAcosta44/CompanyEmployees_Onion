"""
Paquete: app.application.dtos

Exporta todos los Data Transfer Objects (DTOs) de la capa de aplicación.
Los DTOs son esquemas Pydantic que validan y desacoplan la entrada/salida
de la API del modelo de dominio interno.
"""

from app.application.dtos.empleado_dto import (
    EmpleadoDTO,
    EmpleadoCreateDTO,
    EmpleadoCreateAnidadoDTO,
    EmpleadoUpdateDTO,
)
from app.application.dtos.compania_dto import (
    CompaniaDTO,
    CompaniaCreateDTO,
    CompaniaUpdateDTO,
    CompaniaConEmpleadosCreateDTO,
    CompaniaConEmpleadosDTO,
)
from app.application.dtos.pagination_dto import PaginatedResponse
from app.application.dtos.auth_dto import (
    UsuarioRegisterDTO,
    UsuarioLoginDTO,
    TokenDTO,
    UsuarioDTO,
)

__all__ = [
    # Empleado
    "EmpleadoDTO",
    "EmpleadoCreateDTO",
    "EmpleadoCreateAnidadoDTO",
    "EmpleadoUpdateDTO",
    # Compania
    "CompaniaDTO",
    "CompaniaCreateDTO",
    "CompaniaUpdateDTO",
    "CompaniaConEmpleadosCreateDTO",
    "CompaniaConEmpleadosDTO",
    # Genéricos
    "PaginatedResponse",
    # Seguridad
    "UsuarioRegisterDTO",
    "UsuarioLoginDTO",
    "TokenDTO",
    "UsuarioDTO",
]
