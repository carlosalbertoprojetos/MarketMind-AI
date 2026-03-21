"""Testes dos modulos parser, analyzer e generator."""
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ia_pipeline.analyzer.service import analyze_business
from ia_pipeline.generator.service import generate_marketing_content
from ia_pipeline.parser.service import parse_crawl_result
from ia_pipeline.scraping import CrawlResult, PageCapture


def _sample_crawl() -> CrawlResult:
    return CrawlResult(
        start_url="https://acme.com",
        pages=[
            PageCapture(
                url="https://acme.com",
                page_title="Acme Platform",
                primary_heading="Automatize o marketing do seu SaaS",
                meta_description="Plataforma para equipes de growth e marketing",
                screen_type="home",
                screen_label="Pagina inicial",
                raw_html="""
                <html><body>
                  <h1>Automatize o marketing do seu SaaS</h1>
                  <h2>Mais pipeline com menos operacao manual</h2>
                  <p>Gerencie campanhas, leads e conteudo em um so lugar.</p>
                  <p>Agende uma demo e veja a plataforma em acao.</p>
                </body></html>
                """,
                body_text="Gerencie campanhas, leads e conteudo em um so lugar. Agende uma demo e veja a plataforma em acao.",
                internal_links=[
                    {"url": "https://acme.com/precos", "text": "Precos"},
                    {"url": "https://acme.com/demo", "text": "Agende uma demo"},
                ],
            ),
            PageCapture(
                url="https://acme.com/precos",
                page_title="Planos e precos",
                primary_heading="Escolha o plano ideal",
                meta_description="Planos flexiveis para times de marketing",
                screen_type="pricing",
                screen_label="Tela de precos",
                raw_html="""
                <html><body>
                  <h1>Escolha o plano ideal</h1>
                  <h2>ROI claro para sua operacao</h2>
                  <p>Planos mensais e anuais com onboarding incluido.</p>
                  <p>Fale com o time comercial para uma proposta.</p>
                </body></html>
                """,
                body_text="Planos mensais e anuais com onboarding incluido. Fale com o time comercial para uma proposta.",
                internal_links=[
                    {"url": "https://acme.com/demo", "text": "Fale com vendas"},
                ],
            ),
        ],
    )


def test_parse_crawl_result_extracts_headings_keywords_and_ctas():
    parsed = parse_crawl_result(_sample_crawl())
    assert len(parsed.pages) == 2
    assert parsed.pages[0].headings_h2 == ["Mais pipeline com menos operacao manual"]
    assert "marketing" in parsed.global_keywords or "plataforma" in parsed.global_keywords
    assert any("demo" in cta.lower() for cta in parsed.global_ctas)


def test_analyze_business_returns_structured_summary():
    parsed = parse_crawl_result(_sample_crawl())
    business = analyze_business(parsed)
    assert business.product_type in {"software", "negocio digital"}
    assert business.value_proposition
    assert business.summary
    assert len(business.screen_inventory) == 2


def test_generate_marketing_content_returns_variations_for_single_platform():
    parsed = parse_crawl_result(_sample_crawl())
    business = analyze_business(parsed)
    generated = generate_marketing_content(
        parsed,
        business,
        target_platform="linkedin",
        objective="conversao",
        campaign_title="Acme Growth",
    )
    assert len(generated) == 2
    assert generated[0].platform == "linkedin"
    assert generated[0].headlines
    assert generated[0].copy_variations
    assert generated[0].visual_suggestions
