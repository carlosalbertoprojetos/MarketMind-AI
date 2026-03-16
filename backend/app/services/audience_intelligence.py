from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.persona import Persona
from app.models.product import Product


@dataclass(slots=True)
class AudienceResult:
    product_id: str
    personas: list[Persona]


def generate_personas(db: Session, product: Product, count: int = 3) -> AudienceResult:
    templates = [
        ("Carla", "Head de Marketing", "CAC alto", "Escalar demanda"),
        ("Rafael", "Product Marketing", "Baixa conversao", "Alinhar proposta de valor"),
        ("Luisa", "Growth", "Pipeline instavel", "Previsibilidade em campanhas"),
    ]
    personas: list[Persona] = []
    for idx in range(min(count, len(templates))):
        name, profile, problem, goal = templates[idx]
        persona = Persona(
            product_id=product.id,
            organization_id=product.organization_id,
            name=name,
            profile=profile,
            problems=problem,
            goals=goal,
            communication_style="Direta, consultiva e orientada a dados",
        )
        db.add(persona)
        personas.append(persona)

    db.commit()
    return AudienceResult(product_id=str(product.id), personas=personas)