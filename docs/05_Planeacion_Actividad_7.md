# Planeación de la Actividad 7: Construcción de una API REST (Parte II)

Esta planeación sigue las prácticas de **Gitflow**, **Git Semántico (Conventional Commits)** y **SemVer**. El trabajo se divide equilibradamente entre dos desarrolladores, garantizando que el flujo de trabajo avance correctamente por módulos.

El proyecto es una continuación de nuestra arquitectura hexagonal / cebolla basada en Python y FastAPI.

---

## Estrategia de Ramas (Gitflow)

Todas las ramas de trabajo se desprenderán de `develop`. Al finalizar un módulo, se creará un Pull Request hacia `develop`. Opcionalmente, cada desarrollador puede subdividir en `feat/`, `fix/`, `docs/`, `test/`.

### Ramas Generales
- `main`: Código de producción estable (producción).
- `develop`: Código de integración principal.
- `release/*`: Ramas para preparar una versión final hacia `main` (ej. `release/v2.0.0`).

---

## División del Trabajo

Cada desarrollador asumirá la responsabilidad de Módulos específicos. Aquí están las ramas recomendadas para cada uno:

### Desarrollador 1 (Dev1)
Responsable de extender el alcance de la capa de datos (operaciones masivas), paginación y validaciones clave, sentando la base de integración.

1. **Módulo 1: CRUD completo: objetos y colecciones (Paginación, Filtros, Ordenamiento y Bulk)**
   - **Rama principal:** `feature/module-1-collections`
   - **Tareas:**
     - Extender `ICompaniaRepository` e `IEmpleadoRepository` para `CreateRange`, `GetPaged`, `PatchPartial`, `DeleteRange`.
     - Implementar listado avanzado, aplicando filtros y limits.
     - Ajustar los Controllers en FastAPI para endpoints masivos (`/api/empleados/lote`).
   - **Commits esperados:** `feat: agregar paginacion a empleados`, `feat: implementacion bulk insert`

2. **Módulo 2: Programación asíncrona**
   - **Rama principal:** `feature/module-2-async-refactor`
   - **Tareas:**
     - Refactorizar las operaciones ORM de SQLAlchemy a la sesión asíncrona (`AsyncSession`).
     - Actualizar el Unit of Work para soportar métodos asíncronos (`await uow.commit()`).
   - **Commits esperados:** `refactor: migracion de repositorio a async`

3. **Módulo 3: Validaciones**
   - **Rama principal:** `feature/module-3-validations`
   - **Tareas:**
     - Implementar las reglas usando **Pydantic** (`field_validator`).
     - Controlar errores globalmente con exception handlers devolviendo un formato estructurado en JSON 422 HTTP request.
   - **Commits esperados:** `feat: anadir reglas de validacion para esquema de compania`

---

### Desarrollador 2 (Dev2)
Responsable de asegurar la calidad a través de pruebas unitarias/integración, además de la implementación del ecosistema de seguridad (JWT, roles y policies).

1. **Módulo 4: Pruebas (Unitarias y de Integración)**
   - **Rama principal:** `feature/module-4-tests`
   - **Tareas:**
     - Integrar un TestClient de FastAPI (`httpx` + `pytest`).
     - Incluir BD efímera para pruebas con Pytest fixtures.
     - Realizar las pruebas transaccionales del Caso de Crear Compañía con empleados defectuosos que detonen el *Rollback*.
   - **Commits esperados:** `test: agregar prueba transaccional de rollback`, `test: prueba unitaria empleado service`

2. **Módulo 5: Seguridad - JWT orientado a Roles**
   - **Rama principal:** `feature/module-5-jwt-roles`
   - **Tareas:**
     - Emplear librerías como `python-jose` y `passlib` (OAuth2PasswordBearer).
     - Entidades nuevas (Usuario) y Hashing de contraseñas.
     - Configurar `AuthService` (Registro y Login).
     - Implementar Guard / Middleware de validación del token `Authorization: Bearer <token>`.
   - **Commits esperados:** `feat: implementar hashing de contraseñas y esquema usuario`

3. **Módulo 6: Seguridad - JWT orientado a Políticas**
   - **Rama principal:** `feature/module-6-jwt-policies`
   - **Tareas:**
     - Migración de autorización por perfiles (roles) a políticas mediante claims y dependencias avanzadas en FastAPI (`Depends(evaluar_claims)`).
     - Validación del propietario ("Ownership" `EsPropietarioDeCompania`).
   - **Commits esperados:** `feat: dependencia de fastapi para validacion de propiedad`

---

## Flujo de Trabajo Semántico

1. **Ramas Descriptivas:** Usa `feature/` u `hotfix/` o `test/` seguido de la tarea puntual.
2. **Commit Semantics:**
   - `build:`, `chore:`, `ci:`, `docs:`, `style:`, `refactor:`, `perf:`, `test:`, `feat:`, `fix:`.
3. **Pull Requests:** Antes de hacer merge a `develop`, enviar PR para aprobación del trabajo del otro desarrollador asegurando cohesión en Onion Architecture.
4. **SemVer:** Si toda esta actividad concluye y es un avance significativo en retrocompatibilidad, considerar un tag versión `v2.0.0` para Producción (Part II).
