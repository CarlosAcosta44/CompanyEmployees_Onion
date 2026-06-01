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
from app.api.main import app
from app.api.dependencies import get_compania_service, get_empleado_service


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
    def _compania_service():
        return CompaniaService(UnitOfWorkImpl(session_factory))

    def _empleado_service():
        return EmpleadoService(UnitOfWorkImpl(session_factory))

    app.dependency_overrides[get_compania_service] = _compania_service
    app.dependency_overrides[get_empleado_service] = _empleado_service

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()