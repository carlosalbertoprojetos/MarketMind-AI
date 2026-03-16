from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel

from app.models.enums import ContentType


class ProductAnalysisRequest(BaseModel):
    product_id: UUID
    sources: list[str]


class ProductAnalysisResponse(BaseModel):
    product_id: UUID
    extracted_data: dict


class MarketAnalysisRequest(BaseModel):
    product_id: UUID
    competitors: list[dict]


class MarketAnalysisResponse(BaseModel):
    product_id: UUID
    competitive_map: dict


class AudienceRequest(BaseModel):
    product_id: UUID
    count: int = 3


class NarrativeRequest(BaseModel):
    product_id: UUID
    persona_id: UUID | None = None


class NarrativeResponse(BaseModel):
    problem: str
    diagnosis: str
    solution: str
    demonstration: str
    social_proof: str
    cta: str
    angles: list[str]


class ContentGenerationRequest(BaseModel):
    product_id: UUID
    persona_id: UUID | None = None
    content_type: ContentType
    brief: str | None = None


class CampaignPlanRequest(BaseModel):
    workspace_id: UUID
    product_id: UUID
    name: str
    objective: str | None = None


class CampaignPlanResponse(BaseModel):
    campaign_id: UUID
    content_item_ids: list[UUID]


class AnalyticsSummaryResponse(BaseModel):
    engagement_rate: float
    ctr: float
    growth: float