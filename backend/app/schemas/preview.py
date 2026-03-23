"""Schemas para geracao automatizada de marketing a partir de uma URL."""
from datetime import datetime

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
    content_format: str = ""
    primary_cta: str = ""
    platform_rules: dict = {}
    structured_output: dict = {}
    hooks: list[str] = []
    narrative_structure: dict = {}
    cta_options: list[str] = []
    ab_variations: list[dict] = []
    visual_decision: dict = {}


class CampaignPreviewRequest(BaseModel):
    url: str
    campaign_title: str
    platforms: list[str] = ["instagram", "facebook", "linkedin", "youtube"]
    target_platform: str | None = Field(default=None, description="Usar apenas uma rede social por vez")
    objective: str = Field(default="branding", description="branding, engajamento ou conversao")
    source_urls: list[str] = Field(default_factory=list, description="URLs adicionais explicitas para coleta, uma por tela")
    follow_internal_links: bool = Field(default=False, description="Desativado por padrao. So habilite se quiser navegar por links do site")
    capture_scroll_sections: bool = Field(default=True, description="Captura secoes da mesma pagina para landing pages longas")
    max_crawl_pages: int = Field(default=5, ge=1, le=20, description="Numero maximo de URLs explicitas a coletar")
    max_crawl_depth: int = Field(default=0, ge=0, le=5, description="Profundidade de links internos quando follow_internal_links=true")
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
    saved_content_id: int | None = None
    saved_at: datetime | None = None
