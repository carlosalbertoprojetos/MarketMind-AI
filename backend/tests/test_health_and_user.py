"""Testes de health check e rota /user/campaigns."""
import pytest
from fastapi.testclient import TestClient


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_user_campaigns_empty(client: TestClient, auth_headers):
    r = client.get("/user/campaigns", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_user_campaigns_after_create(client: TestClient, auth_headers):
    client.post("/campaign", json={"title": "C1"}, headers=auth_headers)
    r = client.get("/user/campaigns", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 1
    assert data["total"] == 1
