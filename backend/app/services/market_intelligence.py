from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.models.competitor import Competitor
from app.models.product import Product


@dataclass(slots=True)
class MarketAnalysisResult:
    product_id: str
    competitive_map: dict[str, Any]


def analyze_market(
    db: Session,
    product: Product,
    competitors: list[dict[str, Any]],
) -> MarketAnalysisResult:
    created = []
    for item in competitors:
        competitor = Competitor(
            product_id=product.id,
            organization_id=product.organization_id,
            name=item.get("name") or "Competitor",
            website_url=item.get("url"),
            positioning=item.get("positioning"),
            marketing_language=item.get("marketing_language"),
            differentiators=item.get("differentiators"),
            summary=item.get("summary"),
        )
        db.add(competitor)
        created.append(competitor)

    db.commit()

    competitive_map = {
        "leader": product.name,
        "challengers": [c.name for c in created],
        "axes": ["automation", "price", "speed"],
    }
    product.extracted_data = {**(product.extracted_data or {}), "competitive_map": competitive_map}
    db.add(product)
    db.commit()
    db.refresh(product)
    return MarketAnalysisResult(product_id=str(product.id), competitive_map=competitive_map)