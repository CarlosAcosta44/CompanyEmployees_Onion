# API de Compañías y Empleados

API REST de compañías y empleados con **FastAPI**, **SQLAlchemy**, **Alembic**, **Repository Pattern**, **Unit of Work** y **Onion Architecture**.

## Tecnología usada

| Componente | Elección |
|------------|----------|
| Lenguaje | Python 3.11+ |
| Framework HTTP | FastAPI |
| ORM | SQLAlchemy 2.x |
| Migraciones | Alembic |
| Validación de entrada | Pydantic v2 |
| Motor principal (documentado) | PostgreSQL + pgAdmin 4 |
| Motor alternativo (laboratorio SENA) | SQLite (archivo local) |

## ORM usado

**SQLAlchemy** — define modelos en infraestructura, relaciones 1:N, migraciones con Alembic y transacciones mediante `Session`. El patrón Unit of Work se implementa explícitamente en `UnitOfWorkImpl` sobre una única sesión compartida por los repositorios.

## Arquitectura aplicada

**Onion Architecture** con dependencias hacia el núcleo:

```text
API (Presentation)
    -> Application (servicios, DTOs, mappers)
    -> Domain (entidades, políticas, interfaces)

Infrastructure
    -> Domain (implementa interfaces)

Composition Root (app/composition_root.py)
    -> ensambla Application + Infrastructure
```

| Capa | Responsabilidad |
|------|-----------------|
| `app/domain` | Entidades, validaciones, políticas, excepciones, interfaces de repositorio y UoW |
| `app/application` | Casos de uso (`*Service`), DTOs Pydantic, mappers explícitos |
| `app/infrastructure` | ORM, conexión, repositorios concretos, UoW concreto, seed |
| `app/api` | Controladores, middleware, dependencias FastAPI |
| `app/composition_root.py` | Único lugar que instancia implementaciones concretas |

**Regla obligatoria:** el controlador nunca accede al ORM ni a repositorios concretos.

```text
Controller -> Service -> UnitOfWork -> Repositories -> ORM -> Database
```

## Estructura del proyecto

```text
app/
├── composition_root.py      # Ensamblaje de dependencias
├── domain/
│   ├── entities/
│   ├── interfaces/          # ICompaniaRepository, IEmpleadoRepository, IUnitOfWork
│   ├── policies/
│   └── validation.py
├── application/
│   ├── dtos/
│   ├── mappers/
│   └── services/
├── infrastructure/
│   ├── config/
│   ├── database/
│   ├── repositories/
│   └── unit_of_work/
└── api/
    ├── controllers/
    ├── middlewares/
    └── dependencies.py
```

## Entidades

### Compañía

`Id`, `Nombre`, `Direccion`, `Telefono`, `FechaCreacion`

### Empleado

`Id`, `Nombre`, `Apellido`, `Correo` (único), `Cargo`, `Salario`, `CompaniaId`

## Relación entre entidades

```text
Compañía 1 ──── * Empleado
```

Eliminación en cascada configurada en el modelo ORM y en SQLite con `PRAGMA foreign_keys=ON`.

## Repository Pattern

Interfaces en dominio; implementaciones en `infrastructure/repositories/`.

| Método | Descripción |
|--------|-------------|
| `get_all` | Todos los registros |
| `get_by_id` | Por UUID |
| `create` | Alta (sin commit) |
| `update` | Actualización (sin commit) |
| `delete` | Baja (sin commit) |
| `find_by_condition` | Filtros opcionales (AND) |

Los repositorios **no** llaman a `commit`; solo el Unit of Work confirma la transacción.

## Unit of Work

### ¿Qué es Unit of Work?

Patrón que agrupa varias operaciones de persistencia en una **única unidad transaccional** coordinada.

### ¿Cómo se implementó en esta tecnología?

`UnitOfWorkImpl` abre una `Session` de SQLAlchemy, expone `uow.companias` y `uow.empleados`, y centraliza `commit()` / `rollback()`.

### ¿Cómo se manejan las transacciones?

```python
with uow:
    uow.companias.create(compania)
    uow.empleados.create(empleado)
    uow.commit()  # SaveChanges equivalente
```

