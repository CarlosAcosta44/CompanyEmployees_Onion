"""
Punto de entrada de la aplicación FastAPI.
"""

import logging
from fastapi import FastAPI
from app.api.middlewares.error_handler import ErrorHandlerMiddleware
from app.api.controllers.companias_controller import router as companias_router
from app.api.controllers.empleados_controller import router as empleados_router
from app.infrastructure.config.settings import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="API REST con Onion Architecture, FastAPI, PostgreSQL y SQLite.",
    version="1.0.0",
)

app.add_middleware(ErrorHandlerMiddleware)

app.include_router(companias_router, prefix="/api")
app.include_router(empleados_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "API Compañías y Empleados funcionando correctamente."}
