"""Servicos para geracao de imagens via IA."""
import hashlib
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

from ia_pipeline import image_generation
from ia_pipeline.ai_image.models import ImageAsset
from ia_pipeline.runtime import ensure_output_path, get_logger, get_pipeline_config, write_json_artifact


def prompt_builder(content: str, platform: str, style: str = "modern") -> str:
    clean = " ".join((content or "").split())
    if not clean:
        clean = "Digital business product with a clear value proposition"
    style_guides = {
        "modern": "modern composition, clean UI, professional lighting, premium brand feel",
        "editorial": "editorial art direction, sophisticated framing, strong narrative mood",
        "bold": "high contrast, dynamic composition, impactful visual storytelling",
        "minimal": "minimal aesthetic, negative space, soft shadows, elegant details",
    }
    guide = style_guides.get(style.lower(), style_guides["modern"])
    return (
        f"{clean}. Social media campaign visual for {platform}. "
        f"{guide}. No text, no watermark, no letters, brand-safe, high quality."
    )[:3500]


def _select_provider(provider: str) -> str:
    config = get_pipeline_config()
    desired = (provider or config.image_provider or "auto").lower()
    if desired == "auto":
        if config.openai_api_key:
            return "openai"
        if config.stable_diffusion_url:
            return "stable_diffusion"
        return "mock"
    return desired


def _openai_image(prompt: str, platform: str, style: str, out_dir: Path) -> ImageAsset | None:
    logger = get_logger("marketingai.ai_image.openai")
    path = image_generation.generate_visual_from_prompt(prompt, platform, out_dir)
    if not path:
        logger.warning("OpenAI image generation returned no file for platform=%s", platform)
        return None
    return ImageAsset(
        platform=platform,
        provider="openai",
        style=style,
        prompt=prompt,
        path=str(Path(path).resolve()),
        metadata={"platform": platform, "style": style},
    )


def _stable_diffusion_image(prompt: str, platform: str, style: str, out_dir: Path) -> ImageAsset | None:
    config = get_pipeline_config()
    logger = get_logger("marketingai.ai_image.stable_diffusion")
    if not config.stable_diffusion_url or not requests:
        logger.warning("Stable Diffusion provider unavailable or requests missing")
        return None

    payload = {
        "prompt": prompt,
        "style": style,
        "platform": platform,
    }
    headers = {}
    if config.stable_diffusion_api_key:
        headers["Authorization"] = f"Bearer {config.stable_diffusion_api_key}"

    try:
        response = requests.post(config.stable_diffusion_url, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        content_type = (response.headers.get("content-type") or "").lower()
        filename = f"sd_{platform}_{hashlib.md5(prompt.encode('utf-8', errors='ignore')).hexdigest()[:10]}.png"
        dest = out_dir / filename
        if "application/json" in content_type:
            data = response.json()
            image_url = data.get("url") or data.get("image_url") or ""
            if image_url and requests:
                image_response = requests.get(image_url, timeout=120)
                image_response.raise_for_status()
                dest.write_bytes(image_response.content)
                return ImageAsset(
                    platform=platform,
                    provider="stable_diffusion",
                    style=style,
                    prompt=prompt,
                    path=str(dest.resolve()),
                    url=image_url,
                    metadata=data,
                )
            return None
        dest.write_bytes(response.content)
        return ImageAsset(
            platform=platform,
            provider="stable_diffusion",
            style=style,
            prompt=prompt,
            path=str(dest.resolve()),
            metadata={"content_type": content_type},
        )
    except Exception as exc:
        logger.exception("Stable Diffusion generation failed: %s", exc)
        return None


def _mock_image(prompt: str, platform: str, style: str, out_dir: Path) -> ImageAsset | None:
    logger = get_logger("marketingai.ai_image.mock")
    logger.info("Using mock image generation for platform=%s", platform)
    metadata = {"provider": "mock", "platform": platform, "style": style}
    return ImageAsset(platform=platform, provider="mock", style=style, prompt=prompt, metadata=metadata)


def generate_image(prompt: str, style: str, platform: str, provider: str | None = None) -> ImageAsset:
    logger = get_logger("marketingai.ai_image")
    selected_provider = _select_provider(provider or "")
    out_dir = ensure_output_path("ai_images", platform)

    if selected_provider == "openai":
        asset = _openai_image(prompt, platform, style, out_dir)
    elif selected_provider == "stable_diffusion":
        asset = _stable_diffusion_image(prompt, platform, style, out_dir)
    else:
        asset = _mock_image(prompt, platform, style, out_dir)

    if not asset:
        logger.warning("Falling back to mock image generation for provider=%s", selected_provider)
        asset = _mock_image(prompt, platform, style, out_dir)

    artifact_name = f"ai_images/{platform}/{hashlib.md5((prompt + style).encode('utf-8', errors='ignore')).hexdigest()[:12]}.json"
    write_json_artifact(artifact_name, asset)
    return asset


def generate_image_variations(content: str, platform: str, style: str = "modern", provider: str | None = None) -> list[ImageAsset]:
    config = get_pipeline_config()
    base_prompt = prompt_builder(content, platform, style)
    outputs: list[ImageAsset] = []
    for idx in range(max(1, config.image_variations)):
        prompt = f"{base_prompt} Variation {idx + 1}."
        outputs.append(generate_image(prompt=prompt, style=style, platform=platform, provider=provider))
    return outputs
