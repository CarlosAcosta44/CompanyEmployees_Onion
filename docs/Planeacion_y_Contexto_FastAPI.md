# Planeación y Contexto: Migración a FastAPI (Onion Architecture)

Este documento consolida la planeación técnica y el contexto para la creación del proyecto **CompanyEmployees_Onion** utilizando Python, FastAPI y PostgreSQL, siguiendo estrictamente la arquitectura de cebolla (Onion Architecture).

---

## 1. Contexto Técnico e Identidad del Proyecto

### Equivalencias Tecnológicas (C# vs Python)

| Concepto en ASP.NET Core | Equivalente en Python / FastAPI |
| :--- | :--- |
| **Controller** | FastAPI Router / Controller |
| **Entity** | SQLAlchemy Base Model |
| **DbContext** | SQLAlchemy Session / Engine |
| **Migration** | Alembic |
| **Repository Pattern** | Repository Classes |
| **Unit of Work** | Session management / Custom UoW class |
| **Dependency Injection** | FastAPI `Depends()` |
| **Logging** | Python `logging` module |

### Metodología de Desarrollo
*   **Arquitectura:** Onion Architecture (4 capas).
*   **Gitflow:** Uso de ramas `main`, `develop`, `feature/*`.
*   **Git Semántico:** Commits siguiendo el estándar `type: description` (feat, fix, docs, style, etc.).
*   **Versionamiento Semántico:** Formato `MAJOR.MINOR.PATCH`.
*   **Base de Datos:** PostgreSQL con relación 1:N (Compañía : Empleados).

---

## 2. Arquitectura de Cebolla (Onion Architecture)

La solución se dividirá en 4 capas concéntricas:

1.  **Domain (Núcleo):** Entidades (`Compania`, `Empleado`) e interfaces de repositorios.
2.  **Application (Servicios):** Lógica de negocio, DTOs (Pydantic) y servicios que usan el Unit of Work.
3.  **Infrastructure:** Implementaciones de repositorios, configuración de SQLAlchemy, migraciones y Unit of Work.
4.  **API / Presentation:** Endpoints, middlewares de logging y manejo de errores.

---

## 3. Plan de Implementación

### Estructura de Carpetas Propuesta

```text
CompanyEmployees_Onion/
├── app/
│   ├── domain/
│   │   ├── entities/        # Modelos de dominio
│   │   └── interfaces/      # Interfaces de repo y UoW
│   ├── application/
│   │   ├── services/        # Lógica de negocio
│   │   └── dtos/            # Validaciones Pydantic
│   ├── infrastructure/
│   │   ├── database/        # Conexión y sesión
│   │   ├── repositories/    # Implementación de repos
│   │   └── unit_of_work/    # Manejo de transacciones
│   ├── api/
│   │   ├── controllers/     # Routers de FastAPI
│   │   └── main.py          # Punto de entrada
├── alembic/                 # Migraciones
├── .env                     # Variables de entorno
└── requirements.txt         # Dependencias
```

### Roles en el Grupo (2 Miembros)

*   **Miembro A (Líder del Núcleo - Domain & Application):** Encargado de las capas internas puras. Sus responsabilidades incluyen la definición de entidades, interfaces abstractas de persistencia, DTOs de validación con Pydantic y la lógica de servicios de aplicación que orquestan los casos de uso.
*   **Miembro B (Líder de Integración - Infrastructure & Presentation):** Encargado de las capas externas. Sus responsabilidades incluyen la configuración de la base de datos (SQLAlchemy y PostgreSQL), la implementación c## 4. Guía Paso a Paso de Implementación Secuencial

Para permitir que el **Miembro A** trabaje y termine toda su sección primero, y posteriormente el **Miembro B** continúe e integre el resto, hemos diseñado un flujo de trabajo **secuencial desacoplado**. Esta es la principal ventaja de la Onion Architecture: la lógica de negocio y las interfaces del Dominio pueden ser desarrolladas y terminadas por completo antes de escribir una sola línea de código de base de datos o endpoints.

---

### [FASE I] Desarrollo Completo del Núcleo (Miembro A - Trabaja Primero)

El **Miembro A** asume la responsabilidad de diseñar, codificar y dar por finalizadas las capas internas (`Domain` y `Application`). Al terminar esta fase, el núcleo del negocio estará 100% listo.

#### Paso 1: Refinamiento de Entidades de Dominio
*   **Archivo:** `app/domain/entities/compania.py` y `app/domain/entities/empleado.py`
*   **Acción:** Asegurar que los modelos ya provistos en el proyecto tengan todas las columnas necesarias (UUIDs autogenerados, correos únicos, llaves foráneas y relaciones bidireccionales con eliminación en cascada).

