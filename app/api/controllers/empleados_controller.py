"""
Controlador de Empleados.
Expone los endpoints REST para gestión de empleados.
"""

import logging
from uuid import UUID
from fastapi import APIRouter, Depends
from app.application.services.empleado_service import EmpleadoService
from app.application.dtos.empleado_dto import EmpleadoDTO, EmpleadoCreateDTO, EmpleadoUpdateDTO
from app.api.dependencies import get_empleado_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/empleados", tags=["Empleados"])


@router.get("", response_model=list[EmpleadoDTO])
def listar_empleados(service: EmpleadoService = Depends(get_empleado_service)):
    logger.info("[Controller] GET /api/empleados")
    return service.listar_todos()


@router.get("/{empleado_id}", response_model=EmpleadoDTO)
def obtener_empleado(empleado_id: UUID, service: EmpleadoService = Depends(get_empleado_service)):
    logger.info("[Controller] GET /api/empleados/%s", empleado_id)
    return service.obtener_por_id(empleado_id)


@router.get("/compania/{compania_id}", response_model=list[EmpleadoDTO])
def listar_empleados_por_compania(compania_id: UUID, service: EmpleadoService = Depends(get_empleado_service)):
    logger.info("[Controller] GET /api/empleados/compania/%s", compania_id)
    return service.listar_por_compania(compania_id)


@router.post("", response_model=EmpleadoDTO, status_code=201)
def crear_empleado(dto: EmpleadoCreateDTO, service: EmpleadoService = Depends(get_empleado_service)):
    logger.info("[Controller] POST /api/empleados")
    return service.crear(dto)


@router.put("/{empleado_id}", response_model=EmpleadoDTO)
def actualizar_empleado(empleado_id: UUID, dto: EmpleadoUpdateDTO, service: EmpleadoService = Depends(get_empleado_service)):
    logger.info("[Controller] PUT /api/empleados/%s", empleado_id)
    return service.actualizar(empleado_id, dto)


@router.delete("/{empleado_id}", status_code=204)
def eliminar_empleado(empleado_id: UUID, service: EmpleadoService = Depends(get_empleado_service)):
    logger.info("[Controller] DELETE /api/empleados/%s", empleado_id)
    service.eliminar(empleado_id)