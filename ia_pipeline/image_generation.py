"""
MarketingAI - Geração e aprimoramento de imagens (Etapa 5).

- Redimensiona screenshots para tamanhos ideais por rede social.
- Aprimoramento básico (contraste, nitidez) com PIL.
- Placeholder para geração de artes/mockups via API (DALL-E, Stable Diffusion, etc.).
"""
import os
import shutil
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    requests = None

try:
    from PIL import Image, ImageEnhance, ImageFilter
except ImportError:
    Image = None
    ImageEnhance = None
    ImageFilter = None

# Tamanhos recomendados por plataforma (width, height) em pixels
PLATFORM_IMAGE_SIZES = {
    "instagram": [(1080, 1080), (1080, 1350), (1080, 566)],   # quadrado, portrait, landscape
    "facebook": [(1200, 630)],   # link share
    "linkedin": [(1200, 627), (1080, 1080)],
    "twitter": [(1200, 675), (1600, 900)],
    "tiktok": [(1080, 1920)],   # vertical 9:16
}

DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "output_images"


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def copy_image_fallback(image_path: str, platform: str, output_dir: Path) -> Optional[str]:
    """
    Se resize falhar ou PIL não existir: copia o arquivo original para a pasta de saída
    (mantém fidelidade ao screenshot/asset do site).
    """
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        src = Path(image_path)
        if not src.is_file():
            return None
        dest = output_dir / f"{src.stem}_{platform}_source{src.suffix or '.png'}"
        shutil.copy2(src, dest)
        return str(dest)
    except Exception:
        return None


def resize_for_platform(
    image_path: str,
    platform: str,
    variant: int = 0,
    output_dir: Optional[Path] = None,
) -> Optional[str]:
    """
    Redimensiona a imagem para o tamanho recomendado da plataforma.
    variant: índice do tamanho na lista (0 = primeiro formato).
    Retorna caminho do arquivo salvo ou None.
    """
    output_dir = output_dir or DEFAULT_OUTPUT_DIR
    if not Image:
        return copy_image_fallback(image_path, platform, output_dir)
    sizes = PLATFORM_IMAGE_SIZES.get(platform.lower())
    if not sizes:
        sizes = [(1080, 1080)]
    w, h = sizes[variant % len(sizes)]
    _ensure_dir(output_dir)
    out_name = Path(image_path).stem + f"_{platform}_{w}x{h}.png"
    out_path = output_dir / out_name
    try:
        img = Image.open(image_path).convert("RGB")
        img = img.resize((w, h), Image.Resampling.LANCZOS)
        img.save(out_path, "PNG", optimize=True)
        return str(out_path)
    except Exception:
        return copy_image_fallback(image_path, platform, output_dir or DEFAULT_OUTPUT_DIR)


def compose_promo_card_from_screenshot(
    image_path: str,
    headline: str,
    platform: str,
    output_dir: Optional[Path] = None,
) -> Optional[str]:
    """
    Sem DALL-E: combina screenshot com faixa de texto (marketing) para carregar narrativa na arte.
    """
    if not Image:
        return None
    output_dir = output_dir or DEFAULT_OUTPUT_DIR
    _ensure_dir(output_dir)
    sizes = PLATFORM_IMAGE_SIZES.get(platform.lower(), [(1080, 1080)])
    w, h = sizes[0]
    try:
        from PIL import ImageDraw, ImageFont

        bg = Image.open(image_path).convert("RGB")
        bg = bg.resize((w, h), Image.Resampling.LANCZOS)
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        bar_h = int(h * 0.22)
        draw.rectangle([(0, h - bar_h), (w, h)], fill=(0, 0, 0, 190))
        text = _clip_headline(headline, 90)
        try:
            font = ImageFont.truetype("arial.ttf", max(18, min(32, w // 28)))
        except Exception:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((w - tw) // 2, h - bar_h + (bar_h - th) // 2), text, font=font, fill=(255, 255, 255, 255))
        bg = Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")
        out_path = output_dir / (Path(image_path).stem + f"_{platform}_promo.png")
        bg.save(out_path, "PNG", optimize=True)
        return str(out_path)
    except Exception:
        return None


def _clip_headline(s: str, n: int) -> str:
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1] + "…"


def enhance_screenshot(image_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Aplica leve aprimoramento: contraste e nitidez.
    Útil para screenshots que serão usados como arte.
    """
    if not Image or not ImageEnhance or not ImageFilter:
        return None
    try:
        img = Image.open(image_path).convert("RGB")
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.1)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.2)
        out = output_path or str(Path(image_path).with_stem(Path(image_path).stem + "_enhanced"))
        if not out.lower().endswith(".png"):
            out += ".png"
        img.save(out, "PNG")
        return out
    except Exception:
        return None


def prompt_for_marketing_image(
    *,
    platform: str,
    headline: str,
    caption: str,
    page_title: str = "",
    page_url: str = "",
    extra_context: str = "",
) -> str:
    """
    Prompt para DALL·E alinhado ao copy de marketing (sem texto na arte).
    """
    ctx = " ".join(
        x for x in (extra_context or "").split()[:120]
    )  # limitar ruído
    parts = [
        f"Professional, eye-catching social media advertisement visual for {platform}.",
        "No text, letters, logos or watermarks in the image.",
        "Clean composition, brand-safe, modern, high quality.",
        f"Creative concept reflecting this message: {headline[:220]}.",
        f"Supporting idea: {caption[:500]}.",
    ]
    if page_title:
        parts.append(f"Website section theme: {page_title[:120]}.")
    if page_url:
        parts.append(f"(Inferred from this business page: {page_url[:80]})")
    if ctx:
        parts.append(f"Keywords: {ctx[:400]}")
    return " ".join(parts)[:3900]


def generate_visual_from_prompt(
    prompt: str,
    platform: str = "instagram",
    output_dir: Optional[Path] = None,
) -> Optional[str]:
    """
    Gera arte visual a partir de um prompt (DALL-E) e salva em disco; sem API retorna None.
    """
    output_dir = output_dir or DEFAULT_OUTPUT_DIR
    _ensure_dir(output_dir)

    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            size_map = {"instagram": "1024x1024", "facebook": "1024x1024", "twitter": "1024x1024", "tiktok": "1024x1792"}
            size = size_map.get(platform.lower(), "1024x1024")
            r = client.images.generate(model="dall-e-3", prompt=prompt[:3900], size=size, n=1)
            url = r.data[0].url
            if url and requests:
                dest = output_dir / f"ai_gen_{platform}_{abs(hash(prompt)) % 10_000_000}.png"
                resp = requests.get(url, timeout=120)
                resp.raise_for_status()
                dest.write_bytes(resp.content)
                return str(dest)
        except Exception:
            pass
    return None


if __name__ == "__main__":
    # Teste de redimensionamento (requer uma imagem em screenshots)
    screenshots_dir = Path(__file__).resolve().parent / "screenshots"
    if screenshots_dir.exists():
        for f in screenshots_dir.glob("*.png"):
            p = resize_for_platform(str(f), "instagram", 0)
            if p:
                print("Salvo:", p)
            break
    else:
        print("Nenhum screenshot em", screenshots_dir, "- rode scraping.py primeiro.")
