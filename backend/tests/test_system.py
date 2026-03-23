from unittest.mock import Mock


def test_stop_local_requires_auth(client):
    response = client.post('/system/stop-local')
    assert response.status_code == 401


def test_stop_local_starts_script(client, auth_headers, monkeypatch):
    monkeypatch.setenv('MARKETINGAI_LOCAL_CONTROL', '1')
    import app.routes.system as system_routes

    launched = {}

    def fake_popen(args, cwd=None, stdout=None, stderr=None):
        launched['args'] = args
        launched['cwd'] = cwd
        return Mock()

    monkeypatch.setattr(system_routes.subprocess, 'Popen', fake_popen)

    response = client.post('/system/stop-local', headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body['status'] == 'stopping'
    assert 'cmd' in launched['args'][0].lower()



def test_stop_local_requires_run_bat_flag(client, auth_headers, monkeypatch):
    monkeypatch.delenv('MARKETINGAI_LOCAL_CONTROL', raising=False)
    response = client.post('/system/stop-local', headers=auth_headers)
    assert response.status_code == 403
    assert 'run.bat' in response.json()['detail']
