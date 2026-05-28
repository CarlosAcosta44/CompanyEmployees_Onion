"""Politicas de dominio reutilizables."""

from app.domain.policies.unicidad_correo import asegurar_correos_unicos_en_solicitud

__all__ = ["asegurar_correos_unicos_en_solicitud"]
