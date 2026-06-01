"""Pruebas de integración para autenticación, roles y políticas de propiedad (Módulos 5 y 6)."""

from __future__ import annotations
import pytest
from uuid import uuid4

pytestmark = pytest.mark.anyio


# =============================================================================
#  Módulo 5: Pruebas de Roles y Autenticación Global (401 & 403)
# =============================================================================

def test_invitado_acceder_endpoints_retorna_401(client_invitado):
    # GET companias
    r = client_invitado.get("/api/companias")
    assert r.status_code == 401

    # POST compania
    r = client_invitado.post("/api/companias", json={"nombre": "T", "direccion": "D", "telefono": "1234567"})
    assert r.status_code == 401

    # DELETE compania
    r = client_invitado.delete(f"/api/companias/{uuid4()}")
    assert r.status_code == 401


def test_usuario_puede_hacer_get_post_put_pero_no_delete(client_usuario, test_client):
    # Crear una compañía usando el cliente admin (para que exista)
    compania = test_client.post("/api/companias", json={
        "nombre": "Compañia Test SRL",
        "direccion": "Calle Falsa 123",
        "telefono": "+57 604 123 4567"
    }).json()
    compania_id = compania["id"]

    # Cliente autenticado como USUARIO asociado a esa compañía
    cl_user = client_usuario(compania_id=compania_id)

    # 1. GET (Permitido para cualquier autenticado)
    r = cl_user.get(f"/api/companias/{compania_id}")
    assert r.status_code == 200

    # 2. POST (Permitido para ADMIN o USUARIO)
    r = cl_user.post("/api/empleados", json={
        "nombre": "Juan",
        "apellido": "Perez",
        "correo": "juan.perez@test.com",
        "cargo": "Desarrollador",
        "salario": "1500000.00",
        "compania_id": compania_id
    })
    assert r.status_code == 201
    empleado_id = r.json()["id"]

    # 3. PUT (Permitido para ADMIN o USUARIO)
    r = cl_user.put(f"/api/empleados/{empleado_id}", json={
        "nombre": "Juan Modificado",
        "apellido": "Perez",
        "correo": "juan.perez@test.com",
        "cargo": "Desarrollador Senior",
        "salario": "2500000.00",
        "compania_id": compania_id
    })
    assert r.status_code == 200

    # 4. DELETE (Solo ADMIN) -> Debe retornar 403 Forbidden
    r = cl_user.delete(f"/api/companias/{compania_id}")
    assert r.status_code == 403


# =============================================================================
#  Módulo 6: Pruebas de la Política EsPropietarioDeCompania
# =============================================================================

def test_politica_es_propietario_de_compania(client_usuario, test_client):
    # 1. Crear Compañía A y Compañía B (usando admin client)
    cia_a = test_client.post("/api/companias", json={
        "nombre": "Compañia A",
        "direccion": "Direccion A",
        "telefono": "+57 604 111 2222"
    }).json()
    cia_b = test_client.post("/api/companias", json={
        "nombre": "Compañia B",
        "direccion": "Direccion B",
        "telefono": "+57 604 333 4444"
    }).json()

    cia_a_id = cia_a["id"]
    cia_b_id = cia_b["id"]

    # 2. Crear Cliente USUARIO vinculado a la Compañía A
    cl_user_a = client_usuario(compania_id=cia_a_id)

    # 3. Crear empleado en la Compañía A (Debe ser PERMITIDO)
    r = cl_user_a.post("/api/empleados", json={
        "nombre": "Empleado A",
        "apellido": "Test",
        "correo": "empleado.a@compania.com",
        "cargo": "Asistente",
        "salario": "1500000.00",
        "compania_id": cia_a_id
    })
    assert r.status_code == 201
    emp_a_id = r.json()["id"]

    # 4. Intentar crear empleado en la Compañía B (Debe ser DENEGADO - 403)
    r = cl_user_a.post("/api/empleados", json={
        "nombre": "Empleado B",
        "apellido": "Test",
        "correo": "empleado.b@compania.com",
        "cargo": "Asistente",
        "salario": "1500000.00",
        "compania_id": cia_b_id
    })
    assert r.status_code == 403
    assert "solo puede crear empleados para su propia compañía" in r.json()["mensaje"]

    # 5. Modificar empleado de su propia Compañía A (Debe ser PERMITIDO)
    r = cl_user_a.put(f"/api/empleados/{emp_a_id}", json={
        "nombre": "Empleado A Modificado",
        "apellido": "Test",
        "correo": "empleado.a@compania.com",
        "cargo": "Asistente Senior",
        "salario": "2200000.00",
        "compania_id": cia_a_id
    })
    assert r.status_code == 200

    # 6. Crear un empleado en Compañía B con admin para intentar modificarlo con cl_user_a
    emp_b = test_client.post("/api/empleados", json={
        "nombre": "Empleado B Real",
        "apellido": "Test",
        "correo": "real.b@compania.com",
        "cargo": "Lider",
        "salario": "5000000.00",
        "compania_id": cia_b_id
    }).json()
    emp_b_id = emp_b["id"]

    # 7. Intentar modificar empleado de Compañía B siendo USUARIO de Compañía A (Debe ser DENEGADO - 403)
    r = cl_user_a.put(f"/api/empleados/{emp_b_id}", json={
        "nombre": "Intruso",
        "apellido": "Modificador",
        "correo": "real.b@compania.com",
        "cargo": "Hack",
        "salario": "9999999.00",
        "compania_id": cia_b_id
    })
    assert r.status_code == 403
    assert "solo puede modificar empleados de su propia compañía" in r.json()["mensaje"]

    # 8. Modificar empleado de Compañía B siendo ADMIN (Debe ser EXENTO de política - PERMITIDO)
    r = test_client.put(f"/api/empleados/{emp_b_id}", json={
        "nombre": "Empleado B Admin",
        "apellido": "Test",
        "correo": "real.b@compania.com",
        "cargo": "Gerente",
        "salario": "6000000.00",
        "compania_id": cia_b_id
    })
    assert r.status_code == 200
    assert r.json()["nombre"] == "Empleado B Admin"
