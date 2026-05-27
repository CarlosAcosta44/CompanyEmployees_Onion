"""Pruebas livianas de contrato HTTP."""

from fastapi.testclient import TestClient

from app.api.main import app


def test_root_endpoint_responde_estado_basico() -> None:
    response = TestClient(app).get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "API Compañías y Empleados funcionando correctamente."}
