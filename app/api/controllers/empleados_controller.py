"""
Controlador de Empleados.
Expone los endpoints REST para gestión de empleados.
"""

import logging
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Body
from app.application.services.empleado_service import EmpleadoService
from app.application.dtos.empleado_dto import EmpleadoDTO, EmpleadoCreateDTO, EmpleadoUpdateDTO
from app.application.dtos.pagination_dto import PaginatedResponse
from app.api.dependencies import get_empleado_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/empleados", tags=["Empleados"])


@router.get("", response_model=PaginatedResponse[EmpleadoDTO])
async def listar_empleados(
    pagina: int = Query(1, ge=1, description="Número de página"),
    tamano: int = Query(10, ge=1, le=100, description="Tamaño de la página"),
    orden: str | None = Query(None, description="Campo a ordenar"),
    dir: str | None = Query(None, description="asc o desc"),
    buscar: str | None = Query(None, description="Término de búsqueda"),
    service: EmpleadoService = Depends(get_empleado_service)
):
    logger.info("[Controller] GET /api/empleados")
    return await service.listar_paginados(pagina, tamano, orden, dir, buscar)


@router.get("/{empleado_id}", response_model=EmpleadoDTO)
async def obtener_empleado(empleado_id: UUID, service: EmpleadoService = Depends(get_empleado_service)):
    logger.info("[Controller] GET /api/empleados/%s", empleado_id)
    return await service.obtener_por_id(empleado_id)


@router.get("/compania/{compania_id}", response_model=PaginatedResponse[EmpleadoDTO])
async def listar_empleados_por_compania(
    compania_id: UUID,
    pagina: int = Query(1, ge=1),
    tamano: int = Query(10, ge=1, le=100),
    service: EmpleadoService = Depends(get_empleado_service)
):
    logger.info("[Controller] GET /api/empleados/compania/%s", compania_id)
    return await service.listar_paginados(pagina, tamano, compania_id=compania_id)


@router.post("", response_model=EmpleadoDTO, status_code=201)
async def crear_empleado(dto: EmpleadoCreateDTO, service: EmpleadoService = Depends(get_empleado_service)):
    logger.info("[Controller] POST /api/empleados")
    return await service.crear(dto)


@router.post("/lote", response_model=list[EmpleadoDTO], status_code=201)
async def crear_empleados_lote(dtos: list[EmpleadoCreateDTO] = Body(...), service: EmpleadoService = Depends(get_empleado_service)):
    logger.info("[Controller] POST /api/empleados/lote")
    return await service.crear_en_lote(dtos)


@router.put("/{empleado_id}", response_model=EmpleadoDTO)
async def actualizar_empleado(empleado_id: UUID, dto: EmpleadoUpdateDTO, service: EmpleadoService = Depends(get_empleado_service)):
    logger.info("[Controller] PUT /api/empleados/%s", empleado_id)
    return await service.actualizar(empleado_id, dto)


@router.patch("/{empleado_id}", response_model=EmpleadoDTO)
async def actualizar_empleado_parcial(empleado_id: UUID, dto: EmpleadoUpdateDTO, service: EmpleadoService = Depends(get_empleado_service)):
    logger.info("[Controller] PATCH /api/empleados/%s", empleado_id)
    return await service.actualizar_parcial(empleado_id, dto)


@router.delete("/lote", status_code=204)
async def eliminar_empleados_lote(empleado_ids: list[UUID] = Body(...), service: EmpleadoService = Depends(get_empleado_service)):
    logger.info("[Controller] DELETE /api/empleados/lote")
    await service.eliminar_en_lote(empleado_ids)


@router.delete("/{empleado_id}", status_code=204)
async def eliminar_empleado(empleado_id: UUID, service: EmpleadoService = Depends(get_empleado_service)):
    logger.info("[Controller] DELETE /api/empleados/%s", empleado_id)
    await service.eliminar(empleado_id)