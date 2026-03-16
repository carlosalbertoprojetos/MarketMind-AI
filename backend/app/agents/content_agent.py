from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.enums import ContentType
from app.models.persona import Persona
from app.models.product import Product
from app.services.content_generation import ContentResult, generate_content
from app.services.narrative_engine import NarrativeResult


@dataclass(slots=True)
class ContentAgent:
    db: Session

    def run(
        self,
        product: Product,
        content_type: ContentType,
        persona: Persona | None = None,
        narrative: NarrativeResult | None = None,
        brief: str | None = None,
    ) -> ContentResult:
        return generate_content(self.db, product, content_type, persona, narrative, brief)