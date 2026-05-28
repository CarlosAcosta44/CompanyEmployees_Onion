"""Implementacion SQLAlchemy del repositorio de empleados."""

from uuid import UUID
from typing import Optional, Sequence
from sqlalchemy.orm import Session

from app.domain.entities.empleado import Empleado
from app.domain.interfaces.empleado_repository import IEmpleadoRepository
from app.infrastructure.database.models import EmpleadoModel
from app.infrastructure.repositories.mappers import apply_empleado, empleado_to_domain, empleado_to_model


class EmpleadoRepositoryImpl(IEmpleadoRepository):

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_all(self) -> Sequence[Empleado]:
        modelos = self._session.query(EmpleadoModel).all()
        return [empleado_to_domain(modelo) for modelo in modelos]

    def get_by_id(self, empleado_id: UUID) -> Optional[Empleado]:
        modelo = self._session.get(EmpleadoModel, empleado_id)
        return empleado_to_domain(modelo) if modelo else None

    def get_by_correo(self, correo: str) -> Optional[Empleado]:
        modelo = self._session.query(EmpleadoModel).filter(EmpleadoModel.correo == correo.strip().lower()).first()
        return empleado_to_domain(modelo) if modelo else None

    def get_by_compania(self, compania_id: UUID) -> Sequence[Empleado]:
        modelos = self._session.query(EmpleadoModel).filter(EmpleadoModel.compania_id == compania_id).all()
        return [empleado_to_domain(modelo) for modelo in modelos]

    def create(self, empleado: Empleado) -> Empleado:
        self._session.add(empleado_to_model(empleado))
        return empleado

    def update(self, empleado: Empleado) -> Empleado:
        modelo = self._session.get(EmpleadoModel, empleado.id)
        if modelo:
            apply_empleado(empleado, modelo)
        return empleado

    def delete(self, empleado_id: UUID) -> None:
        modelo = self._session.get(EmpleadoModel, empleado_id)
        if modelo:
            self._session.delete(modelo)

    def find_by_condition(
        self,
        *,
        compania_id: UUID | None = None,
        correo: str | None = None,
        cargo: str | None = None,
    ) -> Sequence[Empleado]:
        query = self._session.query(EmpleadoModel)
        if compania_id is not None:
            query = query.filter(EmpleadoModel.compania_id == compania_id)
        if correo is not None:
            query = query.filter(EmpleadoModel.correo == correo.strip().lower())
        if cargo is not None:
            query = query.filter(EmpleadoModel.cargo.ilike(f"%{cargo.strip()}%"))
        return [empleado_to_domain(modelo) for modelo in query.all()]
