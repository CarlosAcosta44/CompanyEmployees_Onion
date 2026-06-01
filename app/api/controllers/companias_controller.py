"""
Controlador de Compañías.
Expone los endpoints REST para gestión de compañías.
"""

import logging
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from app.application.services.compania_service import CompaniaService
from app.application.services.empleado_service import EmpleadoService
from app.application.dtos.compania_dto import (
    CompaniaCreateDTO,
    CompaniaUpdateDTO,
    CompaniaDTO,
    CompaniaConEmpleadosCreateDTO,
    CompaniaConEmpleadosDTO,
)
from app.application.dtos.empleado_dto import EmpleadoDTO
from app.application.dtos.pagination_dto import PaginatedResponse
from app.api.dependencies import get_compania_service, get_empleado_service, check_role

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/companias", tags=["Compañías"])


@router.get("", response_model=PaginatedResponse[CompaniaDTO], dependencies=[Depends(check_role(["ADMIN", "USUARIO"]))])
async def listar_companias(
    pagina: int = Query(1, ge=1),
    tamano: int = Query(10, ge=1, le=100),
    orden: str | None = Query(None),
    dir: str | None = Query(None),
    buscar: str | None = Query(None),
    service: CompaniaService = Depends(get_compania_service)
):
    logger.info("[Controller] GET /api/companias")
    return await service.listar_paginadas(pagina, tamano, orden, dir, buscar)


@router.get("/{compania_id}", response_model=CompaniaDTO, dependencies=[Depends(check_role(["ADMIN", "USUARIO"]))])
async def obtener_compania(compania_id: UUID, service: CompaniaService = Depends(get_compania_service)):
    logger.info("[Controller] GET /api/companias/%s", compania_id)
    return await service.obtener_por_id(compania_id)


@router.get("/{compania_id}/empleados", response_model=PaginatedResponse[EmpleadoDTO], dependencies=[Depends(check_role(["ADMIN", "USUARIO"]))])
async def listar_empleados_de_compania(
    compania_id: UUID,
    pagina: int = Query(1, ge=1),
    tamano: int = Query(10, ge=1, le=100),
    service: EmpleadoService = Depends(get_empleado_service),
):
    logger.info("[Controller] GET /api/companias/%s/empleados", compania_id)
    return await service.listar_paginados(pagina, tamano, compania_id=compania_id)


@router.post("", response_model=CompaniaDTO, status_code=201, dependencies=[Depends(check_role(["ADMIN", "USUARIO"]))])
async def crear_compania(dto: CompaniaCreateDTO, service: CompaniaService = Depends(get_compania_service)):
    logger.info("[Controller] POST /api/companias")
    return await service.crear(dto)


@router.put("/{compania_id}", response_model=CompaniaDTO, dependencies=[Depends(check_role(["ADMIN", "USUARIO"]))])
async def actualizar_compania(compania_id: UUID, dto: CompaniaUpdateDTO, service: CompaniaService = Depends(get_compania_service)):
    logger.info("[Controller] PUT /api/companias/%s", compania_id)
    return await service.actualizar(compania_id, dto)


@router.delete("/{compania_id}", status_code=204, dependencies=[Depends(check_role(["ADMIN"]))])
async def eliminar_compania(compania_id: UUID, service: CompaniaService = Depends(get_compania_service)):
    logger.info("[Controller] DELETE /api/companias/%s", compania_id)
    await service.eliminar(compania_id)


@router.post("/con-empleados", response_model=CompaniaConEmpleadosDTO, status_code=201, dependencies=[Depends(check_role(["ADMIN", "USUARIO"]))])
async def crear_compania_con_empleados(dto: CompaniaConEmpleadosCreateDTO, service: CompaniaService = Depends(get_compania_service)):
    logger.info("[Controller] POST /api/companias/con-empleados")
    return await service.crear_compania_con_empleados(dto)
