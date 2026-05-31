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

    async def listar_todos(self) -> Sequence[EmpleadoDTO]:
        logger.info("[EmpleadoService] Iniciando consulta de todos los empleados.")
        async with self._uow as uow:
            empleados = await uow.empleados.get_all()
            logger.info("[EmpleadoService] %d empleados encontrados.", len(empleados))
            return [empleado_to_dto(empleado) for empleado in empleados]

    async def obtener_por_id(self, empleado_id: UUID) -> EmpleadoDTO:
        logger.info("[EmpleadoService] Buscando empleado id=%s.", empleado_id)
        async with self._uow as uow:
            empleado = await uow.empleados.get_by_id(empleado_id)
            if empleado is None:
                logger.warning("[EmpleadoService] Empleado id=%s no encontrado.", empleado_id)
                raise EntityNotFoundError(f"Empleado con id '{empleado_id}' no encontrado.")
            return empleado_to_dto(empleado)

    async def listar_por_compania(self, compania_id: UUID) -> Sequence[EmpleadoDTO]:
        logger.info("[EmpleadoService] Listando empleados de compania_id=%s.", compania_id)
        async with self._uow as uow:
            if await uow.companias.get_by_id(compania_id) is None:
                raise EntityNotFoundError(f"Compañía con id '{compania_id}' no encontrada.")
            empleados = await uow.empleados.find_by_condition(compania_id=compania_id)
            return [empleado_to_dto(empleado) for empleado in empleados]

    async def crear(self, dto: EmpleadoCreateDTO) -> EmpleadoDTO:
        logger.info("[EmpleadoService] Iniciando transacción: crear empleado '%s %s'.", dto.nombre, dto.apellido)
        async with self._uow as uow:
            if await uow.companias.get_by_id(dto.compania_id) is None:
                raise EntityNotFoundError(f"Compañía con id '{dto.compania_id}' no encontrada.")
            correo = str(dto.correo).strip().lower()
            if await uow.empleados.get_by_correo(correo):
                raise ConflictError(f"Ya existe un empleado con el correo '{correo}'.")

            nuevo = Empleado(
                nombre=dto.nombre,
                apellido=dto.apellido,
                correo=correo,
                cargo=dto.cargo,
                salario=dto.salario,
                compania_id=dto.compania_id,
            )
            creado = await uow.empleados.create(nuevo)
            await uow.commit()
            logger.info("[EmpleadoService] Commit exitoso. Empleado id=%s creado.", creado.id)
            return empleado_to_dto(creado)

    async def actualizar(self, empleado_id: UUID, dto: EmpleadoUpdateDTO) -> EmpleadoDTO:
        logger.info("[EmpleadoService] Iniciando transacción: actualizar empleado id=%s.", empleado_id)
        async with self._uow as uow:
            empleado = await uow.empleados.get_by_id(empleado_id)
            if empleado is None:
                raise EntityNotFoundError(f"Empleado con id '{empleado_id}' no encontrado.")

            datos = dto.model_dump(exclude_none=True)
            nuevo_correo = datos.get("correo")
            if nuevo_correo is not None:
                correo_normalizado = str(nuevo_correo).strip().lower()
                existente = await uow.empleados.get_by_correo(correo_normalizado)
                if existente is not None and existente.id != empleado_id:
                    raise ConflictError(f"Ya existe un empleado con el correo '{nuevo_correo}'.")

            empleado.actualizar(
                nombre=datos.get("nombre"),
                apellido=datos.get("apellido"),
                correo=str(nuevo_correo).strip().lower() if nuevo_correo is not None else None,
                cargo=datos.get("cargo"),
                salario=datos.get("salario"),
            )

            actualizado = await uow.empleados.update(empleado)
            await uow.commit()
            logger.info("[EmpleadoService] Commit exitoso. Empleado id=%s actualizado.", empleado_id)
            return empleado_to_dto(actualizado)

    async def eliminar(self, empleado_id: UUID) -> None:
        logger.info("[EmpleadoService] Iniciando transacción: eliminar empleado id=%s.", empleado_id)
        async with self._uow as uow:
            empleado = await uow.empleados.get_by_id(empleado_id)
            if empleado is None:
                raise EntityNotFoundError(f"Empleado con id '{empleado_id}' no encontrado.")
            await uow.empleados.delete(empleado_id)
            await uow.commit()
            logger.info("[EmpleadoService] Commit exitoso. Empleado id=%s eliminado.", empleado_id)

    async def listar_paginados(
        self, pagina: int, tamano: int, orden: str | None = None, dir: str | None = None, buscar: str | None = None, compania_id: UUID | None = None
    ) -> PaginatedResponse[EmpleadoDTO]:
        logger.info("[EmpleadoService] Consultando empleados paginados (pagina %d, tamano %d).", pagina, tamano)
        async with self._uow as uow:
            empleados, total = await uow.empleados.get_paged(pagina, tamano, orden, dir, buscar, compania_id)
            dtos = [empleado_to_dto(e) for e in empleados]
            return PaginatedResponse.create(dtos, pagina, tamano, total)

    async def crear_en_lote(self, dtos: Sequence[EmpleadoCreateDTO]) -> Sequence[EmpleadoDTO]:
        logger.info("[EmpleadoService] Iniciando transacción bulk insert: crear %d empleados.", len(dtos))
        from app.domain.policies.unicidad_correo import asegurar_correos_unicos_en_solicitud
        correos_solicitud = [str(dto.correo).strip().lower() for dto in dtos]
        asegurar_correos_unicos_en_solicitud(correos_solicitud)
        
        async with self._uow as uow:
            nuevos = []
            for dto in dtos:
                if await uow.companias.get_by_id(dto.compania_id) is None:
                    raise EntityNotFoundError(f"Compañía con id '{dto.compania_id}' no encontrada.")
                if await uow.empleados.get_by_correo(str(dto.correo).strip().lower()):
                    raise ConflictError(f"Ya existe un empleado con el correo '{dto.correo}'.")
                    
                nuevos.append(Empleado(
                    nombre=dto.nombre,
                    apellido=dto.apellido,
                    correo=str(dto.correo).strip().lower(),
                    cargo=dto.cargo,
                    salario=dto.salario,
                    compania_id=dto.compania_id,
                ))
            
            creados = await uow.empleados.create_range(nuevos)
            await uow.commit()
            return [empleado_to_dto(e) for e in creados]

    async def actualizar_parcial(self, empleado_id: UUID, dto: EmpleadoUpdateDTO) -> EmpleadoDTO:
        logger.info("[EmpleadoService] Iniciando transacción PATCH: empleado id=%s.", empleado_id)
        async with self._uow as uow:
            datos = dto.model_dump(exclude_none=True)
            if not datos:
                raise ValueError("No hay campos para actualizar")
                
            nuevo_correo = datos.get("correo")
            if nuevo_correo is not None:
                correo_normalizado = str(nuevo_correo).strip().lower()
                existente = await uow.empleados.get_by_correo(correo_normalizado)
                if existente is not None and existente.id != empleado_id:
                    raise ConflictError(f"Ya existe un empleado con el correo '{nuevo_correo}'.")
                datos["correo"] = correo_normalizado
                
            actualizado = await uow.empleados.patch_partial(empleado_id, datos)
            if actualizado is None:
                raise EntityNotFoundError(f"Empleado con id '{empleado_id}' no encontrado.")
                
            await uow.commit()
            return empleado_to_dto(actualizado)

    async def eliminar_en_lote(self, empleado_ids: Sequence[UUID]) -> None:
        logger.info("[EmpleadoService] Iniciando transacción bulk delete: %d empleados.", len(empleado_ids))
        async with self._uow as uow:
            await uow.empleados.delete_range(empleado_ids)
            await uow.commit()
