"""
Rotas do usuário: listar campanhas e resumo do dashboard.
"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.utils.deps import get_current_user
from app.schemas.campaign import CampaignResponse, CampaignListResponse
from app.schemas.summary import UserSummaryResponse
from app.services.campaign_service import (
    get_campaign_platforms,
    get_campaigns_by_user,
    get_campaigns_by_user_paginated,
)

router = APIRouter(prefix="/user", tags=["user"])


def _serialize_campaign(campaign) -> CampaignResponse:
    return CampaignResponse.model_validate(
        {
            "id": campaign.id,
            "user_id": campaign.user_id,
            "title": campaign.title,
            "content": campaign.content,
            "platform": campaign.platform,
            "platforms": get_campaign_platforms(campaign),
            "schedule": campaign.schedule,
            "reminder_sent_at": campaign.reminder_sent_at,
            "created_at": campaign.created_at,
            "updated_at": campaign.updated_at,
        }
    )


@router.get("/summary", response_model=UserSummaryResponse)
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Resumo para o dashboard: total de campanhas, por plataforma e próximas 24h."""
    campaigns = get_campaigns_by_user(db, current_user.id)
    by_platform: dict[str, int] = {}
    for campaign in campaigns:
        platforms = get_campaign_platforms(campaign)
        if not platforms:
            by_platform["sem_plataforma"] = by_platform.get("sem_plataforma", 0) + 1
            continue
        for item in platforms:
            by_platform[item] = by_platform.get(item, 0) + 1
    now = datetime.utcnow()
    end = now + timedelta(hours=24)
    upcoming = sum(
        1
        for campaign in campaigns
        if campaign.schedule and now <= campaign.schedule <= end
    )
    return UserSummaryResponse(
        total_campaigns=len(campaigns),
        by_platform=by_platform,
        upcoming_count=upcoming,
    )


@router.get("/campaigns", response_model=CampaignListResponse)
def list_my_campaigns(
    limit: int = 50,
    offset: int = 0,
    platform: str | None = None,
    platforms: str | None = None,
    search: str | None = None,
    sort: str = "created_at_desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista campanhas do usuário com paginação e filtros."""
    limit = min(max(1, limit), 100)
    offset = max(0, offset)
    if sort not in ("created_at_desc", "created_at_asc", "schedule_desc", "schedule_asc"):
        sort = "created_at_desc"
    items, total = get_campaigns_by_user_paginated(
        db,
        current_user.id,
        limit=limit,
        offset=offset,
        platform=platform,
        platforms=platforms,
        search=search,
        sort=sort,
    )
    return CampaignListResponse(items=[_serialize_campaign(item) for item in items], total=total, limit=limit, offset=offset)
