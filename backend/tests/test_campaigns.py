from unittest.mock import Mock

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


def test_preview_from_url_returns_422_when_pipeline_fails(client, auth_headers, monkeypatch):
    class DummyOut:
        error = None
        url = "https://example.com"

    def fake_run_pipeline(**kwargs):
        raise RuntimeError("boom")

    import app.routes.campaign as campaign_routes
    fake_module = Mock(run_pipeline=fake_run_pipeline)
    monkeypatch.setattr(campaign_routes, 'Path', campaign_routes.Path)
    monkeypatch.setitem(__import__('sys').modules, 'ia_pipeline.pipeline', fake_module)

    response = client.post(
        '/campaign/preview',
        json={'url': 'https://example.com', 'campaign_title': 'Teste', 'target_platform': 'instagram'},
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert 'Falha ao executar o pipeline' in response.json()['detail']


def test_generate_saved_campaign_returns_422_when_pipeline_reports_error(client, auth_headers, monkeypatch):
    created = client.post('/campaign', json={'title': 'C1', 'content': 'URL: https://example.com'}, headers=auth_headers)
    campaign_id = created.json()['id']

    class DummyOut:
        error = 'crawler falhou'

    import app.routes.campaign as campaign_routes
    fake_module = Mock(run_pipeline=lambda **kwargs: DummyOut())
    monkeypatch.setitem(__import__('sys').modules, 'ia_pipeline.pipeline', fake_module)

    response = client.post(f'/campaign/{campaign_id}/generate', headers=auth_headers)
    assert response.status_code == 422
    assert response.json()['detail'] == 'crawler falhou'



def test_preview_from_url_uses_only_explicit_urls_by_default(client, auth_headers, monkeypatch):
    captured = {}

    class DummyOut:
        error = None
        url = "https://example.com"
        posts = []
        business_summary = {}
        generated_contents = []
        copy_variations = []
        visual_suggestions = []

    def fake_run_pipeline(**kwargs):
        captured.update(kwargs)
        return DummyOut()

    fake_module = Mock(run_pipeline=fake_run_pipeline)
    monkeypatch.setitem(__import__('sys').modules, 'ia_pipeline.pipeline', fake_module)

    response = client.post(
        '/campaign/preview',
        json={
            'url': 'https://example.com',
            'campaign_title': 'Teste',
            'target_platform': 'instagram',
            'source_urls': ['https://example.com/precos', 'https://example.com/faq'],
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert captured['source_urls'] == ['https://example.com/precos', 'https://example.com/faq']
    assert captured['follow_internal_links'] is False
    assert captured['capture_scroll_sections'] is True



def test_preview_rejects_login_url_as_analysis_target(client, auth_headers):
    response = client.post(
        '/campaign/preview',
        json={
            'url': 'https://example.com/login',
            'campaign_title': 'Teste',
            'target_platform': 'instagram',
            'login_url': 'https://example.com/login',
            'login_username': 'user',
            'login_password': 'secret',
        },
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert 'nao pode ser a mesma URL de login' in response.json()['detail']


def test_export_rejects_login_url_as_analysis_target(client, auth_headers):
    response = client.post(
        '/campaign/export',
        json={
            'url': 'https://example.com/login',
            'campaign_title': 'Teste',
            'target_platform': 'instagram',
            'login_url': 'https://example.com/login',
            'login_username': 'user',
            'login_password': 'secret',
        },
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert 'nao pode ser a mesma URL de login' in response.json()['detail']


def test_generate_saved_campaign_persists_posts_and_latest_route_returns_them(client, auth_headers, monkeypatch):
    created = client.post('/campaign', json={'title': 'C1', 'content': 'URL: https://example.com'}, headers=auth_headers)
    campaign_id = created.json()['id']

    class DummyPost:
        platform = 'instagram'
        title = 'Titulo salvo'
        text = 'Texto salvo'
        image_paths = []
        hashtags = ['#teste']
        suggested_times = ['09:00']
        steps = ['Publicar']
        source_page_url = 'https://example.com'
        page_title = 'Example'
        screen_type = 'product'
        screen_label = 'Pagina'
        strategy_summary = 'Resumo'
        content_format = 'caption'
        primary_cta = 'Compre agora'
        platform_rules = {'tone': 'direct'}
        structured_output = {'caption': 'Texto salvo'}
        hooks = ['Hook']
        narrative_structure = {'hook': 'Hook'}
        cta_options = ['Compre agora']
        ab_variations = [{'label': 'A', 'text': 'Variante A'}]
        visual_decision = {'selected_mode': 'real'}

    class DummyOut:
        error = None
        url = 'https://example.com'
        posts = [DummyPost()]
        business_summary = {'value_proposition': 'VP'}
        generated_contents = [{'platform': 'instagram'}]
        copy_variations = []
        visual_suggestions = []

    fake_module = Mock(run_pipeline=lambda **kwargs: DummyOut())
    monkeypatch.setitem(__import__('sys').modules, 'ia_pipeline.pipeline', fake_module)

    response = client.post(f'/campaign/{campaign_id}/generate', headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload['saved_content_id']
    assert payload['posts'][0]['title'] == 'Titulo salvo'

    latest = client.get(f'/campaign/{campaign_id}/saved-posts/latest', headers=auth_headers)
    assert latest.status_code == 200
    latest_payload = latest.json()
    assert latest_payload['saved_content_id'] == payload['saved_content_id']
    assert latest_payload['posts'][0]['text'] == 'Texto salvo'


def test_final_content_route_persists_runs_and_supports_listing_get_and_delete(client, auth_headers, monkeypatch):
    from ia_pipeline.pipelines.models import FinalABTestSuggestion, FinalContentPipelineResult, FinalPlatformContent

    def fake_run_final_content_pipeline(**kwargs):
        return FinalContentPipelineResult(
            theme='Tema teste',
            objective='branding',
            audience='Publico teste',
            outputs=[
                FinalPlatformContent(
                    platform='instagram',
                    objective='branding',
                    audience='Publico teste',
                    content_format='caption',
                    full_content='Conteudo salvo',
                    hooks=['Hook'],
                    cta_options=['CTA'],
                    image_prompt='Prompt',
                    visual_decision={'selected_mode': 'ai'},
                )
            ],
            ab_test_suggestions=[
                FinalABTestSuggestion(
                    platform='instagram',
                    hypothesis='Hipotese',
                    variant_a='A',
                    variant_b='B',
                    success_metric='CTR',
                )
            ],
        )

    fake_module = Mock(run_final_content_pipeline=fake_run_final_content_pipeline)
    monkeypatch.setitem(__import__('sys').modules, 'ia_pipeline.pipelines.final_content_pipeline', fake_module)

    response = client.post(
        '/campaign/final-content',
        json={'theme': 'Tema teste', 'objective': 'branding', 'audience': 'Publico teste', 'platforms': ['instagram'], 'style': 'modern'},
        headers=auth_headers,
    )
    assert response.status_code == 200
    payload = response.json()
    saved_id = payload['saved_content_id']
    assert saved_id

    listing = client.get('/campaign/final-content/saved', headers=auth_headers)
    assert listing.status_code == 200
    assert listing.json()['total'] >= 1
    assert listing.json()['items'][0]['id'] == saved_id

    detail = client.get(f'/campaign/final-content/saved/{saved_id}', headers=auth_headers)
    assert detail.status_code == 200
    assert detail.json()['theme'] == 'Tema teste'
    assert detail.json()['outputs'][0]['full_content'] == 'Conteudo salvo'

    delete_resp = client.delete(f'/campaign/final-content/saved/{saved_id}', headers=auth_headers)
    assert delete_resp.status_code == 204

    missing = client.get(f'/campaign/final-content/saved/{saved_id}', headers=auth_headers)
    assert missing.status_code == 404



def test_final_content_saved_listing_supports_filters_and_real_total(client, auth_headers, monkeypatch):
    from ia_pipeline.pipelines.models import FinalContentPipelineResult, FinalPlatformContent

    calls = [
        ('Tema vendas', 'branding', 'vendas', ['instagram'], 'modern'),
        ('Tema financeiro', 'branding', 'financeiro', ['linkedin'], 'modern'),
    ]

    def fake_run_final_content_pipeline(theme, objective, audience, platforms, style):
        return FinalContentPipelineResult(
            theme=theme,
            objective=objective,
            audience=audience,
            outputs=[
                FinalPlatformContent(
                    platform=platforms[0],
                    objective=objective,
                    audience=audience,
                    content_format='caption',
                    full_content=f'Conteudo {theme}',
                )
            ],
            ab_test_suggestions=[],
        )

    fake_module = Mock(run_final_content_pipeline=fake_run_final_content_pipeline)
    monkeypatch.setitem(__import__('sys').modules, 'ia_pipeline.pipelines.final_content_pipeline', fake_module)

    for theme, objective, audience, platforms, style in calls:
        response = client.post(
            '/campaign/final-content',
            json={'theme': theme, 'objective': objective, 'audience': audience, 'platforms': platforms, 'style': style},
            headers=auth_headers,
        )
        assert response.status_code == 200

    listing = client.get('/campaign/final-content/saved?limit=1', headers=auth_headers)
    assert listing.status_code == 200
    payload = listing.json()
    assert payload['limit'] == 1
    assert payload['total'] == 2
    assert len(payload['items']) == 1

    filtered = client.get('/campaign/final-content/saved?platform=linkedin&search=financeiro', headers=auth_headers)
    assert filtered.status_code == 200
    filtered_payload = filtered.json()
    assert filtered_payload['total'] == 1
    assert filtered_payload['items'][0]['theme'] == 'Tema financeiro'

    multi_filtered = client.get('/campaign/final-content/saved?platforms=instagram,linkedin', headers=auth_headers)
    assert multi_filtered.status_code == 200
    multi_filtered_payload = multi_filtered.json()
    assert multi_filtered_payload['total'] == 2
    assert {item['theme'] for item in multi_filtered_payload['items']} == {'Tema vendas', 'Tema financeiro'}


def test_generate_saved_campaign_ignores_additional_urls_block_when_extracting_primary_url(client, auth_headers, monkeypatch):
    created = client.post(
        '/campaign',
        json={
            'title': 'C1',
            'content': 'URL: http://127.0.0.1:8000/\n\nADDITIONAL_URLS:\nhttp://127.0.0.1:8000/conta/entrar/\nhttp://127.0.0.1:8000/conta/painel/\nhttp://127.0.0.1:8000/cursos/\nEND_ADDITIONAL_URLS\n\nNotas',
        },
        headers=auth_headers,
    )
    campaign_id = created.json()['id']
    captured = {}

    class DummyOut:
        error = None
        url = 'http://127.0.0.1:8000/'
        posts = []
        business_summary = {}
        generated_contents = []
        copy_variations = []
        visual_suggestions = []

    def fake_run_pipeline(**kwargs):
        captured.update(kwargs)
        return DummyOut()

    fake_module = Mock(run_pipeline=fake_run_pipeline)
    monkeypatch.setitem(__import__('sys').modules, 'ia_pipeline.pipeline', fake_module)

    response = client.post(f'/campaign/{campaign_id}/generate', headers=auth_headers)

    assert response.status_code == 200
    assert captured['url'] == 'http://127.0.0.1:8000/'


def test_generate_saved_campaign_restores_saved_credentials(client, auth_headers, monkeypatch):
    cred = client.post(
        '/credentials',
        json={
            'site_name': 'Portal fechado',
            'login_url': 'http://127.0.0.1:8000/conta/entrar/',
            'username': 'carlosalberto',
            'password': '@Testando123',
        },
        headers=auth_headers,
    )
    cred_id = cred.json()['id']
    created = client.post(
        '/campaign',
        json={
            'title': 'C1',
            'content': f'URL: http://127.0.0.1:8000/\n\nCREDENTIALS_ID: {cred_id}',
        },
        headers=auth_headers,
    )
    campaign_id = created.json()['id']
    captured = {}

    class DummyOut:
        error = None
        url = 'http://127.0.0.1:8000/'
        posts = []
        business_summary = {}
        generated_contents = []
        copy_variations = []
        visual_suggestions = []

    def fake_run_pipeline(**kwargs):
        captured.update(kwargs)
        return DummyOut()

    fake_module = Mock(run_pipeline=fake_run_pipeline)
    monkeypatch.setitem(__import__('sys').modules, 'ia_pipeline.pipeline', fake_module)

    response = client.post(f'/campaign/{campaign_id}/generate', headers=auth_headers)

    assert response.status_code == 200
    assert captured['login_url'] == 'http://127.0.0.1:8000/conta/entrar/'
    assert captured['login_user'] == 'carlosalberto'
    assert captured['login_pass'] == '@Testando123'


def test_generate_saved_campaign_uses_saved_platforms_block(client, auth_headers, monkeypatch):
    created = client.post(
        '/campaign',
        json={
            'title': 'C1',
            'content': 'URL: http://127.0.0.1:8000/\n\nPLATFORMS:\ninstagram\nyoutube\nEND_PLATFORMS\n\nNotas',
        },
        headers=auth_headers,
    )
    campaign_id = created.json()['id']
    captured = {}

    class DummyOut:
        error = None
        url = 'http://127.0.0.1:8000/'
        posts = []
        business_summary = {}
        generated_contents = []
        copy_variations = []
        visual_suggestions = []

    def fake_run_pipeline(**kwargs):
        captured.update(kwargs)
        return DummyOut()

    fake_module = Mock(run_pipeline=fake_run_pipeline)
    monkeypatch.setitem(__import__('sys').modules, 'ia_pipeline.pipeline', fake_module)

    response = client.post(f'/campaign/{campaign_id}/generate', headers=auth_headers)

    assert response.status_code == 200
    assert captured['platforms'] == ['instagram', 'youtube']


def test_generation_history_includes_platforms(client, auth_headers, monkeypatch):
    created = client.post('/campaign', json={'title': 'C1', 'content': 'URL: https://example.com'}, headers=auth_headers)
    campaign_id = created.json()['id']

    class DummyPost:
        def __init__(self, platform):
            self.platform = platform
            self.title = f'Titulo {platform}'
            self.text = 'Texto'
            self.image_paths = []
            self.hashtags = []
            self.suggested_times = []
            self.steps = []
            self.source_page_url = 'https://example.com'
            self.page_title = 'Example'
            self.screen_type = 'product'
            self.screen_label = 'Pagina'
            self.strategy_summary = 'Resumo'
            self.content_format = 'caption'
            self.primary_cta = 'CTA'
            self.platform_rules = {}
            self.structured_output = {}
            self.hooks = []
            self.narrative_structure = {}
            self.cta_options = []
            self.ab_variations = []
            self.visual_decision = {}

    class DummyOut:
        error = None
        url = 'https://example.com'
        posts = [DummyPost('instagram'), DummyPost('linkedin')]
        business_summary = {}
        generated_contents = []
        copy_variations = []
        visual_suggestions = []

    fake_module = Mock(run_pipeline=lambda **kwargs: DummyOut())
    monkeypatch.setitem(__import__('sys').modules, 'ia_pipeline.pipeline', fake_module)

    generated = client.post(f'/campaign/{campaign_id}/generate', headers=auth_headers)
    assert generated.status_code == 200

    history = client.get(f'/campaign/{campaign_id}/generations', headers=auth_headers)
    assert history.status_code == 200
    payload = history.json()
    assert payload['generations'][0]['platforms'] == ['instagram', 'linkedin']


def test_export_campaign_package_writes_manifest_with_platforms(client, auth_headers, monkeypatch):
    class DummyPost:
        def __init__(self, platform):
            self.platform = platform
            self.title = f'Titulo {platform}'
            self.text = 'Texto'
            self.image_paths = []
            self.hashtags = ['#teste']
            self.steps = ['Publicar']
            self.source_page_url = 'https://example.com'
            self.page_title = 'Example'

    class DummyOut:
        error = None
        url = 'https://example.com'
        posts = [DummyPost('instagram'), DummyPost('linkedin')]

    fake_module = Mock(run_pipeline=lambda **kwargs: DummyOut())
    monkeypatch.setitem(__import__('sys').modules, 'ia_pipeline.pipeline', fake_module)

    response = client.post(
        '/campaign/export',
        json={'url': 'https://example.com', 'campaign_title': 'Teste', 'platforms': ['instagram', 'linkedin']},
        headers=auth_headers,
    )
    assert response.status_code == 200
    import io, json as _json, zipfile
    archive = zipfile.ZipFile(io.BytesIO(response.content))
    assert 'manifest.json' in archive.namelist()
    assert 'platforms.txt' in archive.namelist()
    manifest = _json.loads(archive.read('manifest.json').decode('utf-8'))
    assert manifest['platforms'] == ['instagram', 'linkedin']
    platforms_txt = archive.read('platforms.txt').decode('utf-8')
    assert platforms_txt.strip().splitlines() == ['instagram', 'linkedin']
