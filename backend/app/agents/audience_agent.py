from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.product import Product
from app.services.audience_intelligence import AudienceResult, generate_personas


@dataclass(slots=True)
class AudienceAgent:
    db: Session

    def run(self, product: Product, count: int = 3) -> AudienceResult:
        return generate_personas(self.db, product, count)