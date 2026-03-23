"""Pipeline final orientado por tema, objetivo e publico."""

from dataclasses import asdict

from ia_pipeline.analyzer.models import BusinessSummary
from ia_pipeline.generator.service import generate_marketing_content
from ia_pipeline.parser.models import ParsedPageContent, ParsedSiteContent
from ia_pipeline.pipelines.models import FinalABTestSuggestion, FinalContentPipelineResult, FinalPlatformContent
from ia_pipeline.services.visual_service import decide_visual_source, serialize_visual_decision


DEFAULT_PLATFORMS = ["instagram", "tiktok", "linkedin", "x", "youtube", "facebook"]
OBJECTIVE_CTA = {
    "branding": "saiba mais sobre a proposta",
    "engajamento": "comente e compartilhe com o time",
    "conversao": "avance para demo, contato ou cadastro",
}
SUCCESS_METRICS = {
    "instagram": "salvamentos e compartilhamentos",
    "tiktok": "taxa de visualizacao completa",
    "linkedin": "cliques e comentarios qualificados",
    "twitter": "engajamento por impressao",
    "youtube": "CTR da thumbnail e retencao",
    "facebook": "comentarios e cliques no link",
}


def _keyword_seed(theme: str, audience: str) -> list[str]:
    raw = f"{theme} {audience}".replace('/', ' ').replace('-', ' ')
    items = []
    for token in raw.split():
        clean = ''.join(ch for ch in token.lower() if ch.isalnum())
        if len(clean) >= 4 and clean not in items:
            items.append(clean)
    return items[:8] or ["conteudo", "marketing"]


def _normalize_objective(objective: str) -> str:
    low = (objective or '').strip().lower()
    return low if low in OBJECTIVE_CTA else 'branding'


def _build_business_summary(theme: str, objective: str, audience: str) -> BusinessSummary:
    objective = _normalize_objective(objective)
    keywords = _keyword_seed(theme, audience)
    return BusinessSummary(
        source_url='theme://manual',
        product_type='conteudo estrategico',
        value_proposition=theme,
        target_audience=audience,
        differentiators=[
            f"Abordagem orientada a {objective}",
            f"Mensagem adaptada para {audience}",
        ],
        keywords=keywords,
        ctas=[OBJECTIVE_CTA[objective]],
        summary=f"{theme} para {audience} com foco em {objective}.",
        screen_inventory=[{"screen_type": 'concept', "screen_label": theme}],
    )


def _build_parsed_site(theme: str, objective: str, audience: str) -> ParsedSiteContent:
    objective = _normalize_objective(objective)
    keywords = _keyword_seed(theme, audience)
    page = ParsedPageContent(
        url='theme://manual',
        page_title=theme,
        screen_type='concept',
        screen_label=theme,
        primary_heading=theme,
        headings_h2=[
            f"Conteudo adaptado para {audience}",
            f"Objetivo principal: {objective}",
        ],
        headings_h3=[
            "Narrativa orientada a plataforma",
            "Teste de variacoes criativas",
        ],
        paragraphs=[
            f"{theme} foi definido como tema central para comunicar valor de forma clara a {audience}.",
            f"O conteudo prioriza {objective}, com hooks, CTA e estrutura narrativa adequados para cada plataforma.",
            "A comunicacao precisa equilibrar clareza, especificidade e impulso de acao.",
        ],
        keywords=keywords,
        ctas=[OBJECTIVE_CTA[objective]],
        clean_text=f"{theme}. Publico: {audience}. Objetivo: {objective}. Conteudo multiplataforma com CTA claro e testes A/B.",
        meta_description=f"{theme} para {audience} com foco em {objective}.",
    )
    return ParsedSiteContent(source_url='theme://manual', pages=[page], global_keywords=keywords, global_ctas=page.ctas)


def run_final_content_pipeline(theme: str, objective: str, audience: str, platforms: list[str] | None = None, style: str = 'modern') -> FinalContentPipelineResult:
    normalized_objective = _normalize_objective(objective)
    selected_platforms = platforms or DEFAULT_PLATFORMS
    parsed_site = _build_parsed_site(theme, normalized_objective, audience)
    business_summary = _build_business_summary(theme, normalized_objective, audience)
    page = parsed_site.pages[0]
    result = FinalContentPipelineResult(theme=theme, objective=normalized_objective, audience=audience)

    for platform in selected_platforms:
        generated = generate_marketing_content(
            parsed_site,
            business_summary,
            target_platform=platform,
            objective=normalized_objective,
            campaign_title=theme,
        )[0]
        visual_decision = decide_visual_source(
            platform=platform,
            objective=normalized_objective,
            screen_type=generated.screen_type,
            screen_label=generated.screen_label,
            headline=(generated.hooks[0] if generated.hooks else generated.headlines[0]),
            caption=generated.persuasive_text,
            audience=audience,
            value_proposition=business_summary.value_proposition,
            differentiator=(business_summary.differentiators[0] if business_summary.differentiators else ''),
            source_images=[],
            style=style,
        )
        normalized_platform = 'twitter' if platform == 'x' else platform
        result.outputs.append(
            FinalPlatformContent(
                platform=normalized_platform,
                objective=normalized_objective,
                audience=audience,
                content_format=generated.content_format,
                full_content=generated.persuasive_text,
                hooks=generated.hooks,
                narrative_structure=generated.narrative_structure,
                cta_options=generated.cta_options,
                ab_variations=[asdict(item) for item in generated.ab_variations],
                hashtags=generated.hashtags,
                structured_output=generated.structured_output,
                image_prompt=visual_decision.prompt,
                visual_decision=serialize_visual_decision(visual_decision, applied_mode=visual_decision.selected_mode),
            )
        )
        ab_variants = generated.ab_variations[:2]
        if len(ab_variants) >= 2:
            result.ab_test_suggestions.append(
                FinalABTestSuggestion(
                    platform=normalized_platform,
                    hypothesis=f"Hooks e CTA diferentes devem melhorar {SUCCESS_METRICS.get(normalized_platform, 'engajamento')}",
                    variant_a=ab_variants[0].text,
                    variant_b=ab_variants[1].text,
                    success_metric=SUCCESS_METRICS.get(normalized_platform, 'engajamento qualificado'),
                )
            )

    return result
