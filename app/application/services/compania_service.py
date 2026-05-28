"""
Servicio de aplicación: CompaniaService

Orquesta los casos de uso relacionados con las compañías.
Incluye el método transaccional crítico 'crear_compania_con_empleados'
que usa el patrón Unit of Work para garantizar atomicidad.
"""

import logging
from uuid import UUID
from typing import Sequence

from app.application.dtos.compania_dto import (
    CompaniaCreateDTO,
    CompaniaUpdateDTO,
    CompaniaDTO,
    CompaniaConEmpleadosCreateDTO,
    CompaniaConEmpleadosDTO,
)
from app.application.mappers.compania_mapper import compania_con_empleados_to_dto, compania_to_dto
from app.application.mappers.empleado_mapper import empleado_to_dto
from app.domain.entities.compania import Compania
from app.domain.entities.empleado import Empleado
from app.domain.exceptions import ConflictError, EntityNotFoundError
from app.domain.interfaces.unit_of_work import IUnitOfWork
from app.domain.policies.unicidad_correo import asegurar_correos_unicos_en_solicitud

logger = logging.getLogger(__name__)


class CompaniaService:
    """Casos de uso de compañías. Depende solo de IUnitOfWork (puerto de dominio)."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    def listar_todas(self) -> Sequence[CompaniaDTO]:
        logger.info("[CompaniaService] Consultando todas las compañías.")
        with self._uow as uow:
            companias = uow.companias.get_all()
            logger.info("[CompaniaService] %d compañías encontradas.", len(companias))
            return [compania_to_dto(compania) for compania in companias]

    def obtener_por_id(self, compania_id: UUID) -> CompaniaDTO:
        logger.info("[CompaniaService] Buscando compañía id=%s.", compania_id)
        with self._uow as uow:
            compania = uow.companias.get_by_id(compania_id)
            if compania is None:
                logger.warning("[CompaniaService] Compañía id=%s no encontrada.", compania_id)
                raise EntityNotFoundError(f"Compañía con id '{compania_id}' no encontrada.")
            return compania_to_dto(compania)

    def crear(self, dto: CompaniaCreateDTO) -> CompaniaDTO:
        logger.info("[CompaniaService] Iniciando transacción: crear compañía '%s'.", dto.nombre)
        with self._uow as uow:
            nueva = Compania(
                nombre=dto.nombre,
                direccion=dto.direccion,
                telefono=dto.telefono,
            )
            creada = uow.companias.create(nueva)
            uow.commit()
            logger.info("[CompaniaService] Commit exitoso. Compañía id=%s creada.", creada.id)
            return compania_to_dto(creada)

    def actualizar(self, compania_id: UUID, dto: CompaniaUpdateDTO) -> CompaniaDTO:
        logger.info("[CompaniaService] Iniciando transacción: actualizar compañía id=%s.", compania_id)
        with self._uow as uow:
            compania = uow.companias.get_by_id(compania_id)
            if compania is None:
                raise EntityNotFoundError(f"Compañía con id '{compania_id}' no encontrada.")

            datos = dto.model_dump(exclude_none=True)
            compania.actualizar(
                nombre=datos.get("nombre"),
                direccion=datos.get("direccion"),
                telefono=datos.get("telefono"),
            )

            actualizada = uow.companias.update(compania)
            uow.commit()
            logger.info("[CompaniaService] Commit exitoso. Compañía id=%s actualizada.", compania_id)
            return compania_to_dto(actualizada)

    def eliminar(self, compania_id: UUID) -> None:
        logger.info("[CompaniaService] Iniciando transacción: eliminar compañía id=%s.", compania_id)
        with self._uow as uow:
            compania = uow.companias.get_by_id(compania_id)
            if compania is None:
                raise EntityNotFoundError(f"Compañía con id '{compania_id}' no encontrada.")
            uow.companias.delete(compania_id)
            uow.commit()
            logger.info("[CompaniaService] Commit exitoso. Compañía id=%s eliminada.", compania_id)

    def crear_compania_con_empleados(
        self, dto: CompaniaConEmpleadosCreateDTO
    ) -> CompaniaConEmpleadosDTO:
        logger.info(
            "[CompaniaService] Iniciando transacción UoW: crear compañía '%s' con %d empleado(s).",
            dto.nombre,
            len(dto.empleados),
        )

        correos_solicitud = [str(emp.correo) for emp in dto.empleados]
        asegurar_correos_unicos_en_solicitud(correos_solicitud)

        with self._uow as uow:
            nueva_compania = Compania(
                nombre=dto.nombre,
                direccion=dto.direccion,
                telefono=dto.telefono,
            )
            compania_creada = uow.companias.create(nueva_compania)
            compania_id = compania_creada.id

            empleados_creados: list[Empleado] = []
            for i, emp_dto in enumerate(dto.empleados, start=1):
                correo = str(emp_dto.correo).strip().lower()
                if uow.empleados.get_by_correo(correo):
                    raise ConflictError(f"Ya existe un empleado con el correo '{correo}'.")

                nuevo_empleado = Empleado(
                    nombre=emp_dto.nombre,
                    apellido=emp_dto.apellido,
                    correo=correo,
                    cargo=emp_dto.cargo,
                    salario=emp_dto.salario,
                    compania_id=compania_id,
                )
                compania_creada.agregar_empleado(nuevo_empleado)
                empleados_creados.append(uow.empleados.create(nuevo_empleado))
                logger.info(
                    "[CompaniaService] Empleado %d/%d '%s %s' listo para commit.",
                    i,
                    len(dto.empleados),
                    emp_dto.nombre,
                    emp_dto.apellido,
                )

            uow.commit()
            logger.info(
                "[CompaniaService] Commit exitoso. Compañía id=%s con %d empleado(s) persistidos.",
                compania_id,
                len(empleados_creados),
            )
            return compania_con_empleados_to_dto(compania_creada, empleados_creados)
