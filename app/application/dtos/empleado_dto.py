"""
DTOs de Pydantic: Empleado

Esquemas de validación para la entrada y salida de datos de la entidad
Empleado. Desacoplan la capa de dominio de las peticiones HTTP externas.

Equivalente en C#: DTOs + FluentValidation o DataAnnotations.
"""

import re
from decimal import Decimal
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


# Patrón: solo letras (incluyendo acentos y ñ), espacios y guiones
_NOMBRE_RE = re.compile(r"^[A-Za-záéíóúÁÉÍÓÚñÑüÜ\s\-']+$", re.UNICODE)

# Salario mínimo de referencia (puede ajustarse según normativa)
_SALARIO_MINIMO = Decimal("1300606")


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
        description="Nombre del empleado. Solo letras, espacios y guiones.",
    )
    apellido: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["Pérez"],
        description="Apellido del empleado. Solo letras, espacios y guiones.",
    )
    correo: EmailStr = Field(
        ...,
        examples=["juan.perez@empresa.com"],
        description="Correo electrónico único del empleado.",
    )
    cargo: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["Desarrollador Backend"],
        description="Cargo o puesto del empleado. Mínimo 2 caracteres.",
    )
    salario: Decimal = Field(
        ...,
        gt=Decimal("0"),
        max_digits=12,
        decimal_places=2,
        examples=[3500000.00],
        description="Salario mensual del empleado. Debe ser positivo.",
    )

    @field_validator("nombre", "apellido")
    @classmethod
    def validar_solo_letras(cls, v: str, info) -> str:
        """Elimina espacios sobrantes y valida que solo contenga letras."""
        v = v.strip()
        if not v:
            raise ValueError(f"El campo '{info.field_name}' no puede estar vacío.")
        if not _NOMBRE_RE.match(v):
            raise ValueError(
                f"El campo '{info.field_name}' solo puede contener letras, "
                "espacios y guiones. No se permiten números ni símbolos."
            )
        # Capitalizar cada palabra
        return v.title()

    @field_validator("cargo")
    @classmethod
    def validar_cargo(cls, v: str) -> str:
        """Elimina espacios sobrantes y verifica longitud mínima."""
        v = v.strip()
        if len(v) < 2:
            raise ValueError("El cargo debe tener al menos 2 caracteres significativos.")
        return v

    @field_validator("salario")
    @classmethod
    def validar_salario(cls, v: Decimal) -> Decimal:
        """Valida que el salario no sea menor al mínimo legal de referencia."""
        if v < _SALARIO_MINIMO:
            raise ValueError(
                f"El salario no puede ser inferior al mínimo de referencia "
                f"(${_SALARIO_MINIMO:,.0f} COP)."
            )
        return v


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
    cargo: str | None = Field(default=None, min_length=2, max_length=100)
    salario: Decimal | None = Field(default=None, gt=Decimal("0"), max_digits=12, decimal_places=2)

    @field_validator("nombre", "apellido")
    @classmethod
    def validar_solo_letras(cls, v: str | None, info) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError(f"El campo '{info.field_name}' no puede estar vacío.")
        if not _NOMBRE_RE.match(v):
            raise ValueError(
                f"El campo '{info.field_name}' solo puede contener letras, "
                "espacios y guiones."
            )
        return v.title()

    @field_validator("cargo")
    @classmethod
    def validar_cargo(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if len(v) < 2:
            raise ValueError("El cargo debe tener al menos 2 caracteres significativos.")
        return v

    @field_validator("salario")
    @classmethod
    def validar_salario(cls, v: Decimal | None) -> Decimal | None:
        if v is None:
            return v
        if v < _SALARIO_MINIMO:
            raise ValueError(
                f"El salario no puede ser inferior al mínimo de referencia "
                f"(${_SALARIO_MINIMO:,.0f} COP)."
            )
        return v

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

    model_config = {"from_attributes": True}
