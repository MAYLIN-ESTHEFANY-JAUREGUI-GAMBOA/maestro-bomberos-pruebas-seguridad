import pytest

from app import Bombero, create_app, db


@pytest.fixture()
def client(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}",
            "SECRET_KEY": "test-key",
        }
    )
    with app.app_context():
        db.create_all()
    with app.test_client() as test_client:
        yield test_client
    with app.app_context():
        db.drop_all()


def payload(**overrides):
    data = {
        "dni": "12345678",
        "nombres": "Ana",
        "apellidos": "Rojas",
        "especialidad": "Rescate",
    }
    data.update(overrides)
    return data


def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Maestro de bomberos" in response.data


def test_create_list_update_state_and_delete_bombero(client):
    created = client.post("/api/bomberos", json=payload())
    assert created.status_code == 201
    bombero_id = created.json["bombero"]["id"]
    assert client.get("/api/bomberos").json[0]["dni"] == "12345678"

    updated = client.put(
        f"/api/bomberos/{bombero_id}",
        json=payload(nombres="Ana María", especialidad="Incendios"),
    )
    assert updated.status_code == 200
    assert updated.json["bombero"]["nombres"] == "Ana María"
    assert client.patch(f"/api/bomberos/{bombero_id}/estado", json={"estado": False}).status_code == 200
    assert client.get("/api/bomberos?estado=inactivo").json[0]["estado"] is False
    assert client.delete(f"/api/bomberos/{bombero_id}").status_code == 200
    assert client.get("/api/bomberos").json == []


@pytest.mark.parametrize(
    "invalid_data",
    [
        payload(dni="123"),
        payload(especialidad="Administrador"),
        payload(nombres=" "),
    ],
)
def test_create_rejects_invalid_data(client, invalid_data):
    response = client.post("/api/bomberos", json=invalid_data)
    assert response.status_code == 400
    assert "mensaje" in response.json


def test_duplicate_dni_and_invalid_state_are_rejected(client):
    assert client.post("/api/bomberos", json=payload()).status_code == 201
    assert client.post(
        "/api/bomberos",
        json=payload(nombres="Luis", dni="12345678"),
    ).status_code == 409
    bombero_id = client.get("/api/bomberos").json[0]["id"]
    assert client.patch(
        f"/api/bomberos/{bombero_id}/estado", json={"estado": "false"}
    ).status_code == 400


def test_missing_bombero_returns_not_found(client):
    assert client.get("/api/bomberos/999").status_code == 404
    assert client.put("/api/bomberos/999", json=payload()).status_code == 404
    assert client.delete("/api/bomberos/999").status_code == 404
