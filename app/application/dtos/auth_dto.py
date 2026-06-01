"""
DTOs de Pydantic: Autenticación y Usuarios.
"""

from uuid import UUID
from pydantic import BaseModel, Field, EmailStr


class UsuarioRegisterDTO(BaseModel):
    """Esquema para registrar un nuevo usuario."""

    username: str = Field(..., min_length=3, max_length=100, description="Nombre de usuario único.")
    correo: EmailStr = Field(..., description="Correo electrónico único.")
    password: str = Field(..., min_length=6, max_length=100, description="Contraseña en texto plano.")
    rol: str = Field("USUARIO", pattern="^(ADMIN|USUARIO)$", description="Rol del usuario (ADMIN o USUARIO).")
    compania_id: UUID | None = Field(default=None, description="Compañía vinculada si el rol es USUARIO.")


class UsuarioLoginDTO(BaseModel):
    """Esquema para iniciar sesión."""

    correo: EmailStr = Field(..., description="Correo electrónico del usuario.")
    password: str = Field(..., description="Contraseña en texto plano.")


class TokenDTO(BaseModel):
    """Esquema de respuesta que retorna un token JWT."""

    access_token: str = Field(..., description="Token de acceso firmado.")
    token_type: str = Field("bearer", description="Tipo de token.")


class UsuarioDTO(BaseModel):
    """Esquema de respuesta para los datos de un usuario."""

    id: UUID = Field(..., description="Identificador único del usuario.")
    username: str = Field(..., description="Nombre de usuario.")
    correo: EmailStr = Field(..., description="Correo electrónico.")
    rol: str = Field(..., description="Rol del usuario.")
    compania_id: UUID | None = Field(default=None, description="Compañía vinculada.")

    model_config = {"from_attributes": True}
