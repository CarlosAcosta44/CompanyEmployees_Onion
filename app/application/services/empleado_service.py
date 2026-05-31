"""
Servicio de aplicación: EmpleadoService

Orquesta los casos de uso de empleados usando únicamente IUnitOfWork.
"""

import logging
from uuid import UUID
from typing import Sequence

from app.application.dtos.empleado_dto import EmpleadoCreateDTO, EmpleadoUpdateDTO, EmpleadoDTO
from app.application.dtos.pagination_dto import PaginatedResponse
from app.application.mappers.empleado_mapper import empleado_to_dto
from app.domain.entities.empleado import Empleado
from app.domain.exceptions import ConflictError, EntityNotFoundError
from app.domain.interfaces.unit_of_work import IUnitOfWork

logger = logging.getLogger(__name__)


class EmpleadoService:
    """Casos de uso de empleados. Depende solo de IUnitOfWork (puerto de dominio)."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    def listar_todos(self) -> Sequence[EmpleadoDTO]:
        logger.info("[EmpleadoService] Iniciando consulta de todos los empleados.")
        with self._uow as uow:
            empleados = uow.empleados.get_all()
            logger.info("[EmpleadoService] %d empleados encontrados.", len(empleados))
            return [empleado_to_dto(empleado) for empleado in empleados]

    def obtener_por_id(self, empleado_id: UUID) -> EmpleadoDTO:
        logger.info("[EmpleadoService] Buscando empleado id=%s.", empleado_id)
        with self._uow as uow:
            empleado = uow.empleados.get_by_id(empleado_id)
            if empleado is None:
                logger.warning("[EmpleadoService] Empleado id=%s no encontrado.", empleado_id)
                raise EntityNotFoundError(f"Empleado con id '{empleado_id}' no encontrado.")
            return empleado_to_dto(empleado)

    def listar_por_compania(self, compania_id: UUID) -> Sequence[EmpleadoDTO]:
        logger.info("[EmpleadoService] Listando empleados de compania_id=%s.", compania_id)
        with self._uow as uow:
            if uow.companias.get_by_id(compania_id) is None:
                raise EntityNotFoundError(f"Compañía con id '{compania_id}' no encontrada.")
            empleados = uow.empleados.find_by_condition(compania_id=compania_id)
            return [empleado_to_dto(empleado) for empleado in empleados]

    def crear(self, dto: EmpleadoCreateDTO) -> EmpleadoDTO:
        logger.info("[EmpleadoService] Iniciando transacción: crear empleado '%s %s'.", dto.nombre, dto.apellido)
        with self._uow as uow:
            if uow.companias.get_by_id(dto.compania_id) is None:
                raise EntityNotFoundError(f"Compañía con id '{dto.compania_id}' no encontrada.")
            correo = str(dto.correo).strip().lower()
            if uow.empleados.get_by_correo(correo):
                raise ConflictError(f"Ya existe un empleado con el correo '{correo}'.")

            nuevo = Empleado(
                nombre=dto.nombre,
                apellido=dto.apellido,
                correo=correo,
                cargo=dto.cargo,
                salario=dto.salario,
                compania_id=dto.compania_id,
            )
            creado = uow.empleados.create(nuevo)
            uow.commit()
            logger.info("[EmpleadoService] Commit exitoso. Empleado id=%s creado.", creado.id)
            return empleado_to_dto(creado)

    def actualizar(self, empleado_id: UUID, dto: EmpleadoUpdateDTO) -> EmpleadoDTO:
        logger.info("[EmpleadoService] Iniciando transacción: actualizar empleado id=%s.", empleado_id)
        with self._uow as uow:
            empleado = uow.empleados.get_by_id(empleado_id)
            if empleado is None:
                raise EntityNotFoundError(f"Empleado con id '{empleado_id}' no encontrado.")

            datos = dto.model_dump(exclude_none=True)
            nuevo_correo = datos.get("correo")
            if nuevo_correo is not None:
                correo_normalizado = str(nuevo_correo).strip().lower()
                existente = uow.empleados.get_by_correo(correo_normalizado)
                if existente is not None and existente.id != empleado_id:
                    raise ConflictError(f"Ya existe un empleado con el correo '{nuevo_correo}'.")

            empleado.actualizar(
                nombre=datos.get("nombre"),
                apellido=datos.get("apellido"),
                correo=str(nuevo_correo).strip().lower() if nuevo_correo is not None else None,
                cargo=datos.get("cargo"),
                salario=datos.get("salario"),
            )

            actualizado = uow.empleados.update(empleado)
            uow.commit()
            logger.info("[EmpleadoService] Commit exitoso. Empleado id=%s actualizado.", empleado_id)
            return empleado_to_dto(actualizado)

    def eliminar(self, empleado_id: UUID) -> None:
        logger.info("[EmpleadoService] Iniciando transacción: eliminar empleado id=%s.", empleado_id)
        with self._uow as uow:
            empleado = uow.empleados.get_by_id(empleado_id)
        correos_solicitud = [str(dto.correo).strip().lower() for dto in dtos]
        asegurar_correos_unicos_en_solicitud(correos_solicitud)
        
        with self._uow as uow:
            nuevos = []
            for dto in dtos:
                if uow.companias.get_by_id(dto.compania_id) is None:
                    raise EntityNotFoundError(f"Compañía con id '{dto.compania_id}' no encontrada.")
                if uow.empleados.get_by_correo(str(dto.correo).strip().lower()):
                    raise ConflictError(f"Ya existe un empleado con el correo '{dto.correo}'.")
                    
                nuevos.append(Empleado(
                    nombre=dto.nombre,
                    apellido=dto.apellido,
                    correo=str(dto.correo).strip().lower(),
                    cargo=dto.cargo,
                    salario=dto.salario,
                    compania_id=dto.compania_id,
                ))
            
            creados = uow.empleados.create_range(nuevos)
            uow.commit()
            return [empleado_to_dto(e) for e in creados]

    def actualizar_parcial(self, empleado_id: UUID, dto: EmpleadoUpdateDTO) -> EmpleadoDTO:
        logger.info("[EmpleadoService] Iniciando transacción PATCH: empleado id=%s.", empleado_id)
        with self._uow as uow:
            datos = dto.model_dump(exclude_none=True)
            if not datos:
                raise ValueError("No hay campos para actualizar")
                
            nuevo_correo = datos.get("correo")
            if nuevo_correo is not None:
                correo_normalizado = str(nuevo_correo).strip().lower()
                existente = uow.empleados.get_by_correo(correo_normalizado)
                if existente is not None and existente.id != empleado_id:
                    raise ConflictError(f"Ya existe un empleado con el correo '{nuevo_correo}'.")
                datos["correo"] = correo_normalizado
                
            actualizado = uow.empleados.patch_partial(empleado_id, datos)
            if actualizado is None:
                raise EntityNotFoundError(f"Empleado con id '{empleado_id}' no encontrado.")
                
            uow.commit()
            return empleado_to_dto(actualizado)

    def eliminar_en_lote(self, empleado_ids: Sequence[UUID]) -> None:
        logger.info("[EmpleadoService] Iniciando transacción bulk delete: %d empleados.", len(empleado_ids))
        with self._uow as uow:
            uow.empleados.delete_range(empleado_ids)
            uow.commit()
