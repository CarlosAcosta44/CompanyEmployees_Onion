from sqlalchemy import Column, String, Integer, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.infrastructure.database.models import Base

class Empleado(Base):
    __tablename__ = "empleados"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    correo = Column(String, nullable=False, unique=True)
    cargo = Column(String, nullable=False)
    salario = Column(Float, nullable=False)
    compania_id = Column(UUID(as_uuid=True), ForeignKey("companias.id"), nullable=False)

    compania = relationship("Compania", back_populates="empleados")
