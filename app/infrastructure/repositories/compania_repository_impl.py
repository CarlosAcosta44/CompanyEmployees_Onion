"""Implementacion SQLAlchemy del repositorio de companias."""

from uuid import UUID
from typing import Optional, Sequence
from sqlalchemy.orm import Session

from app.domain.entities.compania import Compania
from app.domain.interfaces.compania_repository import ICompaniaRepository
from app.infrastructure.database.models import CompaniaModel
from app.infrastructure.repositories.mappers import apply_compania, compania_to_domain, compania_to_model


class CompaniaRepositoryImpl(ICompaniaRepository):

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_all(self) -> Sequence[Compania]:
        modelos = self._session.query(CompaniaModel).all()
        return [compania_to_domain(modelo) for modelo in modelos]

    def get_by_id(self, compania_id: UUID) -> Optional[Compania]:
        modelo = self._session.get(CompaniaModel, compania_id)
        return compania_to_domain(modelo) if modelo else None

    def create(self, compania: Compania) -> Compania:
        self._session.add(compania_to_model(compania))
        return compania

    def update(self, compania: Compania) -> Compania:
        modelo = self._session.get(CompaniaModel, compania.id)
        if modelo:
            apply_compania(compania, modelo)
        return compania

    def delete(self, compania_id: UUID) -> None:
        modelo = self._session.get(CompaniaModel, compania_id)
        if modelo:
            self._session.delete(modelo)

    def find_by_condition(
        self,
        *,
        nombre: str | None = None,
        telefono: str | None = None,
    ) -> Sequence[Compania]:
        query = self._session.query(CompaniaModel)
        if nombre is not None:
            query = query.filter(CompaniaModel.nombre.ilike(f"%{nombre.strip()}%"))
        if telefono is not None:
            query = query.filter(CompaniaModel.telefono == telefono.strip())
        return [compania_to_domain(modelo) for modelo in query.all()]

    def get_paged(
        self,
        pagina: int,
        tamano: int,
        orden: str | None = None,
        dir: str | None = None,
        buscar: str | None = None,
    ) -> tuple[Sequence[Compania], int]:
        from sqlalchemy import or_, desc, asc
        
        query = self._session.query(CompaniaModel)
        
        if buscar:
            termino = f"%{buscar.strip()}%"
            query = query.filter(
                or_(
                    CompaniaModel.nombre.ilike(termino),
                    CompaniaModel.direccion.ilike(termino),
                    CompaniaModel.telefono.ilike(termino)
                )
            )
            
        total = query.count()
        
        if orden:
            columna = getattr(CompaniaModel, orden, None)
            if columna is not None:
                if dir and dir.lower() == 'desc':
                    query = query.order_by(desc(columna))
                else:
                    query = query.order_by(asc(columna))
                    
        modelos = query.offset((pagina - 1) * tamano).limit(tamano).all()
        return [compania_to_domain(m) for m in modelos], total
