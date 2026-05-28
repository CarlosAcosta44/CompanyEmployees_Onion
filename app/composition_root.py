"""
Composition root: unico punto de ensamblaje entre capas.

Las capas externas (API) dependen de abstracciones expuestas aqui;
solo este modulo conoce implementaciones concretas de infraestructura.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import lru_cache

from sqlalchemy.orm import Session

from app.application.services.compania_service import CompaniaService
from app.application.services.empleado_service import EmpleadoService
from app.domain.interfaces.unit_of_work import IUnitOfWork
from app.infrastructure.config.settings import Settings, get_settings
from app.infrastructure.database.connection import SessionLocal
from app.infrastructure.unit_of_work.unit_of_work_impl import UnitOfWorkImpl


@lru_cache
def get_app_settings() -> Settings:
    return get_settings()


def build_unit_of_work(session_factory: Callable[[], Session] | None = None) -> IUnitOfWork:
    return UnitOfWorkImpl(session_factory or SessionLocal)


def build_compania_service(uow: IUnitOfWork | None = None) -> CompaniaService:
    return CompaniaService(uow or build_unit_of_work())


def build_empleado_service(uow: IUnitOfWork | None = None) -> EmpleadoService:
    return EmpleadoService(uow or build_unit_of_work())
