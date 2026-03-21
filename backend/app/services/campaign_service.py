"""
Serviço de campanhas: criar, listar por usuário, obter por id.
"""
from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.schemas.campaign import CampaignCreate, CampaignUpdate


def get_campaigns_by_user(db: Session, user_id: int):
    """Lista todas as campanhas do usuário."""
    return db.query(Campaign).filter(Campaign.user_id == user_id).order_by(Campaign.created_at.desc()).all()


def get_campaigns_by_user_paginated(
    db: Session,
    user_id: int,
    limit: int = 20,
    offset: int = 0,
    platform: str | None = None,
    search: str | None = None,
    sort: str = "created_at_desc",
) -> tuple[list[Campaign], int]:
    """Lista campanhas do usuário com paginação e filtros. Retorna (lista da página, total).
    sort: created_at_desc | created_at_asc | schedule_desc | schedule_asc
    """
    q = db.query(Campaign).filter(Campaign.user_id == user_id)
    if platform and platform.strip():
        q = q.filter(Campaign.platform.ilike(platform.strip()))
    if search and search.strip():
        q = q.filter(Campaign.title.ilike(f"%{search.strip()}%"))
    if sort == "created_at_asc":
        q = q.order_by(Campaign.created_at.asc())
    elif sort == "schedule_desc":
        q = q.order_by(Campaign.schedule.desc(), Campaign.created_at.desc())
    elif sort == "schedule_asc":
        q = q.order_by(Campaign.schedule.asc(), Campaign.created_at.desc())
    else:
        q = q.order_by(Campaign.created_at.desc())
    total = q.count()
    items = q.limit(limit).offset(offset).all()
    return items, total


def get_campaign_by_id(db: Session, campaign_id: int, user_id: int) -> Campaign | None:
    """Retorna campanha por id se pertencer ao usuário."""
    return db.query(Campaign).filter(Campaign.id == campaign_id, Campaign.user_id == user_id).first()


def create_campaign(db: Session, user_id: int, data: CampaignCreate) -> Campaign:
    """Cria nova campanha para o usuário."""
    campaign = Campaign(
        user_id=user_id,
        title=data.title,
        content=data.content,
        platform=data.platform,
        schedule=data.schedule,
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


def update_campaign(db: Session, campaign: Campaign, data: CampaignUpdate) -> Campaign:
    """Atualiza campanha com os campos informados."""
    if data.title is not None:
        campaign.title = data.title
    if data.content is not None:
        campaign.content = data.content
    if data.platform is not None:
        campaign.platform = data.platform
    if data.schedule is not None:
        campaign.schedule = data.schedule
    db.commit()
    db.refresh(campaign)
    return campaign


def delete_campaign(db: Session, campaign: Campaign) -> None:
    """Remove campanha."""
    db.delete(campaign)
    db.commit()
