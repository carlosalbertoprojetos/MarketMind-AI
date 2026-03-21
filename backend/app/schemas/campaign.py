"""
Schemas de campanha: criação, listagem, resposta.
"""
from datetime import datetime
from pydantic import BaseModel


class CampaignCreate(BaseModel):
    title: str
    content: str | None = None
    platform: str | None = None
    schedule: datetime | None = None


class CampaignUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    platform: str | None = None
    schedule: datetime | None = None


class CampaignResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str | None = None
    platform: str | None = None
    schedule: datetime | None = None
    reminder_sent_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class CampaignListResponse(BaseModel):
    """Resposta paginada de listagem de campanhas."""
    items: list[CampaignResponse]
    total: int
    limit: int
    offset: int
