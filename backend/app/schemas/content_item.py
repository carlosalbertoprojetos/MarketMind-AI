from uuid import UUID

from pydantic import AliasChoices, Field

from app.models.enums import ContentType
from app.schemas.common import IDSchema, ORMBase, TenantSchema, TimestampSchema


class ContentItemBase(ORMBase):
    campaign_id: UUID | None = None
    product_id: UUID | None = None
    persona_id: UUID | None = None
    parent_id: UUID | None = None
    content_type: ContentType
    title: str | None = None
    brief: str | None = None
    short_version: str | None = None
    medium_version: str | None = None
    long_version: str | None = None
    technical_version: str | None = None
    sales_version: str | None = None
    meta: dict | None = Field(
        default=None,
        validation_alias=AliasChoices("meta", "metadata"),
        serialization_alias="metadata",
    )


class ContentItemCreate(ContentItemBase):
    pass


class ContentItemUpdate(ORMBase):
    title: str | None = None
    brief: str | None = None
    short_version: str | None = None
    medium_version: str | None = None
    long_version: str | None = None
    technical_version: str | None = None
    sales_version: str | None = None
    meta: dict | None = Field(
        default=None,
        validation_alias=AliasChoices("meta", "metadata"),
        serialization_alias="metadata",
    )


class ContentItemRead(ContentItemBase, TenantSchema, IDSchema, TimestampSchema):
    pass
