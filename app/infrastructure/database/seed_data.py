"""
Script de datos iniciales (Seed Data).
Inserta compañías y empleados de prueba en PostgreSQL.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import logging
from dotenv import load_dotenv
load_dotenv()

from app.infrastructure.database.connection import SessionLocal
from app.domain.entities.compania import Compania
from app.domain.entities.empleado import Empleado

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed():
    session = SessionLocal()
    try:
        # Compañía 1
        c1 = Compania(nombre="TechCorp SAS", direccion="Calle 10 # 5-20, Bogotá", telefono="3001234567")
        c2 = Compania(nombre="Innovatech Ltda", direccion="Av. El Dorado # 68-50, Bogotá", telefono="3109876543")
        c3 = Compania(nombre="DataSolutions SA", direccion="Carrera 7 # 32-10, Medellín", telefono="3207654321")

        session.add_all([c1, c2, c3])
        session.flush()

        empleados = [
            Empleado(nombre="Carlos", apellido="Gómez", correo="carlos.gomez@techcorp.com", cargo="Desarrollador", salario=4500000, compania_id=c1.id),
            Empleado(nombre="Ana", apellido="Martínez", correo="ana.martinez@techcorp.com", cargo="QA Engineer", salario=3800000, compania_id=c1.id),
            Empleado(nombre="Luis", apellido="Pérez", correo="luis.perez@techcorp.com", cargo="DevOps", salario=5000000, compania_id=c1.id),
            Empleado(nombre="María", apellido="López", correo="maria.lopez@innovatech.com", cargo="Gerente de Proyectos", salario=6000000, compania_id=c2.id),
            Empleado(nombre="Jorge", apellido="Ramírez", correo="jorge.ramirez@innovatech.com", cargo="Diseñador UX", salario=3500000, compania_id=c2.id),
            Empleado(nombre="Sofía", apellido="Torres", correo="sofia.torres@innovatech.com", cargo="Analista de Datos", salario=4200000, compania_id=c2.id),
            Empleado(nombre="Andrés", apellido="Vargas", correo="andres.vargas@innovatech.com", cargo="Backend Developer", salario=4800000, compania_id=c2.id),
            Empleado(nombre="Valentina", apellido="Cruz", correo="valentina.cruz@datasolutions.com", cargo="Data Scientist", salario=5500000, compania_id=c3.id),
            Empleado(nombre="Miguel", apellido="Herrera", correo="miguel.herrera@datasolutions.com", cargo="DBA", salario=4700000, compania_id=c3.id),
            Empleado(nombre="Laura", apellido="Díaz", correo="laura.diaz@datasolutions.com", cargo="Frontend Developer", salario=4000000, compania_id=c3.id),
        ]

        session.add_all(empleados)
        session.commit()
        logger.info("Seed completado: 3 compañías y 10 empleados insertados.")

    except Exception as e:
        session.rollback()
        logger.error("Error en seed: %s", e)
    finally:
        session.close()


if __name__ == "__main__":
    seed()