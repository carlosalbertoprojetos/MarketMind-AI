from uuid import UUID

from app.schemas.common import IDSchema, ORMBase, TenantSchema, TimestampSchema


class BrandBase(ORMBase):
    workspace_id: UUID
    name: str
    description: str | None = None
    website_url: str | None = None


class BrandCreate(BrandBase):
    pass


class BrandUpdate(ORMBase):
    name: str | None = None
    description: str | None = None
    website_url: str | None = None


class BrandRead(BrandBase, TenantSchema, IDSchema, TimestampSchema):
    pass