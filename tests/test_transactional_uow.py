"""Pruebas del caso transaccional exigido por la actividad."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.application.dtos.compania_dto import CompaniaConEmpleadosCreateDTO
from app.application.services.compania_service import CompaniaService
from app.domain.exceptions import ConflictError
from app.infrastructure.database.models import Base
from app.infrastructure.unit_of_work.unit_of_work_impl import UnitOfWorkImpl


@pytest.fixture
def session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


def test_crear_compania_con_empleados_hace_rollback_completo_si_un_correo_ya_existe(session_factory) -> None:
    service = CompaniaService(UnitOfWorkImpl(session_factory))

    service.crear_compania_con_empleados(
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

    with pytest.raises(ConflictError):
        service.crear_compania_con_empleados(
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

    with UnitOfWorkImpl(session_factory) as uow:
        assert len(uow.companias.get_all()) == 1
        assert len(uow.empleados.get_all()) == 1
