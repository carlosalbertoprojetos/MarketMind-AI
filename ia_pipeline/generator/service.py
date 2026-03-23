"""Gera conteudo de marketing por plataforma usando o entendimento do negocio."""

from ia_pipeline import nlp
from ia_pipeline.analyzer.models import BusinessSummary
from ia_pipeline.generator.models import CopyVariation, GeneratedContentItem
from ia_pipeline.parser.models import ParsedSiteContent
from ia_pipeline.services.copywriting_service import generate_copywriting_output


SUPPORTED_PLATFORMS = {"instagram", "facebook", "linkedin", "twitter", "x", "tiktok", "youtube"}
SUPPORTED_OBJECTIVES = {"engajamento", "conversao", "branding"}

PLATFORM_PROFILES = {
    "instagram": {
        "display_name": "Instagram",
        "content_format": "caption_visual",
        "max_caption_chars": 2200,
        "asset_orientation": "square_or_reel_cover",
        "tone": "visual, direto e aspiracional",
        "structure_keys": ["hook", "caption", "carousel_slides", "cta", "hashtags"],
    },
    "tiktok": {
        "display_name": "TikTok",
        "content_format": "short_video_concept",
        "max_caption_chars": 150,
        "asset_orientation": "vertical_video",
        "tone": "rapido, informal e energico",
        "structure_keys": ["on_screen_hook", "caption", "scene_beats", "closing_cta", "hashtags"],
    },
    "linkedin": {
        "display_name": "LinkedIn",
        "content_format": "professional_post",
        "max_caption_chars": 3000,
        "asset_orientation": "landscape_or_document",
        "tone": "profissional, consultivo e orientado a valor",
        "structure_keys": ["hook", "context", "insight_bullets", "closing_cta", "hashtags"],
    },
    "twitter": {
        "display_name": "X",
        "content_format": "short_post_or_thread",
        "max_caption_chars": 280,
        "asset_orientation": "landscape_or_vertical",
        "tone": "curto, agudo e conversacional",
        "structure_keys": ["post", "thread", "closing_cta", "hashtags"],
    },
    "youtube": {
        "display_name": "YouTube",
        "content_format": "video_package",
        "max_caption_chars": 5000,
        "asset_orientation": "thumbnail_16_9",
        "tone": "didatico, narrativo e orientado a retencao",
        "structure_keys": ["video_title", "description", "thumbnail_text", "script_outline", "closing_cta"],
    },
    "facebook": {
        "display_name": "Facebook",
        "content_format": "community_story_post",
        "max_caption_chars": 50000,
        "asset_orientation": "feed_image_or_video",
        "tone": "acessivel, narrativo e comunitario",
        "structure_keys": ["intro", "body", "community_prompt", "cta", "hashtags"],
    },
}


def _normalize_platform(platform: str) -> str:
    low = (platform or "").strip().lower()
    aliases = {"x": "twitter", "fb": "facebook", "yt": "youtube"}
    return aliases.get(low, low)


def _normalize_objective(objective: str) -> str:
    low = (objective or "").strip().lower()
    return low if low in SUPPORTED_OBJECTIVES else "branding"


def _first(items: list[str], fallback: str = "") -> str:
    for item in items:
        text = (item or "").strip()
        if text:
            return text
    return fallback


def _limit(text: str, size: int) -> str:
    clean = " ".join((text or "").split())
    if len(clean) <= size:
        return clean
    return clean[: max(0, size - 3)].rstrip(' ,.;:') + '...'


def _sentences_from_page(page, business_summary: BusinessSummary) -> list[str]:
    sentences = []
    for item in [
        business_summary.value_proposition,
        page.primary_heading,
        *page.headings_h2[:3],
        *page.paragraphs[:4],
    ]:
        text = " ".join((item or "").split())
        if text and text not in sentences:
            sentences.append(text)
    return sentences


def _build_visual_suggestions(page, business_summary: BusinessSummary, objective: str, profile: dict) -> list[str]:
    suggestions = [
        f"Usar a tela '{page.screen_label or page.page_title or page.url}' como referencia visual principal.",
        f"Destacar {page.keywords[0] if page.keywords else business_summary.product_type} com foco em {objective}.",
        f"Compor ativo no formato {profile['asset_orientation']} com tom {profile['tone']}.",
    ]
    if business_summary.differentiators:
        suggestions.append(f"Transformar o diferencial '{business_summary.differentiators[0]}' em conceito visual.")
    if page.ctas:
        suggestions.append(f"Incluir CTA visual inspirado em '{page.ctas[0]}'.")
    return suggestions[:5]


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


