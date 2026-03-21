"""Gera conteudo de marketing por plataforma usando o entendimento do negocio."""

from ia_pipeline import nlp
from ia_pipeline.analyzer.models import BusinessSummary
from ia_pipeline.generator.models import CopyVariation, GeneratedContentItem
from ia_pipeline.parser.models import ParsedSiteContent


SUPPORTED_PLATFORMS = {"instagram", "linkedin", "twitter", "x"}
SUPPORTED_OBJECTIVES = {"engajamento", "conversao", "branding"}


def _normalize_platform(platform: str) -> str:
    low = (platform or "").strip().lower()
    return "twitter" if low == "x" else low


def _normalize_objective(objective: str) -> str:
    low = (objective or "").strip().lower()
    return low if low in SUPPORTED_OBJECTIVES else "branding"


def _build_visual_suggestions(page, business_summary: BusinessSummary, objective: str) -> list[str]:
    suggestions = [
        f"Usar a tela '{page.screen_label or page.page_title or page.url}' como referencia visual principal.",
        f"Destacar {page.keywords[0] if page.keywords else business_summary.product_type} com foco em {objective}.",
    ]
    if business_summary.differentiators:
        suggestions.append(f"Transformar o diferencial '{business_summary.differentiators[0]}' em conceito visual.")
    if page.ctas:
        suggestions.append(f"Incluir CTA visual inspirado em '{page.ctas[0]}'.")
    return suggestions[:4]


def _build_copy_variations(platform: str, objective: str, base_text: str, page, business_summary: BusinessSummary) -> list[CopyVariation]:
    variants = []
    short_text = nlp.adapt_for_platform(base_text[:220], platform)
    variants.append(CopyVariation(label="short", text=short_text))

    medium_base = f"{business_summary.value_proposition or ''} {base_text}".strip()
    variants.append(CopyVariation(label="medium", text=nlp.adapt_for_platform(medium_base[:500], platform)))

    sales_base = f"{base_text} CTA: {page.ctas[0] if page.ctas else (business_summary.ctas[0] if business_summary.ctas else 'Saiba mais no site.')}"
    variants.append(CopyVariation(label="sales", text=nlp.adapt_for_platform(sales_base[:650], platform)))

    if objective == "engajamento":
        engage_text = f"{base_text} Pergunta para a audiencia: qual desafio voce quer resolver agora?"
        variants.append(CopyVariation(label="engagement", text=nlp.adapt_for_platform(engage_text[:650], platform)))
    elif objective == "conversao":
        conv_text = f"{base_text} Mostre o proximo passo com urgencia e clareza."
        variants.append(CopyVariation(label="conversion", text=nlp.adapt_for_platform(conv_text[:650], platform)))
    else:
        brand_text = f"{base_text} Reforce autoridade, visao e percepcao de marca."
        variants.append(CopyVariation(label="branding", text=nlp.adapt_for_platform(brand_text[:650], platform)))

    return variants


def generate_marketing_content(
    parsed_site: ParsedSiteContent,
    business_summary: BusinessSummary,
    *,
    target_platform: str,
    objective: str = "branding",
    campaign_title: str = "",
) -> list[GeneratedContentItem]:
    platform = _normalize_platform(target_platform)
    objective = _normalize_objective(objective)
    if platform not in SUPPORTED_PLATFORMS:
        raise ValueError(f"Plataforma nao suportada: {target_platform}")

    contents: list[GeneratedContentItem] = []
    for page in parsed_site.pages:
        page_context = " ".join(
            [
                business_summary.summary,
                page.primary_heading,
                " ".join(page.headings_h2[:3]),
                " ".join(page.paragraphs[:4]),
            ]
        ).strip()
        insights = nlp.extract_marketing_insights(page_context[:12000])

        headlines = []
        for candidate in [
            *(insights.headlines or []),
            page.primary_heading,
            page.page_title,
            campaign_title,
            business_summary.value_proposition,
        ]:
            text = (candidate or "").strip()
            if text and text not in headlines:
                headlines.append(text[:120])
            if len(headlines) >= 3:
                break

        base_text = " ".join(
            part for part in [
                business_summary.value_proposition,
                insights.descricoes_curtas[0] if insights.descricoes_curtas else "",
                page.paragraphs[0] if page.paragraphs else "",
            ]
            if part
        ).strip() or page.clean_text[:500]
        persuasive_text = nlp.adapt_for_platform(base_text, platform)
        hashtags = nlp.suggest_hashtags(
            " ".join([campaign_title, business_summary.summary, page.clean_text[:800]]).strip(),
            platform,
            insights=insights,
            content_snippet=page.clean_text[:1800],
        )
        copy_variations = _build_copy_variations(platform, objective, persuasive_text, page, business_summary)
        visual_suggestions = _build_visual_suggestions(page, business_summary, objective)

        contents.append(
            GeneratedContentItem(
                platform=platform,
                objective=objective,
                source_page_url=page.url,
                screen_type=page.screen_type,
                screen_label=page.screen_label,
                headlines=headlines,
                persuasive_text=persuasive_text,
                copy_variations=copy_variations,
                hashtags=hashtags,
                visual_suggestions=visual_suggestions,
            )
        )

    return contents
