from uuid import UUID

from app.schemas.common import IDSchema, ORMBase, TenantSchema, TimestampSchema


class CompetitorBase(ORMBase):
    product_id: UUID
    name: str
    website_url: str | None = None
    positioning: str | None = None
    marketing_language: str | None = None
    differentiators: dict | None = None
    summary: str | None = None


class CompetitorCreate(CompetitorBase):
    pass


class CompetitorUpdate(ORMBase):
    name: str | None = None
    website_url: str | None = None
    positioning: str | None = None
    marketing_language: str | None = None
    differentiators: dict | None = None
    summary: str | None = None


class CompetitorRead(CompetitorBase, TenantSchema, IDSchema, TimestampSchema):
    pass