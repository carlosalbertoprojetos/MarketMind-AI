from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.integrations.crawler import fetch_url
from app.models.product import Product
from app.services.embedding_service import generate_embedding
from app.services.semantic_extraction import extract_semantics


@dataclass(slots=True)
class ProductAnalysisResult:
    product_id: str
    extracted_data: dict[str, Any]


def _default_extraction(product: Product, sources: list[str]) -> dict[str, Any]:
    semantics = extract_semantics(product.description or product.name)
    return {
        "sources": sources,
        "features": semantics.features,
        "benefits": semantics.benefits,
        "value_proposition": semantics.value_proposition,
        "target_audience": semantics.target_audience,
        "differentiators": semantics.differentiators,
        "use_cases": semantics.use_cases,
    }


def analyze_product(db: Session, product: Product, sources: list[str]) -> ProductAnalysisResult:
    crawled: list[dict[str, Any]] = []
    raw_texts: list[str] = []
    for source in sources:
        if source.startswith("http"):
            result = fetch_url(source)
            crawled.append(
                {
                    "url": result.url,
                    "status_code": result.status_code,
                    "title": result.title,
                    "error": result.error,
                    "text_length": len(result.text),
                }
            )
            if result.text:
                raw_texts.append(result.text)
        else:
            raw_texts.append(source)

    combined_text = " ".join(raw_texts).strip()
    extracted = _default_extraction(product, sources)
    if combined_text:
        semantics = extract_semantics(combined_text)
        extracted = {
            **extracted,
            "features": semantics.features,
            "benefits": semantics.benefits,
            "value_proposition": semantics.value_proposition,
            "target_audience": semantics.target_audience,
            "differentiators": semantics.differentiators,
            "use_cases": semantics.use_cases,
        }

    extracted["crawl"] = crawled
    if combined_text:
        product.embedding = generate_embedding(f\"{product.name} {combined_text}\")

    if product.extracted_data:
        merged = {**product.extracted_data, **extracted}
    else:
        merged = extracted
    product.extracted_data = merged
    db.add(product)
    db.commit()
    db.refresh(product)
    return ProductAnalysisResult(product_id=str(product.id), extracted_data=merged)
