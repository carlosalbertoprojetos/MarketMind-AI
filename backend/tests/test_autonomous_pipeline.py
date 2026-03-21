"""Testes dos novos modulos autonomos."""
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ["MARKETINGAI_PUBLISHER_MODE"] = "mock"
os.environ["MARKETINGAI_IMAGE_PROVIDER"] = "mock"
os.environ["MARKETINGAI_OUTPUT_DIR"] = str(ROOT / "ia_pipeline" / "output_test")
os.environ["MARKETINGAI_MAX_CRAWL_PAGES"] = "2"
os.environ["MARKETINGAI_MAX_CRAWL_DEPTH"] = "1"

from ia_pipeline.ai_image.service import generate_image_variations, prompt_builder
from ia_pipeline.autonomous.service import run_autonomous_cycle
from ia_pipeline.orchestrator.service import run_pipeline as orchestrated_run_pipeline
from ia_pipeline.publisher.service import publish_post, schedule_posts


def test_prompt_builder_and_mock_image_variations():
    prompt = prompt_builder("Sistema SaaS de gestao empresarial", "instagram", "modern")
    assert "instagram" in prompt.lower()
    assets = generate_image_variations("Sistema SaaS de gestao empresarial", "instagram", "modern", provider="mock")
    assert len(assets) >= 1
    assert all(asset.provider == "mock" for asset in assets)


def test_publisher_mock_publish_and_schedule():
    single = publish_post("linkedin", "Texto de valor", image="", hashtags=["#saas"])
    assert single.status == "published"
    assert single.provider == "mock"

    facebook = publish_post("facebook", "Texto para comunidade", image="", hashtags=["#growth"])
    assert facebook.status == "published"
    assert facebook.provider == "mock"

    tiktok = publish_post("tiktok", "Video curto com CTA", image="", hashtags=["#tiktok"])
    assert tiktok.status == "published"
    assert tiktok.provider == "mock"

    batch = schedule_posts(
        [
            {"platform": "instagram", "content": "Post 1", "hashtags": ["#growth"]},
            {"platform": "facebook", "content": "Post 2", "hashtags": ["#community"]},
            {"platform": "tiktok", "content": "Post 3", "hashtags": ["#video"]},
            {"platform": "x", "content": "Post 4", "hashtags": ["#brand"]},
        ]
    )
    assert batch.status in {"completed", "partial_failure"}
    assert len(batch.items) == 4


def test_autonomous_cycle_returns_improvements():
    generated = [
        {
            "platform": "instagram",
            "source_page_url": "https://acme.com/precos",
            "screen_type": "pricing",
            "headlines": ["ROI real para o seu time"],
            "visual_suggestions": ["Usar dashboard moderno"],
        }
    ]
    cycle = run_autonomous_cycle(generated)
    assert cycle.status == "completed"
    assert cycle.improvement_actions
    assert cycle.next_objective in {"branding", "engajamento", "conversao"}


def test_orchestrator_pipeline_runs_with_mock_dependencies(monkeypatch):
    from ia_pipeline.crawler.models import CrawlResult, PageCapture
    from ia_pipeline.orchestrator import service as orchestrator_service

    def fake_crawl(*args, **kwargs):
        return CrawlResult(
            start_url="https://acme.com",
            pages=[
                PageCapture(
                    url="https://acme.com",
                    page_title="Acme Platform",
                    primary_heading="Automatize a operacao comercial",
                    meta_description="Plataforma SaaS para marketing e vendas",
                    screen_type="product",
                    screen_label="Produto principal",
                    raw_html="""
                    <html><body>
                      <h1>Automatize a operacao comercial</h1>
                      <h2>Marketing, vendas e CRM na mesma tela</h2>
                      <p>Ganhe produtividade e previsibilidade com IA.</p>
                      <p>Solicite uma demo para ver a plataforma em acao.</p>
                    </body></html>
                    """,
                    body_text="Ganhe produtividade e previsibilidade com IA. Solicite uma demo para ver a plataforma em acao.",
                    internal_links=[{"url": "https://acme.com/precos", "text": "Precos"}],
                )
            ],
        )

    monkeypatch.setattr(orchestrator_service, "crawl_website", fake_crawl)
    result = orchestrated_run_pipeline("https://acme.com", "instagram", auto_publish=True)
    assert result.status == "completed"
    assert result.business_summary
    assert result.generated_contents
    assert result.image_assets
    assert result.publish_results
    assert result.autonomous_cycle
