"""
Paquete: app.domain.interfaces

Exporta los contratos abstractos de persistencia y transaccionalidad
que forman el núcleo del patrón Repository + Unit of Work.

Ninguna implementación concreta de infraestructura (SQLAlchemy, etc.)
debe residir en este paquete.
"""

from app.domain.interfaces.compania_repository import ICompaniaRepository
from app.domain.interfaces.empleado_repository import IEmpleadoRepository
from app.domain.interfaces.unit_of_work import IUnitOfWork

__all__ = [
    "ICompaniaRepository",
    "IEmpleadoRepository",
    "IUnitOfWork",
]
