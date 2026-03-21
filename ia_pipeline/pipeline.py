"""
MarketingAI - Orquestracao do fluxo de marketing a partir de uma URL.

Fluxo:
1. crawler: navega pelo site e segue links internos relevantes
2. parser: extrai headings, paragrafos, palavras-chave e CTAs
3. analyzer: entende o negocio e produz um resumo estruturado
4. generator: gera copy, variacoes e ideias visuais por rede social
5. image_generation: cria ativos a partir do screenshot ou de prompt IA
"""
import hashlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

from ia_pipeline.analyzer.service import analyze_business
from ia_pipeline.crawler.service import crawl_website
from ia_pipeline.generator.service import generate_marketing_content
from ia_pipeline.parser.service import parse_crawl_result


SUGGESTED_POST_TIMES = {
    "instagram": ["09:00", "12:00", "19:00", "21:00"],
    "facebook": ["09:00", "13:00", "18:00"],
    "linkedin": ["08:00", "12:00", "17:00"],
    "twitter": ["08:00", "12:00", "18:00", "22:00"],
    "tiktok": ["12:00", "19:00", "21:00"],
}


@dataclass
class PostPreview:
    platform: str
    title: str
    text: str
    image_paths: list[str] = field(default_factory=list)
    hashtags: list[str] = field(default_factory=list)
    suggested_times: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)
    source_page_url: str = ""
    page_title: str = ""
    screen_type: str = "generic"
    screen_label: str = ""
    strategy_summary: str = ""


@dataclass
class CampaignOutput:
    campaign_id: Optional[int] = None
    url: str = ""
    posts: list[PostPreview] = field(default_factory=list)
    all_image_paths: list[str] = field(default_factory=list)
    business_summary: dict = field(default_factory=dict)
    generated_contents: list[dict] = field(default_factory=list)
    copy_variations: list[dict] = field(default_factory=list)
    visual_suggestions: list[dict] = field(default_factory=list)
    error: Optional[str] = None


def _image_mode() -> str:
    import os

    raw = (os.environ.get("MARKETINGAI_IMAGE_SOURCE") or "").strip().lower()
    if raw in ("screenshot", "site", "compose"):
        return "screenshot"
    if raw in ("both", "dalle+screenshot", "screenshot+dalle"):
        return "both"
    if raw in ("marketing_dalle", "dalle", "ai", "marketing"):
        return "marketing_dalle"
    return "marketing_dalle" if os.environ.get("OPENAI_API_KEY") else "screenshot"


def _abs_paths(paths: list[str]) -> list[str]:
    out: list[str] = []
    for path in paths or []:
        try:
            out.append(str(Path(path).resolve()))
        except OSError:
            out.append(str(path))
    return out


def _steps_for_platform(platform: str) -> list[str]:
    steps = {
        "instagram": [
            "Abra o Instagram e selecione a imagem ou arte gerada.",
            "Cole a legenda adaptada para a rede.",
            "Revise hashtags e publique.",
        ],
        "linkedin": [
            "No LinkedIn, inicie uma nova publicacao.",
            "Use a copy com foco em valor e credibilidade.",
            "Adicione a imagem e publique.",
        ],
        "twitter": [
            "No X, crie um novo tweet.",
            "Use a variacao curta e direta.",
            "Anexe a imagem e publique.",
        ],
        "facebook": [
            "No Facebook, inicie uma nova publicacao.",
            "Cole o texto e anexe a arte.",
            "Revise e publique.",
        ],
        "tiktok": [
            "No TikTok, suba o criativo.",
            "Use a legenda curta sugerida.",
            "Publique no horario recomendado.",
        ],
    }
    return steps.get(platform.lower(), ["Acesse a rede social e publique o conteudo."])


def _page_slug(url: str) -> str:
    return hashlib.md5((url or "").encode("utf-8", errors="ignore")).hexdigest()[:12]


def _first_non_empty(items: list[str]) -> str:
    for item in items:
        text = (item or "").strip()
        if text:
            return text
    return ""


