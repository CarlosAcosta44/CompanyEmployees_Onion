# Guia para entender el codigo del proyecto

Esta guia explica el proyecto como si estuvieras entrando por primera vez.
La idea es que puedas leer el codigo por capas y entender por que cada archivo
esta donde esta.

## 1. Que hace este proyecto

El proyecto es una API REST hecha con FastAPI para administrar:

- Companias.
- Empleados.
- La relacion entre una compania y muchos empleados.

Tambien demuestra tres ideas importantes:

- Onion Architecture.
- Repository Pattern.
- Unit of Work.

La API permite crear, consultar, actualizar y eliminar companias y empleados.
Ademas tiene un caso especial: crear una compania con varios empleados en una
sola transaccion.

## 2. La idea central de Onion Architecture

Onion Architecture busca que el centro del proyecto no dependa de detalles
externos.

En este proyecto, el centro es `app/domain`.

Regla principal:

```text
Las capas externas pueden depender de las internas.
Las capas internas NO deben depender de las externas.
```

Por eso:

- `domain` no debe conocer FastAPI.
- `domain` no debe conocer SQLAlchemy.
- `domain` no debe conocer PostgreSQL ni SQLite.
- `domain` no debe importar nada de `infrastructure`.

El dominio solo debe representar el negocio.

## 3. Mapa general de carpetas

```text
app/
├── domain/          # Nucleo del negocio
├── application/     # Casos de uso y DTOs
├── infrastructure/  # Base de datos, SQLAlchemy, repositorios concretos
└── api/             # FastAPI, rutas, middlewares, dependencias
```

Si lo miras como una cebolla:

```text
API / Presentation
Infrastructure
Application
Domain
```

Pero las dependencias apuntan hacia adentro:

```text
api -------------> application ---> domain
infrastructure -------------------> domain
infrastructure -------------------> application interfaces
```

## 4. Capa Domain

Ruta:

```text
app/domain/
```

Esta es la capa mas importante. Debe ser la mas limpia.

Contiene:

- Entidades de negocio.
- Validaciones propias del dominio.
- Excepciones de dominio.
- Interfaces de repositorios.
- Interfaz de Unit of Work.

### 4.1 Entidad Compania

Archivo:

```text
app/domain/entities/compania.py
```

La clase `Compania` representa una compania del negocio.

Campos principales:

- `id`
- `nombre`
- `direccion`
- `telefono`
- `fecha_creacion`
- `empleados`

Importante:

`Compania` es una entidad pura de Python. No hereda de SQLAlchemy. No tiene
`Column`, `relationship`, `ForeignKey` ni `__tablename__`.

Esto esta bien porque el dominio no debe saber como se guarda la informacion
en la base de datos.

Tambien tiene metodos de negocio:

```python
actualizar(...)
agregar_empleado(...)
```

Eso evita que otras capas modifiquen la entidad de cualquier manera y se salten
validaciones.

### 4.2 Entidad Empleado

Archivo:

```text
app/domain/entities/empleado.py
```

La clase `Empleado` representa a un empleado.

Campos principales:

- `id`
- `nombre`
- `apellido`
- `correo`
- `cargo`
- `salario`
- `compania_id`

Tambien es una entidad pura.

Tiene validaciones importantes:

- Nombre obligatorio.
- Apellido obligatorio.
- Correo valido.
- Cargo obligatorio.
- Salario mayor que cero.

### 4.3 Validaciones del dominio

Archivo:

```text
app/domain/validation.py
```

Aqui estan funciones pequenas reutilizables:

```python
ensure_required_text(...)
ensure_email(...)
ensure_positive_decimal(...)
```

Estas funciones son usadas por las entidades para proteger las reglas del
negocio.

Por ejemplo, si alguien intenta crear un empleado con salario negativo, el
dominio debe rechazarlo aunque la peticion no venga desde FastAPI.

### 4.4 Excepciones de dominio

Archivo:

```text
app/domain/exceptions.py
```

Define errores propios del negocio:

