"""
Punto de entrada de la aplicación FastAPI.
"""

import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.api.middlewares.error_handler import ErrorHandlerMiddleware
from app.api.controllers.companias_controller import router as companias_router
from app.api.controllers.empleados_controller import router as empleados_router
from app.composition_root import get_app_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)
settings = get_app_settings()

app = FastAPI(
    title=settings.app_name,
    description="API REST con Onion Architecture, FastAPI, PostgreSQL y SQLite.",
    version="2.0.0",
)

app.add_middleware(ErrorHandlerMiddleware)


# ------------------------------------------------------------------ #
#  Handlers de errores de validación (HTTP 422)                        #
# ------------------------------------------------------------------ #

def _formatear_errores(errors: list) -> list[dict]:
    """Transforma los errores de Pydantic en un formato estructurado uniforme."""
    resultado = []
    for error in errors:
        campo = " → ".join(str(loc) for loc in error.get("loc", []))
        resultado.append({
            "campo": campo,
            "mensaje": error.get("msg", "Error de validación."),
            "tipo": error.get("type", "validation_error"),
        })
    return resultado


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Captura errores de validación de FastAPI/Pydantic (422 Unprocessable Entity)
    y devuelve un JSON estructurado con detalles por campo.
    """
    logger.warning("[ValidationHandler] Error 422 en %s %s", request.method, request.url.path)
    errores = _formatear_errores(exc.errors())
    return JSONResponse(
        status_code=422,
        content={
            "status": 422,
            "error": "Error de validación",
            "mensaje": "Los datos enviados no cumplen las reglas requeridas.",
            "errores": errores,
        },
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Captura errores de ValidationError de Pydantic lanzados fuera del ciclo
    de request (e.g., construcción manual de modelos).
    """
    logger.warning("[ValidationHandler] Pydantic ValidationError: %s", str(exc))
    errores = _formatear_errores(exc.errors())
    return JSONResponse(
        status_code=422,
        content={
            "status": 422,
            "error": "Error de validación",
            "mensaje": "Los datos no son válidos.",
            "errores": errores,
        },
    )


# ------------------------------------------------------------------ #
#  Routers                                                             #
# ------------------------------------------------------------------ #

app.include_router(companias_router, prefix="/api")
app.include_router(empleados_router, prefix="/api")


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "API Compañías y Empleados funcionando correctamente."}
