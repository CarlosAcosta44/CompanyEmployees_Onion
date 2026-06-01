"""
Dependencias de FastAPI.

La capa API solo consume el composition root; no referencia
implementaciones concretas de infraestructura.
"""

from __future__ import annotations
from fastapi import Depends, Request

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


def get_unit_of_work() -> IUnitOfWork:
    from app.composition_root import build_unit_of_work
    return build_unit_of_work()


def get_compania_service() -> CompaniaService:
    return build_compania_service()


def get_empleado_service() -> EmpleadoService:
    return build_empleado_service()


def get_auth_service() -> AuthService:
    return build_auth_service()


def get_current_user(request: Request) -> dict:
    """Extrae la informacion de usuario cargada por el middleware de autenticacion."""
    user = getattr(request.state, "user", None)
    if not user:
        raise AuthenticationError("El usuario no esta autenticado.")
    return user


def check_role(allowed_roles: list[str]):
    """Retorna una dependencia que restringe el acceso segun roles."""
    def dependency(user: dict = Depends(get_current_user)) -> dict:
        if user.get("rol") not in allowed_roles:
            raise ForbiddenError("No tiene permisos suficientes para realizar esta accion.")
        return user
    return dependency
