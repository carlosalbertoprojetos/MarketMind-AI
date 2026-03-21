"""Schemas para histórico de gerações de campanha."""
from pydantic import BaseModel


class CampaignGenerationItem(BaseModel):
    generated_at: str
    source_url: str
    post_count: int
    asset_count: int


class CampaignGenerationHistoryResponse(BaseModel):
    campaign_id: int
    generations: list[CampaignGenerationItem] = []