- `DomainValidationError`
- `EntityNotFoundError`
- `ConflictError`
- `PersistenceError`

Esto evita lanzar errores genericos como `ValueError` o devolver directamente
errores HTTP desde la capa de aplicacion.

### 4.5 Interfaces de repositorios

Archivos:

```text
app/domain/interfaces/compania_repository.py
app/domain/interfaces/empleado_repository.py
```

Estas interfaces dicen que operaciones se necesitan para guardar y consultar
datos, pero no dicen como se hacen.

Ejemplo:

```python
def get_by_id(self, empleado_id: UUID) -> Optional[Empleado]:
    ...
```

El dominio dice:

> Necesito poder buscar un empleado por id.

Pero no dice:

> Haz un SELECT con SQLAlchemy.

Eso queda en infraestructura.

### 4.6 Interfaz Unit of Work

Archivo:

```text
app/domain/interfaces/unit_of_work.py
```

Esta interfaz define que debe hacer un Unit of Work:

- Exponer repositorios.
- Confirmar cambios con `commit`.
- Revertir cambios con `rollback`.
- Abrir y cerrar un contexto transaccional con `with`.

La interfaz esta en `domain`, pero la implementacion concreta esta en
`infrastructure`.

## 5. Capa Application

Ruta:

```text
app/application/
```

Esta capa contiene los casos de uso.

Responde preguntas como:

- Como se crea un empleado?
- Que se valida antes de crear un empleado?
- Como se crea una compania con varios empleados de forma atomica?

La capa `application` coordina el flujo, pero no habla directamente con la base
de datos.

## 6. DTOs

Ruta:

```text
app/application/dtos/
```

Los DTOs son objetos para entrada y salida de datos.

Archivos:

```text
app/application/dtos/compania_dto.py
app/application/dtos/empleado_dto.py
```

Ejemplos:

- `CompaniaCreateDTO`
- `CompaniaUpdateDTO`
- `CompaniaDTO`
- `EmpleadoCreateDTO`
- `EmpleadoUpdateDTO`
- `EmpleadoDTO`
- `CompaniaConEmpleadosCreateDTO`

Los DTOs usan Pydantic.

Importante:

Pydantic esta en `application`, no en `domain`.

Eso significa que el dominio no depende del framework de validacion de entrada.
Los DTOs validan datos que vienen desde la API, pero las entidades tambien
protegen sus propias reglas.

## 7. Servicios de aplicacion

Ruta:

```text
app/application/services/
```

Archivos:

```text
app/application/services/compania_service.py
app/application/services/empleado_service.py
```

Los servicios son los casos de uso.

### 7.1 EmpleadoService

Archivo:

```text
app/application/services/empleado_service.py
```

Tiene metodos como:

- `listar_todos`
- `obtener_por_id`
- `listar_por_compania`
- `crear`
- `actualizar`
- `eliminar`

Ejemplo del flujo al crear empleado:

```text
1. Recibe EmpleadoCreateDTO.
2. Abre Unit of Work.
3. Verifica que la compania exista.
4. Verifica que no exista otro empleado con el mismo correo.
5. Crea la entidad Empleado.
6. La envia al repositorio.
7. Hace commit.
8. Devuelve EmpleadoDTO.
```

### 7.2 CompaniaService

Archivo:

```text
app/application/services/compania_service.py
```

Tiene metodos como:

- `listar_todas`
- `obtener_por_id`
- `crear`
- `actualizar`
- `eliminar`
- `crear_compania_con_empleados`

El metodo mas importante para la actividad es:

```python
crear_compania_con_empleados(...)
```

Ese metodo demuestra Unit of Work.

## 8. Caso importante: crear compania con empleados

Endpoint:

```text
POST /api/companias/con-empleados
```

Servicio:

```text
app/application/services/compania_service.py
```

Metodo:

```python
crear_compania_con_empleados(...)
```

Flujo:

