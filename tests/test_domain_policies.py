"""Pruebas de politicas de dominio."""

import pytest

from app.domain.exceptions import ConflictError
from app.domain.policies.unicidad_correo import asegurar_correos_unicos_en_solicitud


def test_asegurar_correos_unicos_normaliza_y_acepta_lista_valida() -> None:
    resultado = asegurar_correos_unicos_en_solicitud([" Ana@Mail.COM ", "bob@test.com"])
    assert resultado == ["ana@mail.com", "bob@test.com"]


def test_asegurar_correos_unicos_rechaza_duplicados_en_solicitud() -> None:
    with pytest.raises(ConflictError):
        asegurar_correos_unicos_en_solicitud(["dup@test.com", "DUP@test.com"])