#### Paso 2: Diseño de Interfaces / Contratos (Abstracción de Persistencia)
*   **Directorio:** `app/domain/interfaces/`
*   **Acción:** Crear los contratos abstractos (clases base abstractas usando `abc.ABC` y `@abstractmethod`) que definen cómo se guardarán y consultarán los datos, sin preocuparse por la sintaxis de base de datos.
    1.  **`compania_repository.py`:** Interfaz `ICompaniaRepository` con firmas CRUD (`get_all`, `get_by_id`, `create`, `update`, `delete`).
    2.  **`empleado_repository.py`:** Interfaz `IEmpleadoRepository` con firmas CRUD y el método específico `get_by_compania(compania_id)`.
    3.  **`unit_of_work.py`:** Interfaz `IUnitOfWork` que expone los repositorios abstractos y los métodos abstractos `commit()`, `rollback()`, además de actuar como Context Manager de Python (`__enter__` y `__exit__`).

#### Paso 3: Diseño de DTOs y Esquemas de Validación (Pydantic)
*   **Directorio:** `app/application/dtos/`
*   **Acción:** Crear los esquemas de validación de Pydantic para desacoplar el Dominio de las peticiones externas.
    1.  **`compania_dto.py`:** `CompaniaDTO`, `CompaniaCreateDTO` (campos requeridos para crear), y `CompaniaUpdateDTO`.
    2.  **`empleado_dto.py`:** `EmpleadoDTO` (con validación de correo electrónico), `EmpleadoCreateDTO`, y `EmpleadoUpdateDTO`.
    3.  **DTO Transaccional Especial:** En `compania_dto.py` o en un archivo común, definir `CompaniaConEmpleadosCreateDTO`, el cual valida la creación conjunta de una compañía y una lista anidada de empleados.

#### Paso 4: Codificación Completa de la Capa de Servicios (Casos de Uso)
*   **Directorio:** `app/application/services/`
*   **Acción:** Desarrollar las clases de servicio que manejan las reglas de negocio reales. Estos servicios **solo** conocen la interfaz abstracta `IUnitOfWork`, por lo que son completamente independientes de la base de datos real.
    1.  **`empleado_service.py`:** Clase `EmpleadoService` que inyecta `IUnitOfWork` en su constructor. Implementa métodos de lógica para listar, crear, actualizar y eliminar empleados consultando y persistiendo a través de `uow.empleados`.
    2.  **`compania_service.py`:** Clase `CompaniaService` que inyecta `IUnitOfWork`. Implementa métodos de lógica para compañías.
    3.  **Lógica del Caso Transaccional Obligatorio:** Implementar dentro de `CompaniaService` el método `crear_compania_con_empleados(compania_dto, lista_empleados_dto)`. Este método debe usar la estructura `with self._uow as uow:` (Context Manager), crear la compañía en el repositorio, hacer un `flush` para obtener la ID generada, asociar y crear cada empleado, y finalmente llamar a `uow.commit()`.

> **Hito:** Al culminar este paso, el **Miembro A** entrega un código limpio, estructurado y terminado en las carpetas `domain/` y `application/`. El código no tiene acoplamiento a base de datos y está listo para que el Miembro B continúe.

---

### [FASE II] Integración de Persistencia y Base de Datos (Miembro B - Trabaja Segundo)

Una vez que el Miembro A finaliza el Núcleo, el **Miembro B** toma el relevo para enlazar la aplicación con las tecnologías externas (PostgreSQL, SQLAlchemy, Alembic).

#### Paso 5: Configuración de Entorno, DB y Conexión
*   **Archivos:** `.env`, `app/infrastructure/database/connection.py`, y `app/infrastructure/database/models.py`
*   **Acción:** 
    1.  Instalar dependencias (`pip install -r requirements.txt`).
    2.  Configurar la variable `DATABASE_URL` en el archivo `.env`.
    3.  En `connection.py`, instanciar el `engine` de SQLAlchemy para PostgreSQL y el generador de sesiones `sessionmaker`.

#### Paso 6: Inicialización y Ejecución de Migraciones (Alembic)
*   **Directorio:** `alembic/` y raíz del proyecto.
*   **Acción:** 
    1.  Ejecutar `alembic init alembic` para inicializar el control de versiones.
    2.  Configurar `alembic/env.py` cargando la URL desde `.env` y asociando `Base.metadata` de SQLAlchemy.
    3.  Ejecutar `alembic revision --autogenerate -m "crear_tablas_iniciales"`.
    4.  Ejecutar `alembic upgrade head` para crear las tablas físicas en la base de datos PostgreSQL local.

#### Paso 7: Implementación Concreta de Repositorios
*   **Directorio:** `app/infrastructure/repositories/`
*   **Acción:** Codificar las clases reales de acceso a datos utilizando la sesión de SQLAlchemy, heredando e implementando todos los métodos abstractos de las interfaces escritas por el Miembro A.
    1.  **`compania_repository_impl.py`** implementa `ICompaniaRepository`.
    2.  **`empleado_repository_impl.py`** implementa `IEmpleadoRepository`.
    3.  *Regla Técnica:* Ninguno de estos métodos ejecuta `commit()` o `rollback()`.

