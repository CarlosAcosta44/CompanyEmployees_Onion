"""Carga de configuracion externa.

El motor de BD se selecciona con DATABASE_URL (PostgreSQL o SQLite).
Por defecto SQLite para entornos sin credenciales locales de PostgreSQL.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "API Compañias y Empleados"
    debug: bool = False
    database_url: str = "sqlite:///./database.db"  # SENA / local sin PostgreSQL

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
