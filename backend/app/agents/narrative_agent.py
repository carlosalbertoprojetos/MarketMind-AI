from dataclasses import dataclass

from app.models.persona import Persona
from app.models.product import Product
from app.services.narrative_engine import NarrativeResult, build_narrative


@dataclass(slots=True)
class NarrativeAgent:
    def run(self, product: Product, persona: Persona | None = None) -> NarrativeResult:
        return build_narrative(product, persona)