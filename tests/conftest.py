"""Configuración global de pytest."""

from __future__ import annotations

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import event
from fastapi.testclient import TestClient

from app.infrastructure.database.models import Base
from app.infrastructure.unit_of_work.unit_of_work_impl import UnitOfWorkImpl
from app.application.services.compania_service import CompaniaService
from app.application.services.empleado_service import EmpleadoService
from app.application.services.auth_service import AuthService
from app.api.main import app
from app.api.dependencies import get_compania_service, get_empleado_service, get_auth_service


_TEST_JWT_PARAMS = {
    "jwt_secret_key": "supersecretkey",
    "jwt_algorithm": "HS256",
    "jwt_access_token_expire_minutes": 60,
}


pytestmark = pytest.mark.anyio


@pytest_asyncio.fixture
async def session_factory():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine.sync_engine, "connect")
    def _enable_fk(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    yield factory

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def uow(session_factory):
    return UnitOfWorkImpl(session_factory)


@pytest_asyncio.fixture
async def compania_service(uow):
    return CompaniaService(uow)


@pytest_asyncio.fixture
async def empleado_service(uow):
    return EmpleadoService(uow)


@pytest.fixture
def test_client(session_factory):
    from jose import jwt
    from datetime import datetime, timedelta, timezone
    from app.infrastructure.config.settings import get_settings

    def _compania_service():
        return CompaniaService(UnitOfWorkImpl(session_factory))

    def _empleado_service():
        return EmpleadoService(UnitOfWorkImpl(session_factory))

    def _auth_service():
        return AuthService(UnitOfWorkImpl(session_factory), **_TEST_JWT_PARAMS)

    app.dependency_overrides[get_compania_service] = _compania_service
    app.dependency_overrides[get_empleado_service] = _empleado_service
    app.dependency_overrides[get_auth_service] = _auth_service

    # Generar token de ADMIN por defecto
    claims = {
        "sub": "00000000-0000-0000-0000-000000000000",
        "username": "testadmin",
        "rol": "ADMIN",
        "compania_id": None,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    settings = get_settings()
    token = jwt.encode(claims, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    with TestClient(app) as client:
        client.headers.update({"Authorization": f"Bearer {token}"})
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def client_usuario(session_factory):
    """Fixture que retorna un creador de clientes autenticados con rol USUARIO."""
    from jose import jwt
    from datetime import datetime, timedelta, timezone
    from app.infrastructure.config.settings import get_settings

    def _crear_client(compania_id=None):
        app.dependency_overrides[get_compania_service] = lambda: CompaniaService(UnitOfWorkImpl(session_factory))
        app.dependency_overrides[get_empleado_service] = lambda: EmpleadoService(UnitOfWorkImpl(session_factory))
        app.dependency_overrides[get_auth_service] = lambda: AuthService(UnitOfWorkImpl(session_factory), **_TEST_JWT_PARAMS)

        claims = {
            "sub": "11111111-1111-1111-1111-111111111111",
            "username": "testuser",
            "rol": "USUARIO",
            "compania_id": str(compania_id) if compania_id else None,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        settings = get_settings()
        token = jwt.encode(claims, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

        client = TestClient(app)
        client.headers.update({"Authorization": f"Bearer {token}"})
        return client

    return _crear_client


@pytest.fixture
def client_invitado(session_factory):
    """Fixture que retorna un cliente no autenticado."""
    app.dependency_overrides[get_compania_service] = lambda: CompaniaService(UnitOfWorkImpl(session_factory))
    app.dependency_overrides[get_empleado_service] = lambda: EmpleadoService(UnitOfWorkImpl(session_factory))

    client = TestClient(app)
    return client