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

    def create_range(self, empleados: Sequence[Empleado]) -> Sequence[Empleado]:
        modelos = [empleado_to_model(emp) for emp in empleados]
        self._session.add_all(modelos)
        return empleados

    def delete_range(self, empleado_ids: Sequence[UUID]) -> None:
        self._session.query(EmpleadoModel).filter(
            EmpleadoModel.id.in_(empleado_ids)
        ).delete(synchronize_session=False)

    def get_paged(
        self,
        pagina: int,
        tamano: int,
        orden: str | None = None,
        dir: str | None = None,
        buscar: str | None = None,
        compania_id: UUID | None = None,
    ) -> tuple[Sequence[Empleado], int]:
        from sqlalchemy import or_, desc, asc
        
        query = self._session.query(EmpleadoModel)
        
        if compania_id is not None:
            query = query.filter(EmpleadoModel.compania_id == compania_id)
            
        if buscar:
            termino = f"%{buscar.strip()}%"
            query = query.filter(
                or_(
                    EmpleadoModel.nombre.ilike(termino),
                    EmpleadoModel.apellido.ilike(termino),
                    EmpleadoModel.correo.ilike(termino)
                )
            )
            
        total = query.count()
        
        if orden:
            columna = getattr(EmpleadoModel, orden, None)
            if columna is not None:
                if dir and dir.lower() == 'desc':
                    query = query.order_by(desc(columna))
                else:
                    query = query.order_by(asc(columna))
                    
        modelos = query.offset((pagina - 1) * tamano).limit(tamano).all()
        return [empleado_to_domain(m) for m in modelos], total

    def patch_partial(self, empleado_id: UUID, cambios: dict) -> Optional[Empleado]:
        modelo = self._session.get(EmpleadoModel, empleado_id)
        if not modelo:
            return None
            
        for key, value in cambios.items():
            if hasattr(modelo, key) and key != 'id':
                setattr(modelo, key, value)
                
        return empleado_to_domain(modelo)
