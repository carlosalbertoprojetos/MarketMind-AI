"""Testes das rotas de autenticação: register e login."""
import pytest
from fastapi.testclient import TestClient


def test_register_ok(client: TestClient):
    r = client.post("/auth/register", json={"email": "novo@test.com", "password": "senha123"})
    assert r.status_code == 200
    data = r.json()
    assert "user" in data
    assert data["user"]["email"] == "novo@test.com"
    assert "id" in data["user"]
    assert "password" not in str(data)


def test_register_duplicate_email(client: TestClient, test_user):
    _, email, _ = test_user
    r = client.post("/auth/register", json={"email": email, "password": "outrasenha"})
    assert r.status_code == 400
    assert "já cadastrado" in r.json().get("detail", "").lower() or "already" in r.json().get("detail", "").lower()


def test_login_ok(client: TestClient, test_user):
    _, email, password = test_user
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    data = r.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data and len(data["access_token"]) > 0


def test_login_wrong_password(client: TestClient, test_user):
    _, email, _ = test_user
    r = client.post("/auth/login", json={"email": email, "password": "wrong"})
    assert r.status_code == 401


def test_login_unknown_email(client: TestClient):
    r = client.post("/auth/login", json={"email": "naoexiste@test.com", "password": "x"})
    assert r.status_code == 401
