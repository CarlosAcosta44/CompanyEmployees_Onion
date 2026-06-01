"""Pruebas unitarias del EmpleadoService."""

from __future__ import annotations

import pytest
from decimal import Decimal
from uuid import uuid4

from app.application.dtos.compania_dto import CompaniaCreateDTO
from app.application.dtos.empleado_dto import EmpleadoCreateDTO, EmpleadoUpdateDTO
from app.domain.exceptions import EntityNotFoundError, ConflictError


pytestmark = pytest.mark.anyio


COMPANIA_DTO = CompaniaCreateDTO(
    nombre="TechCorp SAS",
    direccion="Calle 10 # 5-20",
    telefono="3001234567",
)

def make_empleado_dto(compania_id, correo="ana@techcorp.com"):
    return EmpleadoCreateDTO(
        nombre="Ana",
        apellido="Martinez",
        correo=correo,
        cargo="QA Engineer",
        salario=Decimal("3800000.00"),
        compania_id=compania_id,
    )


async def test_listar_todos_retorna_lista_vacia(empleado_service):
    resultado = await empleado_service.listar_todos()
    assert resultado == []


async def test_crear_empleado_exitosamente(compania_service, empleado_service):
    compania = await compania_service.crear(COMPANIA_DTO)
    creado = await empleado_service.crear(make_empleado_dto(compania.id))
    assert creado.id is not None
    assert creado.nombre == "Ana"
    assert creado.correo == "ana@techcorp.com"


async def test_crear_empleado_falla_si_compania_no_existe(empleado_service):
    with pytest.raises(EntityNotFoundError):
        await empleado_service.crear(make_empleado_dto(uuid4()))


async def test_crear_empleado_falla_si_correo_duplicado(compania_service, empleado_service):
    compania = await compania_service.crear(COMPANIA_DTO)
    await empleado_service.crear(make_empleado_dto(compania.id))
    with pytest.raises(ConflictError):
        await empleado_service.crear(make_empleado_dto(compania.id))


async def test_actualizar_empleado_cambia_cargo(compania_service, empleado_service):
    compania = await compania_service.crear(COMPANIA_DTO)
    creado = await empleado_service.crear(make_empleado_dto(compania.id))
    actualizado = await empleado_service.actualizar(
        creado.id,
        EmpleadoUpdateDTO(cargo="Tech Lead"),
    )
    assert actualizado.cargo == "Tech Lead"


async def test_eliminar_empleado_exitosamente(compania_service, empleado_service):
    compania = await compania_service.crear(COMPANIA_DTO)
    creado = await empleado_service.crear(make_empleado_dto(compania.id))
    await empleado_service.eliminar(creado.id)
    with pytest.raises(EntityNotFoundError):
        await empleado_service.obtener_por_id(creado.id)