"""
DTOs de Pydantic: Compania

Esquemas de validación para la entrada y salida de datos de la entidad
Compania. Incluye el DTO transaccional especial CompaniaConEmpleadosCreateDTO
que permite crear una compañía y sus empleados en una sola operación atómica.

Equivalente en C#: DTOs + FluentValidation o DataAnnotations.
"""

from uuid import UUID
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, model_validator

from app.application.dtos.empleado_dto import EmpleadoCreateAnidadoDTO, EmpleadoDTO


# ------------------------------------------------------------------ #
#  Schema base (campos comunes)                                        #
# ------------------------------------------------------------------ #

class CompaniaBase(BaseModel):
    """Campos comunes que comparten todos los esquemas de Compania."""

    nombre: str = Field(
        ...,
        min_length=1,
        max_length=200,
        examples=["Tech Solutions SAS"],
        description="Nombre oficial de la compañía.",
    )
    direccion: str = Field(
        ...,
        min_length=1,
        max_length=300,
        examples=["Cra 45 # 26-85, Medellín"],
        description="Dirección física de la compañía.",
    )
    telefono: str = Field(
        ...,
        min_length=7,
        max_length=20,
        examples=["+57 604 444 5566"],
        description="Número de contacto de la compañía.",
    )


# ------------------------------------------------------------------ #
#  Schemas de entrada (Create / Update)                                #
# ------------------------------------------------------------------ #

class CompaniaCreateDTO(CompaniaBase):
    """Schema para crear una nueva compañía sin empleados."""
    pass


class CompaniaUpdateDTO(BaseModel):
    """Schema para actualizar campos editables de una compania (parcial)."""

    nombre: str | None = Field(default=None, min_length=1, max_length=200)
    direccion: str | None = Field(default=None, min_length=1, max_length=300)
    telefono: str | None = Field(default=None, min_length=7, max_length=20)

    @model_validator(mode="after")
    def validar_al_menos_un_campo(self) -> "CompaniaUpdateDTO":
        if self.nombre is None and self.direccion is None and self.telefono is None:
            raise ValueError("Debe enviar al menos un campo para actualizar la compania.")
        return self


# ------------------------------------------------------------------ #
#  DTO Transaccional Especial (Unit of Work)                           #
# ------------------------------------------------------------------ #

class CompaniaConEmpleadosCreateDTO(CompaniaBase):
    """
    Schema transaccional para crear una compañía y su lista de empleados
    en una sola operación atómica (Unit of Work).

    Si algún empleado falla la validación o viola una restricción de BD
    (e.g. correo duplicado), la transacción completa hace rollback y
    ni la compañía ni ningún empleado queda registrado.

    Uso: POST /api/companias/con-empleados
    """

    empleados: List[EmpleadoCreateAnidadoDTO] = Field(
        ...,
        min_length=1,
        description="Lista de empleados a crear junto con la compañía. Mínimo 1.",
    )


# ------------------------------------------------------------------ #
#  Schema de salida (Response)                                         #
# ------------------------------------------------------------------ #

class CompaniaDTO(CompaniaBase):
    """Schema de respuesta básico de una Compania (sin empleados anidados)."""

    id: UUID = Field(..., description="Identificador único de la compañía.")
    fecha_creacion: datetime = Field(..., description="Fecha y hora UTC de registro.")


class CompaniaConEmpleadosDTO(CompaniaDTO):
    """Schema de respuesta completo que incluye la lista de empleados."""

    empleados: List[EmpleadoDTO] = Field(
        default_factory=list,
        description="Empleados vinculados a esta compañía.",
    )
