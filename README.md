# CompanyEmployees Onion

API REST de companias y empleados construida con FastAPI, SQLAlchemy, Alembic,
Repository Pattern y Unit of Work siguiendo Onion Architecture.

## Arquitectura

La regla principal del proyecto es que las dependencias apuntan hacia el
nucleo:

```text
API / Presentation
        -> Application
        -> Domain

Infrastructure
        -> Application / Domain
```

Capas:

- `app/domain`: entidades puras, validaciones de dominio, excepciones e interfaces.
- `app/application`: servicios de aplicacion y DTOs Pydantic.
- `app/infrastructure`: SQLAlchemy, conexion, modelos ORM, repositorios y Unit of Work concreto.
- `app/api`: FastAPI, controladores, dependencias y middleware de errores.

El dominio no importa SQLAlchemy, FastAPI, Pydantic ni infraestructura.

## Base de datos

El proyecto soporta PostgreSQL y SQLite mediante `DATABASE_URL`.

PostgreSQL, recomendado para el entorno principal con pgAdmin 4:

```env
DATABASE_URL=postgresql://postgres:TU_CLAVE@localhost:5432/db_companias
```

SQLite, util cuando no se tiene la clave local de PostgreSQL:

```env
DATABASE_URL=sqlite:///./database.db
```

SQLite activa `PRAGMA foreign_keys=ON` desde la conexion para respetar llaves
foraneas y cascadas durante pruebas locales.

## Ejecucion

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.api.main:app --reload
```

Swagger queda disponible en:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

- `GET /api/companias`
- `GET /api/companias/{compania_id}`
- `GET /api/companias/{compania_id}/empleados`
- `POST /api/companias`
- `POST /api/companias/con-empleados`
- `PUT /api/companias/{compania_id}`
- `DELETE /api/companias/{compania_id}`
- `GET /api/empleados`
- `GET /api/empleados/{empleado_id}`
- `GET /api/empleados/compania/{compania_id}`
- `POST /api/empleados`
- `PUT /api/empleados/{empleado_id}`
- `DELETE /api/empleados/{empleado_id}`

## Unit of Work

`UnitOfWorkImpl` abre una sesion de SQLAlchemy, entrega repositorios que
comparten esa sesion y centraliza `commit()` / `rollback()`. Los repositorios
no hacen `commit`; solo agregan, consultan, actualizan o eliminan modelos.

El caso `POST /api/companias/con-empleados` crea una compania y varios
empleados en una sola transaccion. Si un correo esta duplicado o falla una
restriccion de integridad, se revierte toda la operacion.

## Pruebas

```bash
pytest -q
```

Pruebas incluidas:

- Verificacion de que `domain` no importa frameworks ni capas externas.
- Verificacion del rollback completo en el caso transaccional obligatorio.
- Contrato basico del endpoint raiz.
