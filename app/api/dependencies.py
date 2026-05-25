"""
Dependencias de FastAPI.
Provee las instancias del UoW y los servicios de aplicación.
"""

from app.infrastructure.unit_of_work.unit_of_work_impl import UnitOfWorkImpl
from app.application.services.compania_service import CompaniaService
from app.application.services.empleado_service import EmpleadoService


def get_unit_of_work() -> UnitOfWorkImpl:
    return UnitOfWorkImpl()


def get_compania_service() -> CompaniaService:
    return CompaniaService(get_unit_of_work())


def get_empleado_service() -> EmpleadoService:
    return EmpleadoService(get_unit_of_work())