from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.infrastructure.database.models import Base

class Compania(Base):
    __tablename__ = "companias"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String, nullable=False)
    direccion = Column(String, nullable=False)
    telefono = Column(String, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    empleados = relationship("Empleado", back_populates="compania", cascade="all, delete-orphan")
