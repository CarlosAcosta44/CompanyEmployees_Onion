"""Pruebas del agregado Compania."""

from decimal import Decimal
from uuid import uuid4

import pytest

from app.domain.entities.compania import Compania
from app.domain.entities.empleado import Empleado
from app.domain.exceptions import DomainValidationError


def test_agregar_empleado_rechaza_compania_id_incorrecto() -> None:
    compania = Compania(nombre="ACME", direccion="Calle 1", telefono="3001234567")
    empleado = Empleado(
        nombre="Ana",
        apellido="Lopez",
        correo="ana@acme.com",
        cargo="Dev",
        salario=Decimal("3000000"),
        compania_id=uuid4(),
    )

    with pytest.raises(DomainValidationError):
        compania.agregar_empleado(empleado)
