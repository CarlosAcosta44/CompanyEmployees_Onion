"""Pruebas de integracion para autenticacion y roles (Modulo 5)."""

from __future__ import annotations
import pytest
from uuid import uuid4

pytestmark = pytest.mark.anyio


# =============================================================================
#  Modulo 5: Pruebas de Roles y Autenticacion Global (401 & 403)
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
    # Crear una compañia usando el cliente admin (para que exista)
    compania = test_client.post("/api/companias", json={
        "nombre": "Compañia Test SRL",
        "direccion": "Calle Falsa 123",
        "telefono": "+57 604 123 4567"
    }).json()
    compania_id = compania["id"]

    # Cliente autenticado como USUARIO asociado a esa compañia
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
