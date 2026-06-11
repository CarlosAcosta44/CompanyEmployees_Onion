# Usar una imagen base de Python oficial y ligera
FROM python:3.11-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para psycopg2 y otras librerías
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos
COPY requirements.txt .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Exponer el puerto en el que correrá FastAPI (Azure App Service usa el 8000 por defecto para contenedores)
EXPOSE 8000

# Comando para ejecutar la aplicación usando Gunicorn con workers de Uvicorn para producción
CMD ["sh", "-c", "alembic upgrade head && gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.api.main:app --bind 0.0.0.0:8000"]
