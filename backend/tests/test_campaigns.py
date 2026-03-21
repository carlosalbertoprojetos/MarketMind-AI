"""Testes das rotas de campanhas: CRUD e listagem."""
import pytest
from fastapi.testclient import TestClient


def test_create_campaign(client: TestClient, auth_headers):
    r = client.post(
        "/campaign",
        json={"title": "Campanha Teste", "content": "Conteúdo", "platform": "instagram"},
        headers=auth_headers,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "Campanha Teste"
    assert data["platform"] == "instagram"
    assert "id" in data


def test_list_campaigns_empty(client: TestClient, auth_headers):
    r = client.get("/campaign", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert "limit" in data and "offset" in data


def test_list_campaigns_after_create(client: TestClient, auth_headers):
    client.post("/campaign", json={"title": "C1", "content": "x"}, headers=auth_headers)
    r = client.get("/campaign", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 1
    assert data["total"] == 1
    assert data["items"][0]["title"] == "C1"


def test_list_campaigns_filter_platform(client: TestClient, auth_headers):
    client.post("/campaign", json={"title": "IG", "platform": "instagram"}, headers=auth_headers)
    client.post("/campaign", json={"title": "FB", "platform": "facebook"}, headers=auth_headers)
    r = client.get("/campaign?platform=instagram", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["platform"] == "instagram"


def test_list_campaigns_filter_search(client: TestClient, auth_headers):
    client.post("/campaign", json={"title": "Campanha Banana", "content": "x"}, headers=auth_headers)
    client.post("/campaign", json={"title": "Campanha Laranja", "content": "x"}, headers=auth_headers)
    r = client.get("/campaign?search=Banana", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1
    assert any("Banana" in item["title"] for item in data["items"])


def test_list_campaigns_sort(client: TestClient, auth_headers):
    r = client.get("/campaign?sort=created_at_asc", headers=auth_headers)
    assert r.status_code == 200
    assert "items" in r.json()
    r2 = client.get("/campaign?sort=schedule_asc", headers=auth_headers)
    assert r2.status_code == 200
    assert "items" in r2.json()


def test_get_campaign(client: TestClient, auth_headers):
    create = client.post("/campaign", json={"title": "C1", "content": "x"}, headers=auth_headers)
    cid = create.json()["id"]
    r = client.get(f"/campaign/{cid}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["id"] == cid
    assert r.json()["title"] == "C1"


def test_get_campaign_404(client: TestClient, auth_headers):
    r = client.get("/campaign/99999", headers=auth_headers)
    assert r.status_code == 404


def test_patch_campaign(client: TestClient, auth_headers):
    create = client.post("/campaign", json={"title": "C1", "content": "x"}, headers=auth_headers)
    cid = create.json()["id"]
    r = client.patch(f"/campaign/{cid}", json={"title": "C1 Atualizado"}, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["title"] == "C1 Atualizado"


def test_delete_campaign(client: TestClient, auth_headers):
    create = client.post("/campaign", json={"title": "C1"}, headers=auth_headers)
    cid = create.json()["id"]
    r = client.delete(f"/campaign/{cid}", headers=auth_headers)
    assert r.status_code == 204
    r2 = client.get(f"/campaign/{cid}", headers=auth_headers)
    assert r2.status_code == 404


def test_campaign_without_auth(client: TestClient):
    r = client.get("/campaign")
    assert r.status_code == 401


def test_upcoming_empty(client: TestClient, auth_headers):
    r = client.get("/campaign/upcoming?hours=24", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_upcoming_with_scheduled(client: TestClient, auth_headers):
    from datetime import datetime, timedelta
    future = (datetime.utcnow() + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    cr = client.post(
        "/campaign",
        json={"title": "Agendada", "schedule": future, "platform": "instagram"},
        headers=auth_headers,
    )
    assert cr.status_code == 201
    r = client.get("/campaign/upcoming?hours=24", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 1
    titles = [c["title"] for c in data]
    assert "Agendada" in titles


def test_mark_reminder_sent(client: TestClient, auth_headers):
    create = client.post("/campaign", json={"title": "C1"}, headers=auth_headers)
    cid = create.json()["id"]
    r = client.post(f"/campaign/{cid}/remind", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["id"] == cid
