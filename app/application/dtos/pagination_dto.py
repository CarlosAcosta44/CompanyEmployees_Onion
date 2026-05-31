"""
DTO genérico de paginación
"""
import math
from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    """
    Estructura estándar para respuestas paginadas.
    Envuelve una lista genérica de DTOs y añade metadatos de paginación.
    """
    datos: List[T] = Field(description="Lista de elementos en la página actual.")
    pagina: int = Field(description="Número de página actual (inicia en 1).")
    tamano: int = Field(description="Cantidad de registros devueltos por página.")
    total: int = Field(description="Total absoluto de registros que coinciden.")
    total_paginas: int = Field(description="Total de páginas calculadas.")

    @classmethod
    def create(cls, datos: List[T], pagina: int, tamano: int, total: int) -> "PaginatedResponse[T]":
        """Calcula el total de páginas y construye el DTO."""
        total_paginas = math.ceil(total / tamano) if tamano > 0 else 0
        return cls(
            datos=datos,
            pagina=pagina,
            tamano=tamano,
            total=total,
            total_paginas=total_paginas
        )
