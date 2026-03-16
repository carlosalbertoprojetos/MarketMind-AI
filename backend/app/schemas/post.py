from datetime import datetime
from uuid import UUID

from app.models.enums import PostStatus, SocialPlatform
from app.schemas.common import IDSchema, ORMBase, TenantSchema, TimestampSchema


class PostBase(ORMBase):
    content_item_id: UUID
    social_account_id: UUID | None = None
    platform: SocialPlatform
    status: PostStatus = PostStatus.draft
    scheduled_at: datetime | None = None
    published_at: datetime | None = None
    external_id: str | None = None
    url: str | None = None


class PostCreate(PostBase):
    pass


class PostUpdate(ORMBase):
    status: PostStatus | None = None
    scheduled_at: datetime | None = None
    published_at: datetime | None = None
    external_id: str | None = None
    url: str | None = None


class PostRead(PostBase, TenantSchema, IDSchema, TimestampSchema):
    pass