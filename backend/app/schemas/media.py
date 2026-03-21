"""Schemas para visualização de mídia gerada por campanha."""
from pydantic import BaseModel


class CampaignAssetItem(BaseModel):
    path: str
    url: str
    kind: str
    platform: str | None = None
    generated_at: str | None = None


class CampaignAssetsResponse(BaseModel):
    campaign_id: int
    source_url: str | None = None
    assets: list[CampaignAssetItem] = []


class CampaignAssetsExportSelectedRequest(BaseModel):
    paths: list[str]
