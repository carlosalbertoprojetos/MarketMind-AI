from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.models.product import Product
from app.services.market_intelligence import MarketAnalysisResult, analyze_market


@dataclass(slots=True)
class MarketAgent:
    db: Session

    def run(self, product: Product, competitors: list[dict[str, Any]]) -> MarketAnalysisResult:
        return analyze_market(self.db, product, competitors)