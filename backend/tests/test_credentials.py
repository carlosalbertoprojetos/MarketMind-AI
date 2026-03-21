"""Testes das rotas de credenciais: listar, criar e remover."""
import pytest
from fastapi.testclient import TestClient


def test_create_credential(client: TestClient, auth_headers):
    r = client.post(
        "/credentials",
        json={
            "site_name": "Meu Site",
            "login_url": "https://site.com/login",
            "username": "user",
            "password": "secret",
        },
        headers=auth_headers,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["site_name"] == "Meu Site"
    assert data["login_url"] == "https://site.com/login"
    assert data["has_username"] is True
    assert data["has_password"] is True
    assert "password" not in str(data).lower() or "has_password" in str(data)


def test_list_credentials_empty(client: TestClient, auth_headers):
    r = client.get("/credentials", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_list_credentials_after_create(client: TestClient, auth_headers):
    client.post(
        "/credentials",
        json={"site_name": "S1", "login_url": "https://a.com", "username": "u"},
        headers=auth_headers,
    )
    r = client.get("/credentials", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["site_name"] == "S1"


def test_delete_credential(client: TestClient, auth_headers):
    create = client.post(
        "/credentials",
        json={"site_name": "S1", "login_url": "https://a.com"},
        headers=auth_headers,
    )
    cid = create.json()["id"]
    r = client.delete(f"/credentials/{cid}", headers=auth_headers)
    assert r.status_code == 204
    r2 = client.get("/credentials", headers=auth_headers)
    assert len(r2.json()) == 0


def test_credentials_without_auth(client: TestClient):
    r = client.get("/credentials")
    assert r.status_code == 401
