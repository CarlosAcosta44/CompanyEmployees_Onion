"""Mapeo Empleado (dominio) -> DTOs de aplicacion."""

from __future__ import annotations

from app.application.dtos.empleado_dto import EmpleadoDTO
from app.domain.entities.empleado import Empleado


def empleado_to_dto(empleado: Empleado) -> EmpleadoDTO:
    return EmpleadoDTO(
        id=empleado.id,
        nombre=empleado.nombre,
        apellido=empleado.apellido,
        correo=empleado.correo,
        cargo=empleado.cargo,
        salario=empleado.salario,
        compania_id=empleado.compania_id,
    )
