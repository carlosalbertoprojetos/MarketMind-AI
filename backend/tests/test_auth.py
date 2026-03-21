"""Testes das rotas de autenticacao: register, login, sessao, refresh e logout."""
from fastapi.testclient import TestClient


def test_register_ok(client: TestClient):
    r = client.post('/auth/register', json={'email': 'novo@test.com', 'password': 'senha123'})
    assert r.status_code == 200
    data = r.json()
    assert 'user' in data
    assert data['user']['email'] == 'novo@test.com'
    assert 'id' in data['user']
    assert 'password' not in str(data)


def test_register_duplicate_email(client: TestClient, test_user):
    _, email, _ = test_user
    r = client.post('/auth/register', json={'email': email, 'password': 'outrasenha'})
    assert r.status_code == 400
    assert 'cadastrado' in r.json().get('detail', '').lower()


def test_login_ok_sets_cookies(client: TestClient, test_user):
    _, email, password = test_user
    r = client.post('/auth/login', json={'email': email, 'password': password})
    assert r.status_code == 200
    data = r.json()
    assert data['token_type'] == 'bearer'
    assert 'access_token' in data and len(data['access_token']) > 0
    assert data['user']['email'] == email
    assert 'marketingai_access_token' in r.cookies
    assert 'marketingai_refresh_token' in r.cookies


def test_login_wrong_password(client: TestClient, test_user):
    _, email, _ = test_user
    r = client.post('/auth/login', json={'email': email, 'password': 'wrong'})
    assert r.status_code == 401


def test_login_unknown_email(client: TestClient):
    r = client.post('/auth/login', json={'email': 'naoexiste@test.com', 'password': 'x'})
    assert r.status_code == 401


def test_session_works_with_cookie_auth(client: TestClient, test_user):
    _, email, password = test_user
    login = client.post('/auth/login', json={'email': email, 'password': password})
    assert login.status_code == 200

    session = client.get('/auth/session')
    assert session.status_code == 200
    data = session.json()
    assert data['authenticated'] is True
    assert data['user']['email'] == email


def test_refresh_rotates_session(client: TestClient, test_user):
    _, email, password = test_user
    login = client.post('/auth/login', json={'email': email, 'password': password})
    old_access = login.cookies.get('marketingai_access_token')
    old_refresh = login.cookies.get('marketingai_refresh_token')

    refreshed = client.post('/auth/refresh')
    assert refreshed.status_code == 200
    assert refreshed.json()['user']['email'] == email
    assert refreshed.cookies.get('marketingai_access_token') != old_access
    assert refreshed.cookies.get('marketingai_refresh_token') != old_refresh


def test_logout_clears_session(client: TestClient, test_user):
    _, email, password = test_user
    login = client.post('/auth/login', json={'email': email, 'password': password})
    assert login.status_code == 200

    logout = client.post('/auth/logout')
    assert logout.status_code == 204

    session = client.get('/auth/session')
    assert session.status_code == 401
