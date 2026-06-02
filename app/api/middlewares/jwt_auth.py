"""
Middleware global de autenticación JWT.

Verifica el token JWT enviado en la cabecera 'Authorization' para todas las peticiones
de la API, excluyendo rutas públicas como registro, login y la documentación interactiva.
"""

from __future__ import annotations
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError

logger = logging.getLogger(__name__)


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Middleware para interceptar peticiones y validar tokens JWT."""

    def __init__(self, app, jwt_secret_key: str, jwt_algorithm: str):
        super().__init__(app)
        self._jwt_secret_key = jwt_secret_key
        self._jwt_algorithm = jwt_algorithm

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Excluir rutas públicas del chequeo de token
        if (
            path == "/"
            or path.startswith("/docs")
            or path.startswith("/redoc")
            or path.startswith("/openapi.json")
            or path == "/api/auth/registro"
            or path == "/api/auth/login"
        ):
            return await call_next(request)

        auth_header = request.headers.get("Authorization") or request.cookies.get("access_token")
        if not auth_header:
            logger.warning("[JWTAuthMiddleware] Petición rechazada: Cabecera/Cookie Authorization ausente.")
            return JSONResponse(
                status_code=401,
                content={
                    "status": 401,
                    "error": "No autorizado",
                    "mensaje": "Cabecera de autorización Bearer faltante.",
                },
            )

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            logger.warning("[JWTAuthMiddleware] Petición rechazada: Cabecera Authorization con formato inválido.")
            return JSONResponse(
                status_code=401,
                content={
                    "status": 401,
                    "error": "No autorizado",
                    "mensaje": "El token de autorización debe tener el formato 'Bearer <token>'.",
                },
            )

        token = parts[1]

        try:
            payload = jwt.decode(
                token,
                self._jwt_secret_key,
                algorithms=[self._jwt_algorithm],
            )
            # Guardar payload en request.state para consumo en dependencias
            request.state.user = payload
        except jwt.ExpiredSignatureError:
            logger.warning("[JWTAuthMiddleware] Petición rechazada: El token ha expirado.")
            return JSONResponse(
                status_code=401,
                content={
                    "status": 401,
                    "error": "No autorizado",
                    "mensaje": "El token de acceso ha expirado.",
                },
            )
        except JWTError as exc:
            logger.warning("[JWTAuthMiddleware] Petición rechazada: Token JWT inválido: %s", str(exc))
            return JSONResponse(
                status_code=401,
                content={
                    "status": 401,
                    "error": "No autorizado",
                    "mensaje": "Token de acceso inválido.",
                },
            )

        return await call_next(request)