def run_pipeline(
    url: str,
    campaign_title: str,
    platforms: list[str],
    *,
    login_url: Optional[str] = None,
    login_user: Optional[str] = None,
    login_pass: Optional[str] = None,
    output_dir: Optional[Path] = None,
    max_crawl_pages: int = 5,
    max_crawl_depth: int = 2,
    objective: str = "branding",
) -> CampaignOutput:
    from ia_pipeline import image_generation

    output_dir = output_dir or Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    result = CampaignOutput(url=url)

    crawl = crawl_website(
        url,
        output_dir=output_dir / "screenshots",
        login_url=login_url,
        login_username=login_user,
        login_password=login_pass,
        max_pages=max_crawl_pages,
        max_depth=max_crawl_depth,
        max_links_per_page=14,
        wait_seconds=1.5,
        run_ocr=True,
    )
    if crawl.error:
        result.error = crawl.error
        return result

    parsed_site = parse_crawl_result(crawl)
    business_summary = analyze_business(parsed_site)
    result.business_summary = asdict(business_summary)

    crawl_page_map = {page.url: page for page in crawl.pages}
    img_mode = _image_mode()
    import os

    has_openai = bool(os.environ.get("OPENAI_API_KEY"))
    normalized_platforms = platforms or ["instagram"]

    for platform in normalized_platforms:
        generated_items = generate_marketing_content(
            parsed_site,
            business_summary,
            target_platform=platform,
            objective=objective,
            campaign_title=campaign_title,
        )

        for generated in generated_items:
            result.generated_contents.append(
                {
                    "platform": generated.platform,
                    "objective": generated.objective,
                    "source_page_url": generated.source_page_url,
                    "screen_type": generated.screen_type,
                    "screen_label": generated.screen_label,
                    "headlines": generated.headlines,
                    "persuasive_text": generated.persuasive_text,
                    "hashtags": generated.hashtags,
                    "visual_suggestions": generated.visual_suggestions,
                }
            )
            for variation in generated.copy_variations:
                result.copy_variations.append(
                    {
                        "platform": generated.platform,
                        "source_page_url": generated.source_page_url,
                        "label": variation.label,
                        "text": variation.text,
                    }
                )
            result.visual_suggestions.append(
                {
                    "platform": generated.platform,
                    "source_page_url": generated.source_page_url,
                    "suggestions": generated.visual_suggestions,
                }
            )

            source_page = crawl_page_map.get(generated.source_page_url)
            source_images = []
            if source_page:
                source_images = list(source_page.screenshot_paths) + list(source_page.extracted_image_paths)
                result.all_image_paths.extend(source_images)

            img_subdir = output_dir / "images" / generated.platform / _page_slug(generated.source_page_url)
            img_subdir.mkdir(parents=True, exist_ok=True)
            image_paths: list[str] = []

            selected_title = _first_non_empty(generated.headlines) or generated.screen_label or campaign_title or generated.source_page_url
            selected_text = generated.persuasive_text or _first_non_empty([variation.text for variation in generated.copy_variations])

            want_dalle = img_mode in ("marketing_dalle", "both") and has_openai
            if want_dalle:
                prompt = image_generation.prompt_for_marketing_image(
                    platform=generated.platform,
                    headline=selected_title,
                    caption=selected_text,
                    page_title=generated.screen_label,
                    page_url=generated.source_page_url,
                    extra_context=" ".join(generated.visual_suggestions[:3]),
                )
                generated_image = image_generation.generate_visual_from_prompt(prompt, generated.platform, img_subdir)
                if generated_image:
                    image_paths.append(generated_image)

            want_screenshot = img_mode in ("screenshot", "both") or not image_paths
            if want_screenshot and source_images:
                primary_image = source_images[0]
                resized = image_generation.resize_for_platform(primary_image, generated.platform, 0, img_subdir)
                if not resized:
                    resized = image_generation.copy_image_fallback(primary_image, generated.platform, img_subdir)
                promo = None
                if image_generation.Image:
                    promo = image_generation.compose_promo_card_from_screenshot(
                        primary_image,
                        selected_title,
                        generated.platform,
                        img_subdir,
                    )
                if img_mode == "both" and image_paths and promo:
                    image_paths.append(promo)
                elif img_mode == "both" and image_paths and resized:
                    image_paths.append(resized)
                elif not image_paths:
                    if promo:
                        image_paths.append(promo)
                    elif resized:
                        image_paths.append(resized)

            post = PostPreview(
                platform=generated.platform,
                title=selected_title,
                text=selected_text,
                image_paths=_abs_paths(image_paths),
                hashtags=generated.hashtags,
                suggested_times=SUGGESTED_POST_TIMES.get(generated.platform.lower(), ["09:00", "18:00"]),
                steps=_steps_for_platform(generated.platform),
                source_page_url=generated.source_page_url,
                page_title=source_page.page_title if source_page else "",
                screen_type=generated.screen_type,
                screen_label=generated.screen_label,
                strategy_summary=business_summary.summary,
            )
            result.posts.append(post)
            result.all_image_paths.extend(post.image_paths)

    return result
