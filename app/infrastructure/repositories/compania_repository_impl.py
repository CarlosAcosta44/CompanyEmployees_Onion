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
