import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    rv = client.get("/health")
    assert rv.status_code == 200
    assert rv.get_json()["status"] == "ok"


def test_expression_calc(client):
    rv = client.post("/api/calc", json={"input": "2 + 3 * 4"})
    assert rv.status_code == 200
    payload = rv.get_json()
    assert payload["mode"] == "expression"
    assert payload["result"] == 14


def test_nlp_calc(client):
    rv = client.post("/api/calc", json={"input": "suma 5 y 7"})
    assert rv.status_code == 200
    payload = rv.get_json()
    assert payload["mode"] == "nlp"
    assert payload["result"] == 12


def test_invalid_input(client):
    rv = client.post("/api/calc", json={"input": "esta frase no tiene numeros"})
    assert rv.status_code == 400
    assert "error" in rv.get_json()
