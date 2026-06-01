"""Pruebas del caso transaccional exigido por la actividad."""

from __future__ import annotations

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import event

from app.application.dtos.compania_dto import CompaniaConEmpleadosCreateDTO
from app.application.services.compania_service import CompaniaService
from app.domain.exceptions import ConflictError
from app.infrastructure.database.models import Base
from app.infrastructure.unit_of_work.unit_of_work_impl import UnitOfWorkImpl


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


async def test_crear_compania_con_empleados_hace_rollback_completo_si_un_correo_ya_existe(session_factory) -> None:
    service = CompaniaService(UnitOfWorkImpl(session_factory))

    # Primera creación exitosa
    await service.crear_compania_con_empleados(
        CompaniaConEmpleadosCreateDTO(
            nombre="TechCorp SAS",
            direccion="Calle 10 # 5-20",
            telefono="3001234567",
            empleados=[
                {
                    "nombre": "Ana",
                    "apellido": "Martinez",
                    "correo": "ana.martinez@techcorp.com",
                    "cargo": "QA Engineer",
                    "salario": "3800000.00",
                }
            ],
        )
    )

    # Segunda creación debe fallar por correo duplicado -> rollback
    with pytest.raises(ConflictError):
        await service.crear_compania_con_empleados(
            CompaniaConEmpleadosCreateDTO(
                nombre="Otra Compania",
                direccion="Carrera 20 # 10-30",
                telefono="3109998888",
                empleados=[
                    {
                        "nombre": "Ana",
                        "apellido": "Duplicada",
                        "correo": "ana.martinez@techcorp.com",
                        "cargo": "Backend",
                        "salario": "4500000.00",
                    }
                ],
            )
        )

    # Verificar rollback: solo debe haber 1 compañía y 1 empleado
    async with UnitOfWorkImpl(session_factory) as uow:
        companias = await uow.companias.get_all()
        empleados = await uow.empleados.get_all()
        assert len(companias) == 1
        assert len(empleados) == 1