```text
1. Llega una peticion con datos de compania y empleados.
2. FastAPI valida el body usando CompaniaConEmpleadosCreateDTO.
3. El controlador llama a CompaniaService.
4. El servicio abre Unit of Work.
5. Se crea la entidad Compania.
6. Se guarda la compania usando el repositorio.
7. Por cada empleado:
   - Se valida que el correo no venga duplicado en la misma solicitud.
   - Se valida que el correo no exista ya en base de datos.
   - Se crea la entidad Empleado.
   - Se asocia a la compania.
   - Se guarda usando el repositorio.
8. Si todo sale bien, se ejecuta commit.
9. Si algo falla, se ejecuta rollback.
```

La parte clave:

```text
Todo se guarda, o nada se guarda.
```

Eso es atomicidad.

## 9. Capa Infrastructure

Ruta:

```text
app/infrastructure/
```

Esta capa contiene los detalles externos:

- SQLAlchemy.
- Conexion a base de datos.
- Modelos ORM.
- Repositorios concretos.
- Unit of Work concreto.
- Configuracion.
- Seed data.

El dominio no depende de esta capa.

## 10. Configuracion

Archivo:

```text
app/infrastructure/config/settings.py
```

Lee variables de entorno usando `pydantic-settings`.

Variable principal:

```env
DATABASE_URL
```

Puedes usar PostgreSQL:

```env
DATABASE_URL=postgresql://postgres:TU_CLAVE@localhost:5432/db_companias
```

O SQLite:

```env
DATABASE_URL=sqlite:///./database.db
```

El archivo `.env.example` muestra ambos ejemplos.

## 11. Conexion a base de datos

Archivo:

```text
app/infrastructure/database/connection.py
```

Este archivo crea:

- `engine`
- `SessionLocal`

`engine` representa la conexion general con la base de datos.

`SessionLocal` crea sesiones de SQLAlchemy.

Cuando se usa SQLite, tambien activa:

```sql
PRAGMA foreign_keys=ON
```

Eso es importante porque SQLite no siempre respeta llaves foraneas si no se
activan explicitamente.

## 12. Modelos ORM

Archivo:

```text
app/infrastructure/database/models.py
```

Aqui estan los modelos de SQLAlchemy:

- `CompaniaModel`
- `EmpleadoModel`

Estos si tienen detalles de base de datos:

- `__tablename__`
- columnas
- llaves primarias
- llaves foraneas
- relaciones
- restricciones

Ejemplo conceptual:

```text
CompaniaModel  -> tabla companias
EmpleadoModel  -> tabla empleados
```

Estos modelos viven en `infrastructure`, no en `domain`.

Eso es lo correcto en Onion Architecture estricta.

## 13. Mappers

Archivo:

```text
app/infrastructure/repositories/mappers.py
```

Los mappers convierten entre:

```text
Entidad de dominio <-> Modelo ORM
```

Ejemplo:

```text
Compania      <-> CompaniaModel
Empleado      <-> EmpleadoModel
```

Por que existen?

Porque el dominio no quiere saber nada de SQLAlchemy, pero SQLAlchemy necesita
modelos ORM para guardar en la base de datos.

Los mappers son el puente entre esos dos mundos.

## 14. Repositorios concretos

Ruta:

```text
app/infrastructure/repositories/
```

Archivos:

```text
compania_repository_impl.py
empleado_repository_impl.py
```

Estos repositorios implementan las interfaces del dominio.

Ejemplo:

La interfaz dice:

```python
get_by_id(...)
```

La implementacion hace:

```python
self._session.get(CompaniaModel, compania_id)
```

Importante:

Los repositorios NO hacen `commit`.

Solo consultan, agregan, actualizan o eliminan objetos en la sesion.
El `commit` lo maneja Unit of Work.

## 15. Unit of Work concreto

Archivo:

```text
app/infrastructure/unit_of_work/unit_of_work_impl.py
```

Este archivo implementa `IUnitOfWork`.

Hace varias cosas:

- Abre una sesion de SQLAlchemy.
- Crea repositorios usando esa misma sesion.
- Permite usar `with self._uow as uow`.
- Ejecuta `commit`.
- Ejecuta `rollback`.
- Cierra la sesion.

