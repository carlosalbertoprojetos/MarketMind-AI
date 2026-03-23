"""Schemas do pipeline final de conteudo."""
from datetime import datetime

from pydantic import BaseModel, Field


class FinalContentPipelineRequest(BaseModel):
    theme: str
    objective: str = Field(default='branding', description='branding, engajamento ou conversao')
    audience: str
    platforms: list[str] = Field(default_factory=lambda: ['instagram', 'tiktok', 'linkedin', 'x', 'youtube', 'facebook'])
    style: str = Field(default='modern', description='Estilo visual para prompts de imagem')


class FinalPlatformContentResponse(BaseModel):
    platform: str
    objective: str
    audience: str
    content_format: str
    full_content: str
    hooks: list[str] = []
    narrative_structure: dict = {}
    cta_options: list[str] = []
    ab_variations: list[dict] = []
    hashtags: list[str] = []
    structured_output: dict = {}
    image_prompt: str = ''
    visual_decision: dict = {}


class FinalABTestSuggestionResponse(BaseModel):
    platform: str
    hypothesis: str
    variant_a: str
    variant_b: str
    success_metric: str


class FinalContentPipelineResponse(BaseModel):
    theme: str
    objective: str
    audience: str
    outputs: list[FinalPlatformContentResponse] = []
    ab_test_suggestions: list[FinalABTestSuggestionResponse] = []
    saved_content_id: int | None = None
    saved_at: datetime | None = None


class FinalContentPublishResponse(BaseModel):
    theme: str
    objective: str
    audience: str
    outputs: list[FinalPlatformContentResponse] = []
    ab_test_suggestions: list[FinalABTestSuggestionResponse] = []
    publish_results: list[dict] = []
    saved_content_id: int | None = None
    saved_at: datetime | None = None


class SavedFinalContentItemResponse(BaseModel):
    id: int
    title: str | None = None
    theme: str | None = None
    objective: str | None = None
    audience: str | None = None
    style: str | None = None
    platforms: list[str] = []
    post_count: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SavedFinalContentListResponse(BaseModel):
    items: list[SavedFinalContentItemResponse] = []
    total: int = 0
    limit: int = 0
    offset: int = 0


class SavedFinalContentResponse(FinalContentPublishResponse):
    id: int
    source_type: str = 'final_content'
    title: str | None = None
    style: str | None = None
    platforms: list[str] = []
    publish_results: list[dict] = []
    updated_at: datetime | None = None
