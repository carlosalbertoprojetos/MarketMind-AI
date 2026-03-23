import sys
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ia_pipeline.pipelines.final_content_pipeline import run_final_content_pipeline


def test_final_content_pipeline_returns_outputs_for_all_platforms():
    result = run_final_content_pipeline(
        theme='Automacao de marketing para SaaS B2B',
        objective='conversao',
        audience='gestores de growth e marketing',
    )
    assert result.theme
    assert len(result.outputs) == 6
    assert all(item.image_prompt for item in result.outputs)
    assert all(item.ab_variations for item in result.outputs)
    assert len(result.ab_test_suggestions) == 6


def test_final_content_pipeline_route(client: TestClient, auth_headers):
    response = client.post(
        '/campaign/final-content',
        json={
            'theme': 'Gestao comercial com IA',
            'objective': 'branding',
            'audience': 'times de vendas e operacao',
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data['theme'] == 'Gestao comercial com IA'
    assert len(data['outputs']) == 6
    assert 'image_prompt' in data['outputs'][0]
    assert 'ab_test_suggestions' in data
