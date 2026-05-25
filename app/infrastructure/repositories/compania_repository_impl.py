"""
Implementación concreta del repositorio de Compañías.
Usa SQLAlchemy para acceder a PostgreSQL.
"""

from uuid import UUID
from typing import Optional, Sequence
from sqlalchemy.orm import Session

from app.domain.entities.compania import Compania
from app.domain.interfaces.compania_repository import ICompaniaRepository


class CompaniaRepositoryImpl(ICompaniaRepository):

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_all(self) -> Sequence[Compania]:
        return self._session.query(Compania).all()

    def get_by_id(self, compania_id: UUID) -> Optional[Compania]:
        return self._session.query(Compania).filter(Compania.id == compania_id).first()

    def create(self, compania: Compania) -> Compania:
        self._session.add(compania)
        self._session.flush()
        return compania

    def update(self, compania: Compania) -> Compania:
        self._session.flush()
        return compania

    def delete(self, compania_id: UUID) -> None:
        compania = self.get_by_id(compania_id)
        if compania:
            self._session.delete(compania)