Si ocurre una excepción antes del commit, `__exit__` ejecuta rollback.

### ¿Cómo se hace commit?

`uow.commit()` → `session.commit()`

### ¿Cómo se hace rollback?

Automático en `__exit__` si hubo error, o explícito con `uow.rollback()` → `session.rollback()`

### Equivalencia con Entity Framework

| EF Core | Este proyecto |
|---------|----------------|
| `DbContext` | `Session` + `UnitOfWorkImpl` |
| `SaveChanges()` | `uow.commit()` |
| `DbSet<T>` | Repositorios por entidad |
| `using` / transacción | `with uow:` |

## Endpoints

### Compañías

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/companias` | Listar |
| GET | `/api/companias/{id}` | Detalle |
| GET | `/api/companias/{id}/empleados` | Empleados de la compañía |
| POST | `/api/companias` | Crear |
| POST | `/api/companias/con-empleados` | Crear compañía + empleados (transaccional) |
| PUT | `/api/companias/{id}` | Actualizar (parcial, al menos un campo) |
| DELETE | `/api/companias/{id}` | Eliminar |

### Empleados

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/empleados` | Listar |
| GET | `/api/empleados/{id}` | Detalle |
| GET | `/api/empleados/compania/{compania_id}` | Por compañía |
| POST | `/api/empleados` | Crear |
| PUT | `/api/empleados/{id}` | Actualizar (parcial) |
| DELETE | `/api/empleados/{id}` | Eliminar |

## Endpoint transaccional

`POST /api/companias/con-empleados` — crea compañía y N empleados en una sola transacción. Si falla cualquier empleado (correo duplicado, validación, integridad), **no persiste nada**.

Prueba automatizada: `tests/test_transactional_uow.py`

## Instalación

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

## Configuración de base de datos

### PostgreSQL (entorno con pgAdmin 4)

```env
DATABASE_URL=postgresql://postgres:TU_CLAVE@localhost:5432/db_companias
```

Crear la base `db_companias` en pgAdmin antes de migrar.

### SQLite (laboratorio SENA — sin clave local de PostgreSQL)

```env
DATABASE_URL=sqlite:///./database.db
```

- El archivo `database.db` se crea en la raíz del proyecto.
- `connection.py` activa `PRAGMA foreign_keys=ON` para respetar FK y cascadas.
- **Misma API y mismo código**; solo cambia la variable de entorno.
- Alembic y la aplicación leen `DATABASE_URL` desde `.env`.

> **Recomendación:** en SENA use SQLite en `.env`. En casa o producción académica, PostgreSQL.

## Migraciones

```bash
alembic upgrade head
```

Crear nueva migración tras cambiar modelos ORM:

```bash
alembic revision --autogenerate -m "descripcion"
alembic upgrade head
```

## Datos iniciales (seed)

```bash
python -m app.infrastructure.database.seed_data
```

Inserta 3 compañías y 10 empleados (requiere tablas creadas).

## Ejecución del proyecto

```bash
uvicorn app.api.main:app --reload
```

Swagger: http://127.0.0.1:8000/docs

## Pruebas

```bash
pytest -q
```

| Prueba | Propósito |
|--------|-----------|
| `test_onion_architecture.py` | Límites de dependencias entre capas |
| `test_transactional_uow.py` | Rollback del caso transaccional |
| `test_domain_policies.py` | Políticas de dominio |
| `test_api_contract.py` | Contrato HTTP básico |

## Logging

Registros en servicios, UoW, controladores y `ErrorHandlerMiddleware` (inicio, transacciones, commit, rollback, errores).

## Uso de IA

Documentar en el informe del grupo los prompts de la guía de actividad (`docs/Actividad_API_REST_OnionArchitecture.md`).

## Conclusiones

La solución demuestra que Onion Architecture, Repository y Unit of Work son **independientes del lenguaje**: el dominio permanece puro, la aplicación orquesta casos de uso, la infraestructura adapta SQLAlchemy y la API solo expone HTTP. PostgreSQL y SQLite coexisten mediante configuración, lo que permite desarrollo en SENA sin credenciales locales de PostgreSQL.
