"""Validaciones pequenas reutilizables dentro del dominio."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
import re

from app.domain.exceptions import DomainValidationError


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def ensure_required_text(
    value: str,
    field_name: str,
    *,
    min_length: int = 1,
    max_length: int,
) -> str:
    value = value.strip() if isinstance(value, str) else ""
    if len(value) < min_length:
        raise DomainValidationError(f"El campo '{field_name}' es obligatorio.")
    if len(value) > max_length:
        raise DomainValidationError(f"El campo '{field_name}' no puede superar {max_length} caracteres.")
    return value


def ensure_email(value: str) -> str:
    email = value.strip().lower() if isinstance(value, str) else ""
    if len(email) > 150 or not EMAIL_PATTERN.match(email):
        raise DomainValidationError("El correo electronico no es valido.")
    return email


def ensure_positive_decimal(
    value: Decimal | int | float | str,
    field_name: str,
    *,
    max_digits: int,
    decimal_places: int,
) -> Decimal:
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise DomainValidationError(f"El campo '{field_name}' debe ser numerico.") from exc

    if decimal_value <= 0:
        raise DomainValidationError(f"El campo '{field_name}' debe ser mayor que cero.")

    exponent = abs(decimal_value.as_tuple().exponent)
    digits = len(decimal_value.as_tuple().digits)
    if exponent > decimal_places or digits > max_digits:
        raise DomainValidationError(
            f"El campo '{field_name}' debe tener maximo {max_digits} digitos y {decimal_places} decimales."
        )
    return decimal_value
