"""Schemas para histórico de gerações de campanha."""
from pydantic import BaseModel, Field


class CampaignGenerationItem(BaseModel):
    generated_at: str
    source_url: str
    post_count: int
    asset_count: int
    platforms: list[str] = Field(default_factory=list)


class CampaignGenerationHistoryResponse(BaseModel):
    campaign_id: int
    generations: list[CampaignGenerationItem] = Field(default_factory=list)
