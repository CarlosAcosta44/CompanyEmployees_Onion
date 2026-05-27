"""
DTOs de Pydantic: Empleado

Esquemas de validación para la entrada y salida de datos de la entidad
Empleado. Desacoplan la capa de dominio de las peticiones HTTP externas.

Equivalente en C#: DTOs + FluentValidation o DataAnnotations.
"""

from decimal import Decimal
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


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


class EmpleadoUpdateDTO(EmpleadoBase):
    """Schema para reemplazar los datos editables de un empleado."""


# ------------------------------------------------------------------ #
#  Schema de salida (Response)                                         #
# ------------------------------------------------------------------ #

class EmpleadoDTO(EmpleadoBase):
    """
    Schema de respuesta completo de un Empleado.
    Incluye el id y la referencia a la compañía.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Identificador único del empleado.")
    compania_id: UUID = Field(..., description="UUID de la compañía a la que pertenece.")
