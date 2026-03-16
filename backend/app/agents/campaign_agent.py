from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.workspace import Workspace
from app.services.campaign_engine import CampaignPlanResult, plan_campaign


@dataclass(slots=True)
class CampaignAgent:
    db: Session

    def run(
        self, workspace: Workspace, product: Product, name: str, objective: str | None = None
    ) -> CampaignPlanResult:
        return plan_campaign(self.db, workspace, product, name, objective)