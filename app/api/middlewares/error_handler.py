"""
Middleware global de manejo de errores.
"""

import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except ValueError as e:
            logger.warning("[ErrorHandler] ValueError: %s", str(e))
            return JSONResponse(status_code=404, content={"detail": str(e)})
        except Exception as e:
            logger.error("[ErrorHandler] Error inesperado: %s", str(e))
            return JSONResponse(status_code=500, content={"detail": "Error interno del servidor."})