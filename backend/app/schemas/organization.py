from app.schemas.common import IDSchema, ORMBase, TimestampSchema


class OrganizationBase(ORMBase):
    name: str
    slug: str
    plan: str | None = None
    status: str = "active"
    settings: dict | None = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(ORMBase):
    name: str | None = None
    slug: str | None = None
    plan: str | None = None
    status: str | None = None
    settings: dict | None = None


class OrganizationRead(OrganizationBase, IDSchema, TimestampSchema):
    pass