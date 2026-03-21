"""Schemas para geracao automatizada de marketing a partir de uma URL."""
from pydantic import BaseModel, Field


class PostPreviewResponse(BaseModel):
    platform: str
    title: str
    text: str
    image_paths: list[str] = []
    image_urls: list[str] = []
    hashtags: list[str] = []
    suggested_times: list[str] = []
    steps: list[str] = []
    source_page_url: str = ""
    page_title: str = ""
    screen_type: str = "generic"
    screen_label: str = ""
    strategy_summary: str = ""


class CampaignPreviewRequest(BaseModel):
    url: str
    campaign_title: str
    platforms: list[str] = ["instagram", "facebook", "linkedin"]
    target_platform: str | None = Field(default=None, description="Usar apenas uma rede social por vez")
    objective: str = Field(default="branding", description="branding, engajamento ou conversao")
    max_crawl_pages: int = Field(default=5, ge=1, le=20, description="Paginas internas maximas")
    max_crawl_depth: int = Field(default=2, ge=0, le=5, description="Profundidade maxima de links internos")
    credentials_id: int | None = None
    login_url: str | None = None
    login_username: str | None = None
    login_password: str | None = None


class CampaignPreviewResponse(BaseModel):
    url: str
    posts: list[PostPreviewResponse]
    business_summary: dict = {}
    generated_contents: list[dict] = []
    copy_variations: list[dict] = []
    visual_suggestions: list[dict] = []
    error: str | None = None
