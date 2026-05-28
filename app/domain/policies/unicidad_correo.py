"""Reglas de unicidad de correo dentro del dominio."""

from __future__ import annotations

from collections.abc import Iterable

from app.domain.exceptions import ConflictError


def asegurar_correos_unicos_en_solicitud(correos: Iterable[str]) -> list[str]:
    """
    Normaliza correos y garantiza que no se repitan en la misma solicitud.

    Returns:
        Lista de correos normalizados (minusculas, sin espacios extremos).
    """

    normalizados: list[str] = []
    vistos: set[str] = set()

    for correo in correos:
        normalizado = correo.strip().lower()
        if normalizado in vistos:
            raise ConflictError(f"El correo '{normalizado}' esta duplicado en la solicitud.")
        vistos.add(normalizado)
        normalizados.append(normalizado)

    return normalizados