Ejemplo conceptual:

```python
with self._uow as uow:
    uow.companias.create(compania)
    uow.empleados.create(empleado)
    uow.commit()
```

Si ocurre un error antes del `commit`, se revierte la transaccion.

Si hay un correo duplicado o una llave foranea invalida, se convierte en un
error de dominio como `ConflictError`.

## 16. Capa API

Ruta:

```text
app/api/
```

Esta capa contiene FastAPI.

Aqui viven:

- `main.py`
- controladores
- dependencias
- middleware de errores

## 17. main.py

Archivo:

```text
app/api/main.py
```

Este es el punto de entrada de FastAPI.

Crea la aplicacion:

```python
app = FastAPI(...)
```

Agrega el middleware de errores:

```python
app.add_middleware(ErrorHandlerMiddleware)
```

Registra rutas:

```python
app.include_router(companias_router, prefix="/api")
app.include_router(empleados_router, prefix="/api")
```

Tambien tiene el endpoint raiz:

```text
GET /
```

## 18. Dependencies

Archivo:

```text
app/api/dependencies.py
```

Este archivo conecta FastAPI con la aplicacion.

Crea:

- `UnitOfWorkImpl`
- `CompaniaService`
- `EmpleadoService`

Ejemplo:

```python
def get_compania_service() -> CompaniaService:
    return CompaniaService(get_unit_of_work())
```

Esto permite que los controladores reciban servicios sin construirlos
directamente dentro del endpoint.

## 19. Controladores

Ruta:

```text
app/api/controllers/
```

Archivos:

```text
companias_controller.py
empleados_controller.py
```

Los controladores exponen endpoints HTTP.

Ejemplo:

```python
@router.get("", response_model=list[CompaniaDTO])
def listar_companias(...):
    return service.listar_todas()
```

El controlador debe ser delgado.

Debe hacer principalmente esto:

```text
Recibir peticion -> llamar servicio -> devolver respuesta
```

No debe tener SQLAlchemy.
No debe tener reglas complejas de negocio.

## 20. Middleware de errores

Archivo:

```text
app/api/middlewares/error_handler.py
```

Convierte errores del dominio a respuestas HTTP.

Ejemplos:

```text
EntityNotFoundError      -> 404
ConflictError           -> 409
DomainValidationError   -> 400
PersistenceError        -> 500
```

Esto permite que los servicios no tengan que saber de HTTP.

El servicio lanza un error del negocio.
La API decide que codigo HTTP corresponde.

## 21. Flujo completo de una peticion GET

Ejemplo:

```text
GET /api/companias
```

Flujo:

```text
1. FastAPI recibe la peticion.
2. companias_controller.py ejecuta listar_companias.
3. FastAPI inyecta CompaniaService usando dependencies.py.
4. CompaniaService abre UnitOfWork.
5. UnitOfWork crea una sesion de SQLAlchemy.
6. UnitOfWork crea CompaniaRepositoryImpl.
7. El servicio llama uow.companias.get_all().
8. El repositorio consulta CompaniaModel.
9. El mapper convierte CompaniaModel a Compania.
10. El servicio convierte Compania a CompaniaDTO.
11. FastAPI devuelve JSON.
```

## 22. Flujo completo de una peticion POST

Ejemplo:

```text
POST /api/empleados
```

Flujo:

```text
1. FastAPI recibe el JSON.
2. Pydantic valida usando EmpleadoCreateDTO.
3. empleados_controller.py llama service.crear(dto).
4. EmpleadoService abre UnitOfWork.
5. Verifica que exista la compania.
6. Verifica que el correo no exista.
7. Crea la entidad Empleado.
8. El repositorio convierte Empleado a EmpleadoModel.
9. SQLAlchemy prepara el INSERT.
10. UnitOfWork hace commit.
11. El servicio devuelve EmpleadoDTO.
12. FastAPI responde con status 201.
```

## 23. Por que hay DTO y entidad si parecen parecidos

