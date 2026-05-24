"""
Servicio de aplicación: CompaniaService

Orquesta los casos de uso relacionados con las compañías.
Incluye el método transaccional crítico 'crear_compania_con_empleados'
que usa el patrón Unit of Work para garantizar atomicidad: si cualquier
empleado falla, ningún dato queda persistido (rollback completo).

Equivalente en C#: Servicio con IUnitOfWork + SaveChanges + using pattern.
"""

import logging
from uuid import UUID
from typing import Sequence

from app.domain.entities.compania import Compania
from app.domain.entities.empleado import Empleado
from app.domain.interfaces.unit_of_work import IUnitOfWork
from app.application.dtos.compania_dto import (
    CompaniaCreateDTO,
    CompaniaUpdateDTO,
    CompaniaDTO,
    CompaniaConEmpleadosCreateDTO,
    CompaniaConEmpleadosDTO,
)

logger = logging.getLogger(__name__)


class CompaniaService:
    """
    Servicio de aplicación que implementa la lógica de negocio
    para la gestión de compañías.

    Args:
        uow: Instancia del Unit of Work inyectada (IUnitOfWork).
    """

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    # ------------------------------------------------------------------ #
    #  Consultas                                                           #
    # ------------------------------------------------------------------ #

    def listar_todas(self) -> Sequence[CompaniaDTO]:
        """Retorna la lista completa de compañías."""
        logger.info("[CompaniaService] Consultando todas las compañías.")
        with self._uow as uow:
            companias = uow.companias.get_all()
            logger.info("[CompaniaService] %d compañías encontradas.", len(companias))
            return [CompaniaDTO.model_validate(c) for c in companias]

    def obtener_por_id(self, compania_id: UUID) -> CompaniaDTO:
        """
        Retorna una compañía por su UUID.

        Raises:
            ValueError: Si no existe una compañía con el ID dado.
        """
        logger.info("[CompaniaService] Buscando compañía id=%s.", compania_id)
        with self._uow as uow:
            compania = uow.companias.get_by_id(compania_id)
            if compania is None:
                logger.warning("[CompaniaService] Compañía id=%s no encontrada.", compania_id)
                raise ValueError(f"Compañía con id '{compania_id}' no encontrada.")
            return CompaniaDTO.model_validate(compania)

    # ------------------------------------------------------------------ #
    #  Comandos simples                                                    #
    # ------------------------------------------------------------------ #

    def crear(self, dto: CompaniaCreateDTO) -> CompaniaDTO:
        """
        Crea y persiste una nueva compañía (sin empleados).

        Args:
            dto: Datos validados de la nueva compañía.

        Returns:
            La compañía creada con su UUID asignado.
        """
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
            return CompaniaDTO.model_validate(creada)

    def actualizar(self, compania_id: UUID, dto: CompaniaUpdateDTO) -> CompaniaDTO:
        """
        Actualiza los campos provistos de una compañía existente.

        Args:
            compania_id: UUID de la compañía a actualizar.
            dto: Campos a modificar (los None se ignoran).

        Raises:
            ValueError: Si la compañía no existe.
        """
        logger.info("[CompaniaService] Iniciando transacción: actualizar compañía id=%s.", compania_id)
        with self._uow as uow:
            compania = uow.companias.get_by_id(compania_id)
            if compania is None:
                raise ValueError(f"Compañía con id '{compania_id}' no encontrada.")

            datos = dto.model_dump(exclude_none=True)
            for campo, valor in datos.items():
                setattr(compania, campo, valor)

            actualizada = uow.companias.update(compania)
            uow.commit()
            logger.info("[CompaniaService] Commit exitoso. Compañía id=%s actualizada.", compania_id)
            return CompaniaDTO.model_validate(actualizada)

    def eliminar(self, compania_id: UUID) -> None:
        """
        Elimina una compañía y todos sus empleados en cascada.

        Raises:
            ValueError: Si la compañía no existe.
        """
        logger.info("[CompaniaService] Iniciando transacción: eliminar compañía id=%s.", compania_id)
        with self._uow as uow:
            compania = uow.companias.get_by_id(compania_id)
            if compania is None:
                raise ValueError(f"Compañía con id '{compania_id}' no encontrada.")
            uow.companias.delete(compania_id)
            uow.commit()
            logger.info("[CompaniaService] Commit exitoso. Compañía id=%s eliminada.", compania_id)

    # ------------------------------------------------------------------ #
    #  Caso Transaccional Especial (Unit of Work)                         #
    # ------------------------------------------------------------------ #

    def crear_compania_con_empleados(
        self, dto: CompaniaConEmpleadosCreateDTO
    ) -> CompaniaConEmpleadosDTO:
        """
        Crea una compañía y todos sus empleados en una única transacción atómica.

        Flujo:
            1. Abre el contexto de transacción (with self._uow as uow).
            2. Crea y persiste la entidad Compania en el repositorio.
            3. Hace flush para que la BD asigne el UUID de la compañía
               antes de confirmar el commit.
            4. Itera sobre los empleados del DTO, asigna el compania_id
               generado y los persiste uno a uno.
            5. Llama a uow.commit() para confirmar todo de forma atómica.
            6. Si cualquier paso lanza una excepción (e.g. correo duplicado),
               el __exit__ del UoW ejecuta rollback() automáticamente,
               dejando la base de datos sin ningún cambio.

        Args:
            dto: Datos validados de la compañía y su lista de empleados.

        Returns:
            La compañía creada con la lista de empleados incluida.

        Raises:
            Exception: Re-lanza cualquier excepción de BD tras el rollback.
        """
        logger.info(
            "[CompaniaService] Iniciando transacción UoW: crear compañía '%s' con %d empleado(s).",
            dto.nombre,
            len(dto.empleados),
        )

        with self._uow as uow:
            # Paso 1: Crear la entidad Compania
            nueva_compania = Compania(
                nombre=dto.nombre,
                direccion=dto.direccion,
                telefono=dto.telefono,
            )
            compania_creada = uow.companias.create(nueva_compania)

            # Paso 2: Flush para obtener el UUID asignado por la BD
            # (La implementación concreta del repositorio debe exponer
            #  el session.flush() para que el id esté disponible aquí.)
            if hasattr(uow, "flush"):
                uow.flush()

            compania_id = compania_creada.id
            logger.info("[CompaniaService] Compañía provisional id=%s. Procesando empleados...", compania_id)

            # Paso 3: Crear cada empleado vinculándolo a la compañía
            empleados_creados = []
            for i, emp_dto in enumerate(dto.empleados, start=1):
                nuevo_empleado = Empleado(
                    nombre=emp_dto.nombre,
                    apellido=emp_dto.apellido,
                    correo=emp_dto.correo,
                    cargo=emp_dto.cargo,
                    salario=emp_dto.salario,
                    compania_id=compania_id,
                )
                empleado_creado = uow.empleados.create(nuevo_empleado)
                empleados_creados.append(empleado_creado)
                logger.info(
                    "[CompaniaService] Empleado %d/%d '%s %s' listo para commit.",
                    i, len(dto.empleados), emp_dto.nombre, emp_dto.apellido,
                )

            # Paso 4: Commit atómico — si falla aquí, __exit__ hace rollback
            uow.commit()
            logger.info(
                "[CompaniaService] Commit exitoso. Compañía id=%s con %d empleado(s) persistidos.",
                compania_id,
                len(empleados_creados),
            )

            from app.application.dtos.empleado_dto import EmpleadoDTO
            return CompaniaConEmpleadosDTO(
                id=compania_creada.id,
                nombre=compania_creada.nombre,
                direccion=compania_creada.direccion,
                telefono=compania_creada.telefono,
                fecha_creacion=compania_creada.fecha_creacion,
                empleados=[EmpleadoDTO.model_validate(e) for e in empleados_creados],
            )
