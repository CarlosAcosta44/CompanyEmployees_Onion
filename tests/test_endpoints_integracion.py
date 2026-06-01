"""Pruebas de integración de los endpoints HTTP."""

from __future__ import annotations

import pytest


COMPANIA_PAYLOAD = {
    "nombre": "TechCorp SAS",
    "direccion": "Calle 10 # 5-20",
    "telefono": "3001234567",
}

def empleado_payload(compania_id, correo="ana@techcorp.com"):
    return {
        "nombre": "Ana",
        "apellido": "Martinez",
        "correo": correo,
        "cargo": "QA Engineer",
        "salario": "3800000.00",
        "compania_id": compania_id,
    }


# ---- Compañías ----

def test_listar_companias_retorna_200(test_client):
    response = test_client.get("/api/companias")
    assert response.status_code == 200
    assert "datos" in response.json()


def test_crear_compania_retorna_201(test_client):
    response = test_client.post("/api/companias", json=COMPANIA_PAYLOAD)
    assert response.status_code == 201
    assert response.json()["nombre"] == "TechCorp SAS"


def test_obtener_compania_por_id_retorna_200(test_client):
    creada = test_client.post("/api/companias", json=COMPANIA_PAYLOAD).json()
    response = test_client.get(f"/api/companias/{creada['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == creada["id"]


def test_obtener_compania_inexistente_retorna_404(test_client):
    response = test_client.get("/api/companias/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_actualizar_compania_retorna_200(test_client):
    creada = test_client.post("/api/companias", json=COMPANIA_PAYLOAD).json()
    response = test_client.put(
        f"/api/companias/{creada['id']}",
        json={"nombre": "TechCorp Colombia"},
    )
    assert response.status_code == 200
    assert response.json()["nombre"] == "TechCorp Colombia"


def test_eliminar_compania_retorna_204(test_client):
    creada = test_client.post("/api/companias", json=COMPANIA_PAYLOAD).json()
    response = test_client.delete(f"/api/companias/{creada['id']}")
    assert response.status_code == 204


def test_crear_compania_payload_invalido_retorna_422(test_client):
    response = test_client.post("/api/companias", json={"nombre": ""})
    assert response.status_code == 422


# ---- Empleados ----

def test_listar_empleados_retorna_200(test_client):
    response = test_client.get("/api/empleados")
    assert response.status_code == 200
    assert "datos" in response.json()


def test_crear_empleado_retorna_201(test_client):
    compania = test_client.post("/api/companias", json=COMPANIA_PAYLOAD).json()
    response = test_client.post("/api/empleados", json=empleado_payload(compania["id"]))
    assert response.status_code == 201
    assert response.json()["correo"] == "ana@techcorp.com"


def test_crear_empleado_correo_duplicado_retorna_409(test_client):
    compania = test_client.post("/api/companias", json=COMPANIA_PAYLOAD).json()
    test_client.post("/api/empleados", json=empleado_payload(compania["id"]))
    response = test_client.post("/api/empleados", json=empleado_payload(compania["id"]))
    assert response.status_code == 409


def test_crear_empleado_compania_inexistente_retorna_404(test_client):
    response = test_client.post(
        "/api/empleados",
        json=empleado_payload("00000000-0000-0000-0000-000000000000"),
    )
    assert response.status_code == 404


def test_crear_empleado_salario_invalido_retorna_422(test_client):
    compania = test_client.post("/api/companias", json=COMPANIA_PAYLOAD).json()
    payload = empleado_payload(compania["id"])
    payload["salario"] = "-500"