from uuid import UUID

from app.models.enums import SocialPlatform
from app.schemas.common import IDSchema, ORMBase, TenantSchema, TimestampSchema


class SocialAccountBase(ORMBase):
    workspace_id: UUID
    platform: SocialPlatform
    handle: str | None = None
    external_id: str | None = None
    status: str = "active"
    metadata: dict | None = None


class SocialAccountCreate(SocialAccountBase):
    access_token: str | None = None
    refresh_token: str | None = None


class SocialAccountUpdate(ORMBase):
    handle: str | None = None
    status: str | None = None
    metadata: dict | None = None


class SocialAccountRead(SocialAccountBase, TenantSchema, IDSchema, TimestampSchema):
    pass