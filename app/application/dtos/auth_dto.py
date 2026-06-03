"""
DTOs de Pydantic: Autenticación y Usuarios.
"""

from uuid import UUID
from pydantic import BaseModel, Field, EmailStr


class UsuarioRegisterDTO(BaseModel):
    """Esquema para registrar un nuevo usuario (compatible con el instructor)."""

    firstName: str = Field(..., min_length=1, max_length=100, description="Nombre del usuario.")
    lastName: str = Field(..., min_length=1, max_length=100, description="Apellido del usuario.")
    userName: str = Field(..., min_length=3, max_length=100, description="Nombre de usuario único.")
    password: str = Field(..., min_length=6, max_length=100, description="Contraseña en texto plano.")
    email: EmailStr = Field(..., description="Correo electrónico único.")
    phoneNumber: str = Field("", max_length=30, description="Número de teléfono (opcional).")
    roles: list[str] = Field(default=["USUARIO"], description="Roles del usuario (ADMIN o USUARIO).")
    ciudad: str = Field("", max_length=100, description="Ciudad de residencia del usuario.")
    compania_id: UUID | None = Field(default=None, description="Compañía vinculada si el rol es USUARIO.")


class UsuarioLoginDTO(BaseModel):
    """Esquema para iniciar sesión."""

    userName: str = Field(..., description="Username o Correo del usuario.")
    password: str = Field(..., description="Contraseña en texto plano.")


class TokenDTO(BaseModel):
    """Esquema de respuesta que retorna un token JWT."""

    accessToken: str = Field(..., description="Token de acceso firmado.")
    refreshToken: str = Field(..., description="Token de refresco de sesión.")
    token_type: str = Field("bearer", description="Tipo de token.")


class UsuarioDTO(BaseModel):
    """Esquema de respuesta para los datos de un usuario."""

    id: UUID = Field(..., description="Identificador único del usuario.")
    username: str = Field(..., description="Nombre de usuario.")
    correo: EmailStr = Field(..., description="Correo electrónico.")
    rol: str = Field(..., description="Rol del usuario.")
    first_name: str = Field("", description="Nombre.")
    last_name: str = Field("", description="Apellido.")
    phone_number: str = Field("", description="Teléfono.")
    ciudad: str = Field("", description="Ciudad del usuario.")
    compania_id: UUID | None = Field(default=None, description="Compañía vinculada.")

    model_config = {"from_attributes": True}
