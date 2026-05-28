"""Mapeo Compania (dominio) -> DTOs de aplicacion."""

from __future__ import annotations

from app.application.dtos.compania_dto import CompaniaConEmpleadosDTO, CompaniaDTO
from app.application.mappers.empleado_mapper import empleado_to_dto
from app.domain.entities.compania import Compania
from app.domain.entities.empleado import Empleado


def compania_to_dto(compania: Compania) -> CompaniaDTO:
    return CompaniaDTO(
        id=compania.id,
        nombre=compania.nombre,
        direccion=compania.direccion,
        telefono=compania.telefono,
        fecha_creacion=compania.fecha_creacion,
    )


def compania_con_empleados_to_dto(
    compania: Compania,
    empleados: list[Empleado],
) -> CompaniaConEmpleadosDTO:
    return CompaniaConEmpleadosDTO(
        id=compania.id,
        nombre=compania.nombre,
        direccion=compania.direccion,
        telefono=compania.telefono,
        fecha_creacion=compania.fecha_creacion,
        empleados=[empleado_to_dto(empleado) for empleado in empleados],
    )
