"""Pruebas unitarias del CompaniaService."""

from __future__ import annotations

import pytest
from uuid import uuid4

from app.application.dtos.compania_dto import CompaniaCreateDTO, CompaniaUpdateDTO
from app.domain.exceptions import EntityNotFoundError


pytestmark = pytest.mark.anyio


COMPANIA_DTO = CompaniaCreateDTO(
    nombre="TechCorp SAS",
    direccion="Calle 10 # 5-20",
    telefono="3001234567",
)


async def test_listar_todas_retorna_lista_vacia_inicialmente(compania_service):
    resultado = await compania_service.listar_todas()
    assert resultado == []


async def test_crear_compania_genera_id_y_persiste(compania_service):
    creada = await compania_service.crear(COMPANIA_DTO)
    assert creada.id is not None
    assert creada.nombre == "TechCorp SAS"
    assert creada.telefono == "3001234567"


async def test_obtener_por_id_retorna_compania_existente(compania_service):
    creada = await compania_service.crear(COMPANIA_DTO)
    resultado = await compania_service.obtener_por_id(creada.id)
    assert resultado.id == creada.id
    assert resultado.nombre == "TechCorp SAS"


async def test_obtener_por_id_lanza_error_si_no_existe(compania_service):
    with pytest.raises(EntityNotFoundError):
        await compania_service.obtener_por_id(uuid4())


async def test_actualizar_compania_modifica_nombre(compania_service):
    creada = await compania_service.crear(COMPANIA_DTO)
    actualizada = await compania_service.actualizar(
        creada.id,
        CompaniaUpdateDTO(nombre="TechCorp Colombia SAS"),
    )
    assert actualizada.nombre == "TechCorp Colombia SAS"


async def test_eliminar_compania_la_remueve(compania_service):
    creada = await compania_service.crear(COMPANIA_DTO)
    await compania_service.eliminar(creada.id)
    with pytest.raises(EntityNotFoundError):
        await compania_service.obtener_por_id(creada.id)