from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.content_item import ContentItem
from app.models.enums import ContentType
from app.models.persona import Persona
from app.models.product import Product
from app.services.embedding_service import generate_embedding
from app.services.narrative_engine import NarrativeResult


@dataclass(slots=True)
class ContentResult:
    content_item: ContentItem


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

    item = ContentItem(
        product_id=product.id,
        persona_id=persona.id if persona else None,
        organization_id=product.organization_id,
        content_type=content_type,
        title=f"{content_type.value} - {product.name}",
        brief=base,
        short_version=f"Resumo curto: {narrative_text}",
        medium_version=f"Versao media: {base}",
        long_version=f"Versao longa: {base} {narrative_text}",
        technical_version=f"Detalhe tecnico: {product.name} automatiza fluxos de marketing.",
        sales_version=f"Versao comercial: "
        f"{product.name} acelera resultados com IA e dados.",
        meta={"persona": persona_label},
    )
    item.embedding = generate_embedding(f"{item.title} {item.brief}")
    db.add(item)
    db.commit()
    db.refresh(item)
    return ContentResult(content_item=item)
