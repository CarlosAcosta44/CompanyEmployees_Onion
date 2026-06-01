"""Excepciones propias del nucleo de la aplicacion."""


class DomainError(Exception):
    """Base para errores que no dependen del transporte HTTP."""


class DomainValidationError(DomainError):
    """Una entidad o valor no cumple una invariante del dominio."""


class EntityNotFoundError(DomainError):
    """Un recurso requerido por un caso de uso no existe."""


class ConflictError(DomainError):
    """La operacion viola una regla de unicidad o consistencia."""


class PersistenceError(DomainError):
    """La persistencia fallo y no se debe exponer el detalle tecnico."""


class AuthenticationError(DomainError):
    """Fallo en la autenticación o token inválido."""


class ForbiddenError(DomainError):
    """El usuario autenticado no tiene permisos suficientes para el recurso."""

