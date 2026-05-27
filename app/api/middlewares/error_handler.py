"""
Middleware global de manejo de errores.
"""

import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.domain.exceptions import ConflictError, DomainValidationError, EntityNotFoundError, PersistenceError

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except EntityNotFoundError as e:
            logger.warning("[ErrorHandler] NotFound: %s", str(e))
            return JSONResponse(status_code=404, content={"detail": str(e)})
        except ConflictError as e:
            logger.warning("[ErrorHandler] Conflict: %s", str(e))
            return JSONResponse(status_code=409, content={"detail": str(e)})
        except DomainValidationError as e:
            logger.warning("[ErrorHandler] DomainValidation: %s", str(e))
            return JSONResponse(status_code=400, content={"detail": str(e)})
        except PersistenceError as e:
            logger.error("[ErrorHandler] PersistenceError: %s", str(e))
            return JSONResponse(status_code=500, content={"detail": str(e)})
        except Exception as e:
            logger.error("[ErrorHandler] Error inesperado: %s", str(e))
            return JSONResponse(status_code=500, content={"detail": "Error interno del servidor."})
