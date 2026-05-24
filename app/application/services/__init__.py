"""
Paquete: app.application.services

Exporta los servicios de aplicación que implementan los casos de uso
del sistema. Solo dependen de interfaces abstractas (IUnitOfWork),
no de implementaciones concretas de infraestructura.
"""

from app.application.services.empleado_service import EmpleadoService
from app.application.services.compania_service import CompaniaService

__all__ = [
    "EmpleadoService",
    "CompaniaService",
]