def _build_platform_structure(platform: str, page, business_summary: BusinessSummary, persuasive_text: str, headlines: list[str], hashtags: list[str]) -> tuple[str, str, dict]:
    profile = PLATFORM_PROFILES[platform]
    primary_cta = _first(page.ctas, _first(business_summary.ctas, "Saiba mais no site."))
    sentences = _sentences_from_page(page, business_summary)
    hook = _limit(_first(headlines, page.primary_heading or business_summary.value_proposition), 110)
    detail = _limit(_first(page.paragraphs, business_summary.summary), 240)
    proof = _limit(_first(business_summary.differentiators, detail), 180)
    support_points = [sentence for sentence in sentences[1:4] if sentence]

    if platform == "instagram":
        structure = {
            "hook": hook,
            "caption": persuasive_text,
            "carousel_slides": [
                hook,
                _limit(detail, 120),
                _limit(proof, 120),
                _limit(primary_cta, 120),
            ],
            "cta": primary_cta,
            "hashtags": hashtags[:10],
        }
    elif platform == "tiktok":
        structure = {
            "on_screen_hook": _limit(hook, 80),
            "caption": _limit(persuasive_text, 150),
            "scene_beats": [
                _limit(hook, 90),
                _limit(detail, 90),
                _limit(proof, 90),
            ],
            "closing_cta": primary_cta,
            "hashtags": hashtags[:5],
        }
    elif platform == "linkedin":
        structure = {
            "hook": hook,
            "context": _limit(detail, 320),
            "insight_bullets": [_limit(item, 180) for item in support_points[:3]] or [_limit(proof, 180)],
            "closing_cta": primary_cta,
            "hashtags": hashtags[:5],
        }
    elif platform == "twitter":
        thread = [
            _limit(hook, 260),
            _limit(detail, 260),
            _limit(f"Diferencial: {proof}", 260),
            _limit(primary_cta, 240),
        ]
        structure = {
            "post": _limit(persuasive_text, 280),
            "thread": thread,
            "closing_cta": primary_cta,
            "hashtags": hashtags[:3],
        }
    elif platform == "youtube":
        structure = {
            "video_title": _limit(_first(headlines, hook), 100),
            "description": _limit(f"{persuasive_text}\n\nCTA: {primary_cta}", 1800),
            "thumbnail_text": _limit(hook, 60),
            "script_outline": [
                f"Gancho: {_limit(hook, 120)}",
                f"Problema: {_limit(detail, 140)}",
                f"Solucao: {_limit(business_summary.value_proposition or detail, 140)}",
                f"Prova: {_limit(proof, 140)}",
                f"CTA: {_limit(primary_cta, 140)}",
            ],
            "closing_cta": primary_cta,
        }
    else:
        structure = {
            "intro": hook,
            "body": _limit(persuasive_text, 420),
            "community_prompt": _limit(f"Como isso se conecta com a sua operacao hoje?", 120),
            "cta": primary_cta,
            "hashtags": hashtags[:5],
        }

    return profile["content_format"], primary_cta, structure


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

    profile = PLATFORM_PROFILES[platform]
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
        copywriting = generate_copywriting_output(platform, objective, page, business_summary)
        persuasive_text = copywriting.primary_copy or nlp.adapt_for_platform(base_text, platform)
        hashtags = nlp.suggest_hashtags(
            " ".join([campaign_title, business_summary.summary, page.clean_text[:800]]).strip(),
            platform,
            insights=insights,
            content_snippet=page.clean_text[:1800],
        )
        copy_variations = copywriting.ab_variations + _build_copy_variations(platform, objective, persuasive_text, page, business_summary)
        visual_suggestions = _build_visual_suggestions(page, business_summary, objective, profile)
        content_format, primary_cta, structured_output = _build_platform_structure(
            platform,
            page,
            business_summary,
            persuasive_text,
            headlines,
            hashtags,
        )

        contents.append(
            GeneratedContentItem(
                platform=platform,
                objective=objective,
                source_page_url=page.url,
                screen_type=page.screen_type,
                screen_label=page.screen_label,
                headlines=copywriting.hooks or headlines,
                persuasive_text=persuasive_text,
                copy_variations=copy_variations,
                hashtags=hashtags,
                visual_suggestions=visual_suggestions,
                content_format=content_format,
                primary_cta=primary_cta,
                platform_rules=profile,
                structured_output=structured_output,
                hooks=copywriting.hooks,
                narrative_structure=copywriting.narrative_structure,
                cta_options=copywriting.cta_options,
                ab_variations=copywriting.ab_variations,
            )
        )

    return contents
