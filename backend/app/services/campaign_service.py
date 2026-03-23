"""
Serviço de campanhas: criar, listar por usuário, obter por id.
"""
from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.schemas.campaign import CampaignCreate, CampaignUpdate

SUPPORTED_CAMPAIGNS_PLATFORMS = ("instagram", "facebook", "linkedin", "twitter", "tiktok", "youtube")


def normalize_campaign_platform(value: str | None) -> str | None:
    normalized = str(value or "").strip().lower()
    if not normalized:
        return None
    if normalized == "x":
        normalized = "twitter"
    return normalized if normalized in SUPPORTED_CAMPAIGNS_PLATFORMS else None


def extract_platforms_from_campaign_content(content: str | None) -> list[str]:
    import re

    if not content:
        return []
    block = re.search(r"(?:^|\n)PLATFORMS:\s*\n([\s\S]*?)\nEND_PLATFORMS(?:\n|$)", str(content), re.IGNORECASE)
    if not block:
        return []

    platforms: list[str] = []
    seen: set[str] = set()
    for line in block.group(1).splitlines():
        candidate = normalize_campaign_platform(line)
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        platforms.append(candidate)
    return platforms


def get_campaign_platforms(campaign: Campaign) -> list[str]:
    extracted = extract_platforms_from_campaign_content(campaign.content)
    if extracted:
        return extracted
    fallback = normalize_campaign_platform(campaign.platform)
    return [fallback] if fallback else []


def parse_platform_filters(platform: str | None = None, platforms: str | list[str] | None = None) -> list[str]:
    requested: list[str] = []
    seen: set[str] = set()

    raw_values: list[str] = []
    if isinstance(platforms, str) and platforms.strip():
        raw_values.extend(part.strip() for part in platforms.split(","))
    elif isinstance(platforms, list):
        raw_values.extend(platforms)
    if platform and str(platform).strip():
        raw_values.append(str(platform).strip())

    for value in raw_values:
        normalized = normalize_campaign_platform(value)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        requested.append(normalized)
    return requested


def get_campaigns_by_user(db: Session, user_id: int):
    """Lista todas as campanhas do usuário."""
    return db.query(Campaign).filter(Campaign.user_id == user_id).order_by(Campaign.created_at.desc()).all()


def get_campaigns_by_user_paginated(
    db: Session,
    user_id: int,
    limit: int = 20,
    offset: int = 0,
    platform: str | None = None,
    platforms: str | list[str] | None = None,
    search: str | None = None,
    sort: str = "created_at_desc",
) -> tuple[list[Campaign], int]:
    """Lista campanhas do usuário com paginação e filtros. Retorna (lista da página, total).
    sort: created_at_desc | created_at_asc | schedule_desc | schedule_asc
    """
    q = db.query(Campaign).filter(Campaign.user_id == user_id)
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

    items = q.all()
    requested_platforms = parse_platform_filters(platform=platform, platforms=platforms)
    if requested_platforms:
        items = [
            campaign for campaign in items
            if set(get_campaign_platforms(campaign)).intersection(requested_platforms)
        ]

    total = len(items)
    return items[offset: offset + limit], total


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
