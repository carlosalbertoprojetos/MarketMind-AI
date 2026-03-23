"""Modulo visual: prompt contextual e decisao entre imagem real ou IA."""

from dataclasses import asdict, dataclass

from ia_pipeline.ai_image.service import prompt_builder


REAL_FAVORING_SCREEN_TYPES = {"pricing", "product", "docs", "login", "dashboard", "settings", "table", "report", "list"}
AI_FAVORING_SCREEN_TYPES = {"home", "landing", "about", "blog", "case_study"}
UI_SIGNALS = ("dashboard", "painel", "tela", "fluxo", "plataforma", "modulo", "erp", "crm", "relatorio")
BRAND_SIGNALS = ("marca", "campanha", "conceito", "comunidade", "lifestyle", "emocional", "inspira", "posicionamento")


@dataclass
class VisualDecision:
    selected_mode: str
    reason: str
    prompt: str
    confidence: float
    real_score: int
    ai_score: int
    recommended_source_path: str = ""


def _compact(text: str) -> str:
    return " ".join((text or "").split())


def _contains_any(blob: str, values: tuple[str, ...]) -> bool:
    low = (blob or "").lower()
    return any(item in low for item in values)


def build_visual_prompt(
    *,
    platform: str,
    objective: str,
    headline: str,
    caption: str,
    audience: str,
    screen_label: str,
    screen_type: str,
    value_proposition: str,
    differentiator: str,
    style: str = "modern",
    use_real_reference: bool = False,
) -> str:
    parts = [
        headline,
        caption,
        f"Audience: {audience}" if audience else "",
        f"Screen label: {screen_label}" if screen_label else "",
        f"Screen type: {screen_type}" if screen_type else "",
        f"Value proposition: {value_proposition}" if value_proposition else "",
        f"Differentiator: {differentiator}" if differentiator else "",
        f"Objective: {objective}",
    ]
    content = ". ".join(_compact(part) for part in parts if _compact(part))
    reference_hint = " Use the real product interface as visual reference." if use_real_reference else " Create a conceptual campaign visual without copying any existing UI text."
    return prompt_builder(content + reference_hint, platform, style)


def decide_visual_source(
    *,
    platform: str,
    objective: str,
    screen_type: str,
    screen_label: str,
    headline: str,
    caption: str,
    audience: str,
    value_proposition: str,
    differentiator: str,
    source_images: list[str] | None,
    style: str = "modern",
) -> VisualDecision:
    source_images = [item for item in (source_images or []) if item]
    combined = _compact(" ".join([headline, caption, screen_label, value_proposition, differentiator]))
    normalized_screen_type = (screen_type or "generic").strip().lower()
    normalized_objective = (objective or "branding").strip().lower()
    normalized_platform = (platform or "instagram").strip().lower()
    if normalized_platform == "x":
        normalized_platform = "twitter"

    real_score = 0
    ai_score = 0

    if source_images:
        real_score += 2
        if len(source_images) >= 3:
            real_score += 1
    else:
        ai_score += 3

    if normalized_screen_type in REAL_FAVORING_SCREEN_TYPES:
        real_score += 2
    if normalized_screen_type in AI_FAVORING_SCREEN_TYPES:
        ai_score += 1

    if normalized_objective == "conversao":
        real_score += 1
    elif normalized_objective == "branding":
        ai_score += 2
    else:
        ai_score += 1

    if normalized_platform in {"instagram", "tiktok", "facebook", "youtube"}:
        ai_score += 1
    if normalized_platform in {"linkedin", "twitter"}:
        real_score += 1

    if _contains_any(combined, UI_SIGNALS):
        real_score += 1
    if _contains_any(combined, BRAND_SIGNALS):
        ai_score += 1

    selected_mode = "real" if real_score >= ai_score else "ai"
    reason = (
        "Contexto favorece uso da interface real, com foco em prova visual e aderencia ao produto."
        if selected_mode == "real"
        else "Contexto favorece criativo conceitual gerado por IA, com foco em marca e impacto visual."
    )
    prompt = build_visual_prompt(
        platform=normalized_platform,
        objective=normalized_objective,
        headline=headline,
        caption=caption,
        audience=audience,
        screen_label=screen_label,
        screen_type=normalized_screen_type,
        value_proposition=value_proposition,
        differentiator=differentiator,
        style=style,
        use_real_reference=selected_mode == "real" and bool(source_images),
    )
    confidence = round(abs(real_score - ai_score) / max(real_score + ai_score, 1), 3)
    return VisualDecision(
        selected_mode=selected_mode,
        reason=reason,
        prompt=prompt,
        confidence=confidence,
        real_score=real_score,
        ai_score=ai_score,
        recommended_source_path=source_images[0] if selected_mode == "real" and source_images else "",
    )


def serialize_visual_decision(decision: VisualDecision, applied_mode: str | None = None) -> dict:
    payload = asdict(decision)
    if applied_mode:
        payload["applied_mode"] = applied_mode
    return payload
