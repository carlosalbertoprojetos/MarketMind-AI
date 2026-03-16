from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.models.content_item import ContentItem
from app.models.enums import CampaignStage, ContentType
from app.models.product import Product
from app.models.workspace import Workspace


@dataclass(slots=True)
class CampaignPlanResult:
    campaign: Campaign
    content_items: list[ContentItem]


def plan_campaign(
    db: Session,
    workspace: Workspace,
    product: Product,
    name: str,
    objective: str | None = None,
) -> CampaignPlanResult:
    campaign = Campaign(
        workspace_id=workspace.id,
        product_id=product.id,
        organization_id=workspace.organization_id,
        name=name,
        objective=objective,
        stage=CampaignStage.awareness,
    )
    db.add(campaign)
    db.flush()

    stages = [
        CampaignStage.awareness,
        CampaignStage.education,
        CampaignStage.solution,
        CampaignStage.proof,
        CampaignStage.conversion,
    ]

    items: list[ContentItem] = []
    for stage in stages:
        item = ContentItem(
            campaign_id=campaign.id,
            product_id=product.id,
            organization_id=workspace.organization_id,
            content_type=ContentType.linkedin_post,
            title=f"{stage.value.capitalize()} - {product.name}",
            brief=f"Etapa {stage.value} da campanha {name}.",
            meta={"stage": stage.value},
        )
        db.add(item)
        items.append(item)

    db.commit()
    db.refresh(campaign)
    return CampaignPlanResult(campaign=campaign, content_items=items)
