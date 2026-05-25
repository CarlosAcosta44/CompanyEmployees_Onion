"""
Controlador de Compañías.
Expone los endpoints REST para gestión de compañías.
"""

import logging
from uuid import UUID
from fastapi import APIRouter, Depends
from app.application.services.compania_service import CompaniaService
from app.application.dtos.compania_dto import (
    CompaniaCreateDTO,
    CompaniaUpdateDTO,
    CompaniaDTO,
    CompaniaConEmpleadosCreateDTO,
    CompaniaConEmpleadosDTO,
)
from app.api.dependencies import get_compania_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/companias", tags=["Compañías"])


@router.get("", response_model=list[CompaniaDTO])
def listar_companias(service: CompaniaService = Depends(get_compania_service)):
    logger.info("[Controller] GET /api/companias")
    return service.listar_todas()


@router.get("/{compania_id}", response_model=CompaniaDTO)
def obtener_compania(compania_id: UUID, service: CompaniaService = Depends(get_compania_service)):
    logger.info("[Controller] GET /api/companias/%s", compania_id)
    return service.obtener_por_id(compania_id)


@router.post("", response_model=CompaniaDTO, status_code=201)
def crear_compania(dto: CompaniaCreateDTO, service: CompaniaService = Depends(get_compania_service)):
    logger.info("[Controller] POST /api/companias")
    return service.crear(dto)


@router.put("/{compania_id}", response_model=CompaniaDTO)
def actualizar_compania(compania_id: UUID, dto: CompaniaUpdateDTO, service: CompaniaService = Depends(get_compania_service)):
    logger.info("[Controller] PUT /api/companias/%s", compania_id)
    return service.actualizar(compania_id, dto)


@router.delete("/{compania_id}", status_code=204)
def eliminar_compania(compania_id: UUID, service: CompaniaService = Depends(get_compania_service)):
    logger.info("[Controller] DELETE /api/companias/%s", compania_id)
    service.eliminar(compania_id)


@router.post("/con-empleados", response_model=CompaniaConEmpleadosDTO, status_code=201)
def crear_compania_con_empleados(dto: CompaniaConEmpleadosCreateDTO, service: CompaniaService = Depends(get_compania_service)):
    logger.info("[Controller] POST /api/companias/con-empleados")
    return service.crear_compania_con_empleados(dto)