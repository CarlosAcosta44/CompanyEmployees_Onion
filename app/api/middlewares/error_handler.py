"""
Middleware global de manejo de errores de dominio.

Captura excepciones de la capa de dominio y las convierte en
respuestas JSON con formato estructurado uniforme.
"""

import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.domain.exceptions import (
    ConflictError,
    DomainValidationError,
    EntityNotFoundError,
    PersistenceError,
    AuthenticationError,
    ForbiddenError,
)

logger = logging.getLogger(__name__)


def _respuesta_error(status: int, error: str, mensaje: str) -> dict:
    """Formato JSON estructurado estándar para errores de dominio."""
    return {
        "status": status,
        "error": error,
        "mensaje": mensaje,
    }


class ErrorHandlerMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except EntityNotFoundError as e:
            logger.warning("[ErrorHandler] NotFound: %s", str(e))
            return JSONResponse(
                status_code=404,
                content=_respuesta_error(404, "Recurso no encontrado", str(e)),
            )
        except AuthenticationError as e:
            logger.warning("[ErrorHandler] Unauthorized: %s", str(e))
            return JSONResponse(
                status_code=401,
                content=_respuesta_error(401, "No autorizado", str(e)),
            )
        except ForbiddenError as e:
            logger.warning("[ErrorHandler] Forbidden: %s", str(e))
            return JSONResponse(
                status_code=403,
                content=_respuesta_error(403, "Acceso denegado", str(e)),
            )
        except ConflictError as e:
            logger.warning("[ErrorHandler] Conflict: %s", str(e))
            return JSONResponse(
                status_code=409,
                content=_respuesta_error(409, "Conflicto de datos", str(e)),
            )
        except DomainValidationError as e:
            logger.warning("[ErrorHandler] DomainValidation: %s", str(e))
            return JSONResponse(
                status_code=400,
                content=_respuesta_error(400, "Error de validación de dominio", str(e)),
            )
        except PersistenceError as e:
            logger.error("[ErrorHandler] PersistenceError: %s", str(e))
            return JSONResponse(
                status_code=500,
                content=_respuesta_error(500, "Error de persistencia", str(e)),
            )
        except Exception as e:
            logger.error("[ErrorHandler] Error inesperado: %s", str(e))
            return JSONResponse(
                status_code=500,
                content=_respuesta_error(500, "Error interno del servidor", "Ha ocurrido un error inesperado."),
            )
