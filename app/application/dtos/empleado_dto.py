"""
DTOs de Pydantic: Empleado

Esquemas de validación para la entrada y salida de datos de la entidad
Empleado. Desacoplan la capa de dominio de las peticiones HTTP externas.

Equivalente en C#: DTOs + FluentValidation o DataAnnotations.
"""

from decimal import Decimal
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, model_validator


# ------------------------------------------------------------------ #
#  Schema base (campos comunes)                                        #
# ------------------------------------------------------------------ #

class EmpleadoBase(BaseModel):
    """Campos comunes que comparten todos los esquemas de Empleado."""

    nombre: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["Juan"],
        description="Nombre del empleado.",
    )
    apellido: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["Pérez"],
        description="Apellido del empleado.",
    )
    correo: EmailStr = Field(
        ...,
        examples=["juan.perez@empresa.com"],
        description="Correo electrónico único del empleado.",
    )
    cargo: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["Desarrollador Backend"],
        description="Cargo o puesto del empleado.",
    )
    salario: Decimal = Field(
        ...,
        gt=Decimal("0"),
        max_digits=10,
        decimal_places=2,
        examples=[3500000.00],
        description="Salario mensual del empleado. Debe ser positivo.",
    )


# ------------------------------------------------------------------ #
#  Schemas de entrada (Create / Update)                                #
# ------------------------------------------------------------------ #

class EmpleadoCreateDTO(EmpleadoBase):
    """
    Schema para crear un nuevo empleado.
    Se usa en: POST /api/empleados y como item anidado en CompaniaConEmpleadosCreateDTO.
    """

    compania_id: UUID = Field(
        ...,
        description="UUID de la compañía a la que pertenece el empleado.",
    )


class EmpleadoCreateAnidadoDTO(EmpleadoBase):
    """
    Schema para crear un empleado dentro del flujo transaccional
    de creación conjunta de compañía + empleados. NO incluye compania_id
    porque éste se inyecta automáticamente desde la compañía padre.
    """
    pass


class EmpleadoUpdateDTO(BaseModel):
    """Schema para actualizar campos editables de un empleado (parcial)."""

    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    apellido: str | None = Field(default=None, min_length=1, max_length=100)
    correo: EmailStr | None = Field(default=None)
    cargo: str | None = Field(default=None, min_length=1, max_length=100)
    salario: Decimal | None = Field(default=None, gt=Decimal("0"), max_digits=10, decimal_places=2)

    @model_validator(mode="after")
    def validar_al_menos_un_campo(self) -> "EmpleadoUpdateDTO":
        if all(
            value is None
            for value in (self.nombre, self.apellido, self.correo, self.cargo, self.salario)
        ):
            raise ValueError("Debe enviar al menos un campo para actualizar el empleado.")
        return self


# ------------------------------------------------------------------ #
#  Schema de salida (Response)                                         #
# ------------------------------------------------------------------ #

class EmpleadoDTO(EmpleadoBase):
    """
    Schema de respuesta completo de un Empleado.
    Incluye el id y la referencia a la compañía.
    """

    id: UUID = Field(..., description="Identificador único del empleado.")
    compania_id: UUID = Field(..., description="UUID de la compañía a la que pertenece.")
