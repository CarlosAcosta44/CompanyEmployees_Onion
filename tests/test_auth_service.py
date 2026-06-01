"""Pruebas unitarias de AuthService."""

from __future__ import annotations
import pytest
from uuid import uuid4

from app.application.services.auth_service import AuthService
from app.application.dtos.auth_dto import UsuarioRegisterDTO, UsuarioLoginDTO
from app.domain.exceptions import ConflictError, AuthenticationError, EntityNotFoundError

pytestmark = pytest.mark.anyio


JWT_PARAMS = {
    "jwt_secret_key": "test-secret-key",
    "jwt_algorithm": "HS256",
    "jwt_access_token_expire_minutes": 60,
}


def make_service(uow) -> AuthService:
    return AuthService(uow, **JWT_PARAMS)


async def test_registro_usuario_exitoso(uow):
    auth_service = make_service(uow)
    dto = UsuarioRegisterDTO(
        username="nuevousuario",
        correo="nuevo@correo.com",
        password="password123",
        rol="USUARIO",
    )

    result = await auth_service.registrar(dto)

    assert result.id is not None
    assert result.username == "nuevousuario"
    assert result.correo == "nuevo@correo.com"
    assert result.rol == "USUARIO"
    assert result.compania_id is None


async def test_registro_usuario_duplicado_username_lanza_conflict(uow):
    auth_service = make_service(uow)
    dto1 = UsuarioRegisterDTO(
        username="repetido",
        correo="uno@correo.com",
        password="password123",
        rol="USUARIO",
    )
    dto2 = UsuarioRegisterDTO(
        username="repetido",
        correo="dos@correo.com",
        password="password123",
        rol="USUARIO",
    )

    await auth_service.registrar(dto1)

    with pytest.raises(ConflictError) as exc:
        await auth_service.registrar(dto2)
    assert "nombre de usuario 'repetido' ya está en uso" in str(exc.value)


async def test_registro_usuario_duplicado_correo_lanza_conflict(uow):
    auth_service = make_service(uow)
    dto1 = UsuarioRegisterDTO(
        username="userone",
        correo="mismo@correo.com",
        password="password123",
        rol="USUARIO",
    )
    dto2 = UsuarioRegisterDTO(
        username="usertwo",
        correo="mismo@correo.com",
        password="password123",
        rol="USUARIO",
    )

    await auth_service.registrar(dto1)

    with pytest.raises(ConflictError) as exc:
        await auth_service.registrar(dto2)
    assert "correo electrónico 'mismo@correo.com' ya está registrado" in str(exc.value)


async def test_login_exitoso_retorna_token(uow):
    auth_service = make_service(uow)
    # Registrar
    await auth_service.registrar(UsuarioRegisterDTO(
        username="loginuser",
        correo="login@correo.com",
        password="secretpassword",
        rol="ADMIN",
    ))

    # Login
    login_dto = UsuarioLoginDTO(
        correo="login@correo.com",
        password="secretpassword",
    )
    token_dto = await auth_service.login(login_dto)

    assert token_dto.access_token is not None
    assert token_dto.token_type == "bearer"


async def test_login_password_incorrecta_lanza_unauthorized(uow):
    auth_service = make_service(uow)
    await auth_service.registrar(UsuarioRegisterDTO(
        username="loginuser2",
        correo="login2@correo.com",
        password="secretpassword",
        rol="USUARIO",
    ))

    login_dto = UsuarioLoginDTO(
        correo="login2@correo.com",
        password="wrongpassword",
    )

    with pytest.raises(AuthenticationError) as exc:
        await auth_service.login(login_dto)
    assert "Credenciales de acceso incorrectas" in str(exc.value)


async def test_login_correo_inexistente_lanza_unauthorized(uow):
    auth_service = make_service(uow)
    login_dto = UsuarioLoginDTO(
        correo="noexiste@correo.com",
        password="secretpassword",
    )

    with pytest.raises(AuthenticationError) as exc:
        await auth_service.login(login_dto)
    assert "Credenciales de acceso incorrectas" in str(exc.value)


async def test_obtener_perfil_exitoso(uow):
    auth_service = make_service(uow)
    creado = await auth_service.registrar(UsuarioRegisterDTO(
        username="perfiluser",
        correo="perfil@correo.com",
        password="secretpassword",
        rol="USUARIO",
    ))

    perfil = await auth_service.obtener_perfil(str(creado.id))

    assert perfil.id == creado.id
    assert perfil.username == "perfiluser"
    assert perfil.correo == "perfil@correo.com"


async def test_obtener_perfil_inexistente_lanza_not_found(uow):
    auth_service = make_service(uow)
    with pytest.raises(EntityNotFoundError) as exc:
        await auth_service.obtener_perfil(str(uuid4()))
    assert "El usuario no existe" in str(exc.value)
