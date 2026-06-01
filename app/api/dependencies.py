"""
Dependencias de FastAPI.

La capa API solo consume el composition root; no referencia
implementaciones concretas de infraestructura.
"""

from __future__ import annotations
from uuid import UUID
from fastapi import Depends, Request, Body
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

from app.application.services.compania_service import CompaniaService
from app.application.services.empleado_service import EmpleadoService
from app.application.services.auth_service import AuthService
from app.composition_root import (
    build_compania_service,
    build_empleado_service,
    build_auth_service,
)
from app.domain.interfaces.unit_of_work import IUnitOfWork
from app.domain.exceptions import AuthenticationError, ForbiddenError
from app.application.dtos.empleado_dto import EmpleadoCreateDTO


def get_unit_of_work() -> IUnitOfWork:
    from app.composition_root import build_unit_of_work

    return build_unit_of_work()


def get_compania_service() -> CompaniaService:
    return build_compania_service()


def get_empleado_service() -> EmpleadoService:
    return build_empleado_service()


def get_auth_service() -> AuthService:
    return build_auth_service()


def get_current_user(request: Request, token: str = Depends(oauth2_scheme)) -> dict:
    """Extrae la información de usuario cargada por el middleware de autenticación."""
    user = getattr(request.state, "user", None)
    if not user:
        raise AuthenticationError("El usuario no está autenticado.")
    return user


def check_role(allowed_roles: list[str]):
    """Retorna una dependencia que restringe el acceso según roles."""
    def dependency(user: dict = Depends(get_current_user)) -> dict:
        if user.get("rol") not in allowed_roles:
            raise ForbiddenError("No tiene permisos suficientes para realizar esta acción.")
        return user
    return dependency


# =============================================================================
#  Políticas de Autorización Compuestas (Módulo 6)
# =============================================================================

async def verificar_propietario_crear_empleado(
    dto: EmpleadoCreateDTO,
    user: dict = Depends(check_role(["ADMIN", "USUARIO"])),
) -> dict:
    """Valida que un USUARIO solo cree empleados para su propia compañía."""
    if user.get("rol") == "ADMIN":
        return user

    user_compania_id = user.get("compania_id")
    if not user_compania_id or str(dto.compania_id) != str(user_compania_id):
        raise ForbiddenError("Un usuario de rol USUARIO solo puede crear empleados para su propia compañía.")

    return user


async def verificar_propietario_crear_empleados_lote(
    dtos: list[EmpleadoCreateDTO] = Body(...),
    user: dict = Depends(check_role(["ADMIN", "USUARIO"])),
) -> dict:
    """Valida que un USUARIO cree empleados en lote solo para su propia compañía."""
    if user.get("rol") == "ADMIN":
        return user

    user_compania_id = user.get("compania_id")
    if not user_compania_id:
        raise ForbiddenError("El usuario no está asociado a ninguna compañía.")

    for dto in dtos:
        if str(dto.compania_id) != str(user_compania_id):
            raise ForbiddenError("Un usuario de rol USUARIO solo puede crear empleados para su propia compañía.")

    return user


async def verificar_propietario_modificar_empleado(
    empleado_id: UUID,
    user: dict = Depends(check_role(["ADMIN", "USUARIO"])),
    service: EmpleadoService = Depends(get_empleado_service),
) -> dict:
    """Valida que un USUARIO solo modifique empleados de su propia compañía."""
    if user.get("rol") == "ADMIN":
        return user

    user_compania_id = user.get("compania_id")
    if not user_compania_id:
        raise ForbiddenError("El usuario no está asociado a ninguna compañía.")

    empleado = await service.obtener_por_id(empleado_id)
    if str(empleado.compania_id) != str(user_compania_id):
        raise ForbiddenError("Un usuario de rol USUARIO solo puede modificar empleados de su propia compañía.")

    return user
