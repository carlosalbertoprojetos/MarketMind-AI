from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.campaign import Campaign
from app.schemas.campaign import CampaignCreate, CampaignRead, CampaignUpdate
from app.services.validators import get_product_or_404, get_workspace_or_404
from app.utils.db import apply_updates, get_object_or_404

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("/", response_model=list[CampaignRead])
def list_campaigns(
    db: Session = Depends(get_db), current_user=Depends(get_current_active_user)
) -> list[Campaign]:
    return (
        db.query(Campaign)
        .filter(Campaign.organization_id == current_user.organization_id)
        .all()
    )


@router.post("/", response_model=CampaignRead, status_code=status.HTTP_201_CREATED)
def create_campaign(
    payload: CampaignCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Campaign:
    get_workspace_or_404(db, payload.workspace_id, current_user.organization_id)
    get_product_or_404(db, payload.product_id, current_user.organization_id)
    campaign = Campaign(
        **payload.model_dump(), organization_id=current_user.organization_id
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


@router.get("/{campaign_id}", response_model=CampaignRead)
def read_campaign(
    campaign_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Campaign:
    return get_object_or_404(db, Campaign, campaign_id, current_user.organization_id)


@router.patch("/{campaign_id}", response_model=CampaignRead)
def update_campaign(
    campaign_id: str,
    payload: CampaignUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Campaign:
    campaign = get_object_or_404(db, Campaign, campaign_id, current_user.organization_id)
    apply_updates(campaign, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(campaign)
    return campaign


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign(
    campaign_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> None:
    campaign = get_object_or_404(db, Campaign, campaign_id, current_user.organization_id)
    db.delete(campaign)
    db.commit()
    return None