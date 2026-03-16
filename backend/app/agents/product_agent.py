from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.product import Product
from app.services.product_intelligence import ProductAnalysisResult, analyze_product


@dataclass(slots=True)
class ProductAgent:
    db: Session

    def run(self, product: Product, sources: list[str]) -> ProductAnalysisResult:
        return analyze_product(self.db, product, sources)