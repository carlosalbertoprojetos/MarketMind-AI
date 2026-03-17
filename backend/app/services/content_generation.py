from __future__ import annotations

from dataclasses import dataclass
import json
import logging

from sqlalchemy.orm import Session

from app.models.content_item import ContentItem
from app.models.enums import ContentType
from app.models.persona import Persona
from app.models.product import Product
from app.core.config import settings
from app.services.openai_client import get_openai_client
from app.services.embedding_service import generate_embedding
from app.services.narrative_engine import NarrativeResult


@dataclass(slots=True)
class ContentResult:
    content_item: ContentItem


logger = logging.getLogger(__name__)


def generate_content(
    db: Session,
    product: Product,
    content_type: ContentType,
    persona: Persona | None = None,
    narrative: NarrativeResult | None = None,
    brief: str | None = None,
) -> ContentResult:
    narrative_text = narrative.solution if narrative else product.name
    persona_label = persona.name if persona else "Audience"
    base = brief or f"Conteudo para {persona_label} sobre {product.name}."
    content_payload = None
    if settings.OPENAI_API_KEY:
        content_payload = _generate_with_openai(
            product,
            content_type,
            persona_label,
            narrative_text,
            base,
        )

    if not content_payload:
        content_payload = {
            "title": f"{content_type.value} - {product.name}",
            "short_version": f"Resumo curto: {narrative_text}",
            "medium_version": f"Versao media: {base}",
            "long_version": f"Versao longa: {base} {narrative_text}",
            "technical_version": (
                f"Detalhe tecnico: {product.name} automatiza fluxos de marketing."
            ),
            "sales_version": f"Versao comercial: {product.name} acelera resultados com IA e dados.",
        }

    item = ContentItem(
        product_id=product.id,
        persona_id=persona.id if persona else None,
        organization_id=product.organization_id,
        content_type=content_type,
        title=content_payload.get("title"),
        brief=base,
        short_version=content_payload.get("short_version"),
        medium_version=content_payload.get("medium_version"),
        long_version=content_payload.get("long_version"),
        technical_version=content_payload.get("technical_version"),
        sales_version=content_payload.get("sales_version"),
        meta={"persona": persona_label, "source": "openai" if settings.OPENAI_API_KEY else "template"},
    )
    item.embedding = generate_embedding(f"{item.title} {item.brief}")
    db.add(item)
    db.commit()
    db.refresh(item)
    return ContentResult(content_item=item)


def _generate_with_openai(
    product: Product,
    content_type: ContentType,
    persona_label: str,
    narrative_text: str,
    brief: str,
) -> dict | None:
    try:
        client = get_openai_client()
        system = (
            "Voce e um estrategista de marketing SaaS. "
            "Responda APENAS com JSON valido, sem markdown, com as chaves: "
            "title, short_version, medium_version, long_version, technical_version, sales_version."
        )
        user = (
            f"Produto: {product.name}\n"
            f"Descricao: {product.description or 'N/A'}\n"
            f"Persona: {persona_label}\n"
            f"Narrativa: {narrative_text}\n"
            f"Brief: {brief}\n"
            f"Tipo de conteudo: {content_type.value}\n"
            "Idioma: pt-BR\n"
        )
        response = client.responses.create(
            model=settings.OPENAI_TEXT_MODEL,
            input=[
                {
                    "role": "system",
                    "content": [{"type": "text", "text": system}],
                },
                {
                    "role": "user",
                    "content": [{"type": "text", "text": user}],
                },
            ],
            temperature=settings.OPENAI_TEXT_TEMPERATURE,
        )
        raw_text = getattr(response, "output_text", None)
        if not raw_text:
            return None
        payload = _parse_json_payload(raw_text)
        if not payload:
            return None
        return payload
    except Exception as exc:  # pragma: no cover - network errors vary
        logger.warning("OpenAI content generation failed, using fallback: %s", exc)
        return None


def _parse_json_payload(raw_text: str) -> dict | None:
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.strip("`")
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
