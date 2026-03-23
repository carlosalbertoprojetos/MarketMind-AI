"""Testes de health check e rotas /user."""
from fastapi.testclient import TestClient


def test_health(client: TestClient):
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json() == {'status': 'ok'}


def test_user_campaigns_empty(client: TestClient, auth_headers):
    r = client.get('/user/campaigns', headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data['items'] == []
    assert data['total'] == 0


def test_user_campaigns_after_create(client: TestClient, auth_headers):
    client.post('/campaign', json={'title': 'C1'}, headers=auth_headers)
    r = client.get('/user/campaigns', headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data['items']) == 1
    assert data['total'] == 1


def test_user_campaigns_expose_multiple_platforms_and_support_multi_filter(client: TestClient, auth_headers):
    client.post(
        '/campaign',
        json={
            'title': 'Campanha multicanal',
            'content': 'URL: https://example.com\n\nPLATFORMS:\ninstagram\nlinkedin\nEND_PLATFORMS',
            'platform': 'instagram',
        },
        headers=auth_headers,
    )
    client.post(
        '/campaign',
        json={
            'title': 'Campanha tiktok',
            'content': 'URL: https://example.com/tiktok',
            'platform': 'tiktok',
        },
        headers=auth_headers,
    )

    listing = client.get('/user/campaigns?platforms=instagram,linkedin', headers=auth_headers)
    assert listing.status_code == 200
    payload = listing.json()
    assert payload['total'] == 1
    assert payload['items'][0]['platforms'] == ['instagram', 'linkedin']

    summary = client.get('/user/summary', headers=auth_headers)
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload['by_platform']['instagram'] == 1
    assert summary_payload['by_platform']['linkedin'] == 1
    assert summary_payload['by_platform']['tiktok'] == 1
