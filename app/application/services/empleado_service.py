"""
Servicio de aplicación: EmpleadoService

Orquesta los casos de uso relacionados con los empleados.
Solo conoce la interfaz abstracta IUnitOfWork; no tiene ninguna
referencia directa a SQLAlchemy ni a PostgreSQL.

Equivalente en C#: Clase de servicio que inyecta IUnitOfWork.
"""

import logging
from uuid import UUID
from typing import Sequence

from app.domain.entities.empleado import Empleado
from app.domain.interfaces.unit_of_work import IUnitOfWork
from app.application.dtos.empleado_dto import EmpleadoCreateDTO, EmpleadoUpdateDTO, EmpleadoDTO

logger = logging.getLogger(__name__)


class EmpleadoService:
    """
    Servicio de aplicación que implementa la lógica de negocio
    para la gestión de empleados.

    Args:
        uow: Instancia del Unit of Work inyectada (IUnitOfWork).
    """

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    # ------------------------------------------------------------------ #
    #  Consultas                                                           #
    # ------------------------------------------------------------------ #

    def listar_todos(self) -> Sequence[EmpleadoDTO]:
        """Retorna la lista completa de empleados."""
        logger.info("[EmpleadoService] Iniciando consulta de todos los empleados.")
        with self._uow as uow:
            empleados = uow.empleados.get_all()
            logger.info("[EmpleadoService] %d empleados encontrados.", len(empleados))
            return [EmpleadoDTO.model_validate(e) for e in empleados]

    def obtener_por_id(self, empleado_id: UUID) -> EmpleadoDTO:
        """
        Retorna un empleado por su UUID.

        Raises:
            ValueError: Si no existe un empleado con el ID dado.
        """
        logger.info("[EmpleadoService] Buscando empleado id=%s.", empleado_id)
        with self._uow as uow:
            empleado = uow.empleados.get_by_id(empleado_id)
            if empleado is None:
                logger.warning("[EmpleadoService] Empleado id=%s no encontrado.", empleado_id)
                raise ValueError(f"Empleado con id '{empleado_id}' no encontrado.")
            return EmpleadoDTO.model_validate(empleado)

    def listar_por_compania(self, compania_id: UUID) -> Sequence[EmpleadoDTO]:
        """Retorna todos los empleados de una compañía específica."""
        logger.info("[EmpleadoService] Listando empleados de compania_id=%s.", compania_id)
        with self._uow as uow:
            empleados = uow.empleados.get_by_compania(compania_id)
            return [EmpleadoDTO.model_validate(e) for e in empleados]

    # ------------------------------------------------------------------ #
    #  Comandos                                                            #
    # ------------------------------------------------------------------ #

    def crear(self, dto: EmpleadoCreateDTO) -> EmpleadoDTO:
        """
        Crea y persiste un nuevo empleado.

        Args:
            dto: Datos validados del nuevo empleado.

        Returns:
            El empleado creado con su UUID asignado.
        """
        logger.info("[EmpleadoService] Iniciando transacción: crear empleado '%s %s'.", dto.nombre, dto.apellido)
        with self._uow as uow:
            nuevo = Empleado(
                nombre=dto.nombre,
                apellido=dto.apellido,
                correo=dto.correo,
                cargo=dto.cargo,
                salario=dto.salario,
                compania_id=dto.compania_id,
            )
            creado = uow.empleados.create(nuevo)
            uow.commit()
            logger.info("[EmpleadoService] Commit exitoso. Empleado id=%s creado.", creado.id)
            return EmpleadoDTO.model_validate(creado)

    def actualizar(self, empleado_id: UUID, dto: EmpleadoUpdateDTO) -> EmpleadoDTO:
        """
        Actualiza los campos provistos de un empleado existente.

        Args:
            empleado_id: UUID del empleado a actualizar.
            dto: Campos a modificar (los None se ignoran).

        Raises:
            ValueError: Si el empleado no existe.
        """
        logger.info("[EmpleadoService] Iniciando transacción: actualizar empleado id=%s.", empleado_id)
        with self._uow as uow:
            empleado = uow.empleados.get_by_id(empleado_id)
            if empleado is None:
                raise ValueError(f"Empleado con id '{empleado_id}' no encontrado.")

            # Solo actualiza los campos que no son None
            datos = dto.model_dump(exclude_none=True)
            for campo, valor in datos.items():
                setattr(empleado, campo, valor)

            actualizado = uow.empleados.update(empleado)
            uow.commit()
            logger.info("[EmpleadoService] Commit exitoso. Empleado id=%s actualizado.", empleado_id)
            return EmpleadoDTO.model_validate(actualizado)

    def eliminar(self, empleado_id: UUID) -> None:
        """
        Elimina un empleado por su UUID.

        Raises:
            ValueError: Si el empleado no existe.
        """
        logger.info("[EmpleadoService] Iniciando transacción: eliminar empleado id=%s.", empleado_id)
        with self._uow as uow:
            empleado = uow.empleados.get_by_id(empleado_id)
            if empleado is None:
                raise ValueError(f"Empleado con id '{empleado_id}' no encontrado.")
            uow.empleados.delete(empleado_id)
            uow.commit()
            logger.info("[EmpleadoService] Commit exitoso. Empleado id=%s eliminado.", empleado_id)
