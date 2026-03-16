from uuid import UUID

from app.schemas.common import IDSchema, ORMBase, TenantSchema, TimestampSchema


class ProductBase(ORMBase):
    brand_id: UUID
    name: str
    description: str | None = None
    website_url: str | None = None
    landing_page_url: str | None = None
    docs_url: str | None = None
    pricing_url: str | None = None
    status: str = "active"
    extracted_data: dict | None = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ORMBase):
    name: str | None = None
    description: str | None = None
    website_url: str | None = None
    landing_page_url: str | None = None
    docs_url: str | None = None
    pricing_url: str | None = None
    status: str | None = None
    extracted_data: dict | None = None


class ProductRead(ProductBase, TenantSchema, IDSchema, TimestampSchema):
    pass