#### Paso 8: Implementación Concreta del Unit of Work (Context Manager)
*   **Directorio:** `app/infrastructure/unit_of_work/`
*   **Acción:** Crear `unit_of_work_impl.py` heredando de `IUnitOfWork`.
    1.  Implementar `__enter__` para crear la sesión de SQLAlchemy e inicializar las implementaciones de los repositorios inyectándoles esa sesión.
    2.  Implementar `__exit__` para capturar cualquier excepción. Si ocurre una excepción, ejecuta automáticamente `rollback()`. Al final, cierra la sesión.
    3.  Implementar los métodos `commit()` y `rollback()`.

#### Paso 9: Inserción de Datos Iniciales (Seed Data)
*   **Archivo:** `app/infrastructure/database/seed_data.py`
*   **Acción:** Crear un script autónomo que cree una sesión transaccional directa de SQLAlchemy e inserte al menos 3 compañías y 10 empleados coherentes en PostgreSQL para tener datos de prueba.

---

### [FASE III] Creación de la API y Capa de Presentación (Miembro B)

El **Miembro B** expone la funcionalidad a través de FastAPI utilizando los servicios que el Miembro A programó en la Fase I.

#### Paso 10: Inicialización de la Aplicación y Middlewares
*   **Archivos:** `app/api/main.py` y `app/api/middlewares/`
*   **Acción:**
    1.  Crear `main.py` instanciando `FastAPI` e incluyendo la documentación automática de Swagger.
    2.  Implementar un middleware global para manejo de errores (`error_handler.py`) y configurar el logging para registrar de manera clara los eventos de transacciones.

#### Paso 11: Inyección de Dependencias
*   **Archivo:** `app/api/dependencies.py`
*   **Acción:** Definir las dependencias de FastAPI. Crear una función `get_unit_of_work` que provea la instancia de `UnitOfWorkImpl` y funciones para proveer `CompaniaService` y `EmpleadoService` inyectándoles el UoW correspondiente.

#### Paso 12: Controladores y Endpoints (APIRouter)
*   **Directorio:** `app/api/controllers/`
*   **Acción:** Crear los controladores REST usando `APIRouter`.
    1.  **`companias_controller.py`:** Expone los endpoints de compañías (incluyendo el transaccional especial `POST /api/companias/con-empleados`).
    2.  **`empleados_controller.py`:** Expone los endpoints de empleados.
    3.  *Regla Técnica:* Los controladores inyectan los servicios de aplicación (`CompaniaService` o `EmpleadoService`) en sus constructores/parámetros de ruta y manejan la entrada y salida utilizando estrictamente los DTOs de Pydantic.

---

### [FASE IV] Verificación y Documentación (Ambos Miembros)

Una vez que todo está integrado, ambos miembros participan de forma colaborativa para cerrar la actividad.

#### Paso 13: Pruebas Funcionales y Transaccionales en Swagger
*   **Acción:** Correr el servidor y acceder a `http://127.0.0.1:8000/docs`.
    1.  **Prueba de Éxito:** Crear una compañía con sus empleados. Verificar persistencia correcta en PostgreSQL.
    2.  **Prueba de Falla:** Intentar crear otra compañía con un empleado que use un correo electrónico ya existente en el sistema. Comprobar que falle y verificar en la base de datos que la compañía no se haya creado (confirmando que el rollback de la transacción Unit of Work funcionó perfectamente).

#### Paso 14: Reporte Técnico y Evidencias
*   **Acción:** Registrar logs detallados de la consola mostrando la ejecución de commits y rollbacks. Completar el archivo `README.md` principal según la plantilla obligatoria y preparar la sustentación del proyecto.

---

## 5. Requisitos Funcionales y Endpoints... Ejecutando Rollback...`, etc.).
    2.  **README:** Llenar el archivo `README.md` de la raíz siguiendo la plantilla obligatoria con el análisis transaccional y la justificación técnica de la equivalencia frente a C#.

---

## 5. Requisitos Funcionales y Endpoints

### Entidades
*   **Compañía:** Id, Nombre, Direccion, Telefono, FechaCreacion.
*   **Empleado:** Id, Nombre, Apellido, Correo, Cargo, Salario, CompaniaId.

### Endpoints Principales
*   `GET /api/companias`: Listar todas.
*   `POST /api/companias`: Crear compañía.
*   `GET /api/companias/{id}/empleados`: Listar empleados por compañía.
*   `POST /api/companias/con-empleados`: **Transacción Unit of Work** (Crea compañía y empleados en un solo paso). Si falla uno, no se crea nada.

---

## 6. Verificación y Pruebas
*   Uso de **Swagger UI** (`/docs`) para pruebas manuales.
*   Validación de **Logging** para cada inicio de transacción, commit y rollback.
*   Pruebas de integridad: Intentar crear una compañía con un empleado erróneo y verificar que el rollback funcione correctamente.
