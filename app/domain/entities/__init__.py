"""
Paquete de entidades de dominio.

Exporta los modelos SQLAlchemy del núcleo del dominio para facilitar
los imports desde otras capas de la arquitectura.

Uso:
    from app.domain.entities import Compania, Empleado
"""

from app.domain.entities.compania import Compania
from app.domain.entities.empleado import Empleado

__all__ = ["Compania", "Empleado"]
