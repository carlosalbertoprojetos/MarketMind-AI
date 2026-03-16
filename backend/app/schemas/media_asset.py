from uuid import UUID

from app.models.enums import MediaType
from app.schemas.common import IDSchema, ORMBase, TenantSchema, TimestampSchema


class MediaAssetBase(ORMBase):
    content_item_id: UUID | None = None
    asset_type: MediaType
    url: str | None = None
    storage_key: str | None = None
    metadata: dict | None = None


class MediaAssetCreate(MediaAssetBase):
    pass


class MediaAssetUpdate(ORMBase):
    url: str | None = None
    storage_key: str | None = None
    metadata: dict | None = None


class MediaAssetRead(MediaAssetBase, TenantSchema, IDSchema, TimestampSchema):
    pass