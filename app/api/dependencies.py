"""
Dependencias de FastAPI.

La capa API solo consume el composition root; no referencia
implementaciones concretas de infraestructura.
"""

from app.application.services.compania_service import CompaniaService
from app.application.services.empleado_service import EmpleadoService
from app.composition_root import build_compania_service, build_empleado_service
from app.domain.interfaces.unit_of_work import IUnitOfWork


def get_unit_of_work() -> IUnitOfWork:
    from app.composition_root import build_unit_of_work

    return build_unit_of_work()


def get_compania_service() -> CompaniaService:
    return build_compania_service()


def get_empleado_service() -> EmpleadoService:
    return build_empleado_service()