Aunque se parezcan, no son lo mismo.

DTO:

```text
Sirve para entrada y salida de datos.
Vive cerca de la API.
Puede usar Pydantic.
```

Entidad:

```text
Representa el negocio.
Vive en domain.
No conoce FastAPI ni Pydantic.
Protege reglas del negocio.
```

Modelo ORM:

```text
Representa la tabla en base de datos.
Vive en infrastructure.
Usa SQLAlchemy.
```

Resumen:

```text
DTO         -> habla con la API
Entidad    -> habla del negocio
ORM Model  -> habla con la base de datos
```

## 24. Por que hay interfaces y tambien implementaciones

Ejemplo:

```text
IEmpleadoRepository
EmpleadoRepositoryImpl
```

La interfaz dice que necesita la aplicacion:

```text
Necesito guardar empleados.
Necesito buscar empleados.
Necesito buscar por correo.
```

La implementacion dice como se hace con SQLAlchemy.

Ventaja:

Si manana se cambia SQLAlchemy por otra herramienta, el dominio y la aplicacion
pueden quedarse casi iguales.

## 25. Como leer el proyecto sin perderse

Te recomiendo este orden:

1. Lee `app/domain/entities/compania.py`.
2. Lee `app/domain/entities/empleado.py`.
3. Lee `app/domain/interfaces/empleado_repository.py`.
4. Lee `app/domain/interfaces/unit_of_work.py`.
5. Lee `app/application/dtos/empleado_dto.py`.
6. Lee `app/application/services/empleado_service.py`.
7. Lee `app/infrastructure/database/models.py`.
8. Lee `app/infrastructure/repositories/mappers.py`.
9. Lee `app/infrastructure/repositories/empleado_repository_impl.py`.
10. Lee `app/infrastructure/unit_of_work/unit_of_work_impl.py`.
11. Lee `app/api/controllers/empleados_controller.py`.
12. Lee `app/api/main.py`.

Despues repite el mismo recorrido para companias.

## 26. Como correr el proyecto

Primero instala dependencias:

```bash
pip install -r requirements.txt
```

Crea un `.env` tomando como base `.env.example`.

Para SQLite:

```env
DATABASE_URL=sqlite:///./database.db
```

Para PostgreSQL:

```env
DATABASE_URL=postgresql://postgres:TU_CLAVE@localhost:5432/db_companias
```

Ejecuta migraciones:

```bash
alembic upgrade head
```

Levanta FastAPI:

```bash
uvicorn app.api.main:app --reload
```

Abre Swagger:

```text
http://127.0.0.1:8000/docs
```

## 27. Como correr pruebas

```bash
pytest -q
```

Las pruebas actuales revisan:

- Que `domain` no importe capas externas ni frameworks.
- Que el caso transaccional haga rollback completo.
- Que el endpoint raiz responda correctamente.

## 28. Preguntas tipicas

### Por que el dominio no tiene SQLAlchemy?

Porque SQLAlchemy es un detalle tecnico de infraestructura.
El negocio debe poder entenderse sin saber que base de datos se usa.

### Por que los repositorios no hacen commit?

Porque el commit debe coordinar varias operaciones juntas.
Eso lo hace Unit of Work.

### Por que SQLite y PostgreSQL usan el mismo codigo?

Porque SQLAlchemy abstrae gran parte de la base de datos.
El proyecto decide cual usar leyendo `DATABASE_URL`.

### Por que existe mappers.py?

Porque hay dos objetos distintos:

- Entidad de dominio.
- Modelo ORM.

El mapper convierte entre ellos.

### Donde esta el caso principal de Unit of Work?

En:

```text
app/application/services/compania_service.py
```

Metodo:

```python
crear_compania_con_empleados(...)
```

## 29. Resumen corto

Si solo recuerdas una cosa, recuerda esta:

```text
Domain define el negocio.
Application ejecuta casos de uso.
Infrastructure guarda datos.
API expone HTTP.
```

Y esta regla:

```text
El centro no depende de los detalles externos.
```

