"""Testes dos modulos parser, analyzer e generator."""
import sys
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ia_pipeline.analyzer.service import analyze_business
from ia_pipeline.generator.models import CopyVariation, GeneratedContentItem
from ia_pipeline.generator.service import generate_marketing_content
from ia_pipeline.parser.service import parse_crawl_result
from ia_pipeline.scraping import CrawlResult, PageCapture
from ia_pipeline.services.copywriting_service import generate_copywriting_output
import ia_pipeline.pipeline as pipeline_module


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


def test_copywriting_service_generates_hooks_narrative_ctas_and_ab_variations():
    parsed = parse_crawl_result(_sample_crawl())
    business = analyze_business(parsed)
    page = parsed.pages[0]
    output = generate_copywriting_output("linkedin", "conversao", page, business)
    assert len(output.hooks) == 3
    assert list(output.narrative_structure.keys()) == ["hook", "context", "insight", "proof", "cta"]
    assert len(output.cta_options) == 3
    assert [item.label for item in output.ab_variations] == ["A", "B"]
    assert output.primary_copy


def test_generate_marketing_content_includes_copywriting_fields():
    parsed = parse_crawl_result(_sample_crawl())
    business = analyze_business(parsed)
    generated = generate_marketing_content(
        parsed,
        business,
        target_platform="instagram",
        objective="branding",
        campaign_title="Acme Growth",
    )
    first = generated[0]
    assert first.hooks
    assert first.narrative_structure
    assert first.cta_options
    assert len(first.ab_variations) == 2
    assert first.headlines == first.hooks
    assert first.copy_variations[0].label == "A"


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
    assert generated[0].content_format == "professional_post"
    assert "insight_bullets" in generated[0].structured_output


def test_generate_marketing_content_supports_facebook_platform():
    parsed = parse_crawl_result(_sample_crawl())
    business = analyze_business(parsed)
    generated = generate_marketing_content(
        parsed,
        business,
        target_platform="facebook",
        objective="branding",
        campaign_title="Acme Growth",
    )
    assert len(generated) == 2
    assert all(item.platform == "facebook" for item in generated)
    assert all(item.persuasive_text for item in generated)
    assert all(item.content_format == "community_story_post" for item in generated)
    assert all("community_prompt" in item.structured_output for item in generated)


def test_generate_marketing_content_supports_tiktok_platform():
    parsed = parse_crawl_result(_sample_crawl())
    business = analyze_business(parsed)
    generated = generate_marketing_content(
        parsed,
        business,
        target_platform="tiktok",
        objective="branding",
        campaign_title="Acme Growth",
    )
    assert len(generated) == 2
    assert all(item.platform == "tiktok" for item in generated)
    assert all(item.copy_variations for item in generated)
    assert all(item.content_format == "short_video_concept" for item in generated)
    assert all("scene_beats" in item.structured_output for item in generated)


def test_generate_marketing_content_supports_instagram_structure():
    parsed = parse_crawl_result(_sample_crawl())
    business = analyze_business(parsed)
    generated = generate_marketing_content(parsed, business, target_platform="instagram", objective="branding", campaign_title="Acme Growth")
    first = generated[0]
    assert first.content_format == "caption_visual"
    assert set(["hook", "caption", "carousel_slides", "cta", "hashtags"]).issubset(first.structured_output.keys())


def test_generate_marketing_content_supports_x_structure():
    parsed = parse_crawl_result(_sample_crawl())
    business = analyze_business(parsed)
    generated = generate_marketing_content(parsed, business, target_platform="x", objective="engajamento", campaign_title="Acme Growth")
    first = generated[0]
    assert first.platform == "twitter"
    assert first.content_format == "short_post_or_thread"
    assert set(["post", "thread", "closing_cta", "hashtags"]).issubset(first.structured_output.keys())


def test_generate_marketing_content_supports_youtube_structure():
    parsed = parse_crawl_result(_sample_crawl())
    business = analyze_business(parsed)
    generated = generate_marketing_content(parsed, business, target_platform="youtube", objective="branding", campaign_title="Acme Growth")
    first = generated[0]
    assert first.platform == "youtube"
    assert first.content_format == "video_package"
    assert set(["video_title", "description", "thumbnail_text", "script_outline", "closing_cta"]).issubset(first.structured_output.keys())

def test_run_pipeline_populates_visual_decision_without_unboundlocalerror(monkeypatch, tmp_path):
    crawl = _sample_crawl()
    parsed = parse_crawl_result(crawl)
    business = analyze_business(parsed)
    generated_item = GeneratedContentItem(
        platform="instagram",
        objective="branding",
        source_page_url="https://acme.com",
        screen_type="home",
        screen_label="Pagina inicial",
        headlines=["Hook principal"],
        persuasive_text="Texto persuasivo",
        copy_variations=[CopyVariation(label="A", text="Variacao A")],
        hashtags=["#acme"],
        visual_suggestions=["usar interface do produto"],
        content_format="caption_visual",
        primary_cta="Agende uma demo",
        platform_rules={"tone": "direct"},
        structured_output={"caption": "Texto persuasivo"},
        hooks=["Hook principal"],
        narrative_structure={"hook": "Hook principal", "cta": "Agende uma demo"},
        cta_options=["Agende uma demo"],
        ab_variations=[CopyVariation(label="A", text="Variacao A")],
    )

    monkeypatch.setattr(pipeline_module, "crawl_website", lambda *args, **kwargs: crawl)
    monkeypatch.setattr(pipeline_module, "parse_crawl_result", lambda *_args, **_kwargs: parsed)
    monkeypatch.setattr(pipeline_module, "analyze_business", lambda *_args, **_kwargs: business)
    monkeypatch.setattr(pipeline_module, "generate_marketing_content", lambda *args, **kwargs: [generated_item])
    monkeypatch.setattr(
        pipeline_module,
        "decide_visual_source",
        lambda **kwargs: SimpleNamespace(selected_mode="real", prompt="Prompt visual", recommended_source_path=None),
    )
    monkeypatch.setattr(
        pipeline_module,
        "serialize_visual_decision",
        lambda decision, applied_mode=None: {
            "selected_mode": decision.selected_mode,
            "prompt": decision.prompt,
            "applied_mode": applied_mode,
        },
    )

    result = pipeline_module.run_pipeline(
        url="https://acme.com",
        campaign_title="Acme Growth",
        platforms=["instagram"],
        output_dir=tmp_path,
    )

    assert result.error is None
    assert result.generated_contents
    assert result.generated_contents[0]["visual_decision"]["selected_mode"] == "real"
    assert result.posts[0].visual_decision["selected_mode"] == "real"
