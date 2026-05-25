"""
Implementación concreta del repositorio de Empleados.
Usa SQLAlchemy para acceder a PostgreSQL.
"""

from uuid import UUID
from typing import Optional, Sequence
from sqlalchemy.orm import Session

from app.domain.entities.empleado import Empleado
from app.domain.interfaces.empleado_repository import IEmpleadoRepository


class EmpleadoRepositoryImpl(IEmpleadoRepository):

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_all(self) -> Sequence[Empleado]:
        return self._session.query(Empleado).all()

    def get_by_id(self, empleado_id: UUID) -> Optional[Empleado]:
        return self._session.query(Empleado).filter(Empleado.id == empleado_id).first()

    def get_by_compania(self, compania_id: UUID) -> Sequence[Empleado]:
        return self._session.query(Empleado).filter(Empleado.compania_id == compania_id).all()

    def create(self, empleado: Empleado) -> Empleado:
        self._session.add(empleado)
        self._session.flush()
        return empleado

    def update(self, empleado: Empleado) -> Empleado:
        self._session.flush()
        return empleado

    def delete(self, empleado_id: UUID) -> None:
        empleado = self.get_by_id(empleado_id)
        if empleado:
            self._session.delete(empleado)