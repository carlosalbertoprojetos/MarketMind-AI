from datetime import datetime

from app.schemas.common import IDSchema, ORMBase, TenantSchema, TimestampSchema


class IntegrationBase(ORMBase):
    provider: str
    status: str = "active"
    config: dict | None = None
    last_synced_at: datetime | None = None


class IntegrationCreate(IntegrationBase):
    pass


class IntegrationUpdate(ORMBase):
    status: str | None = None
    config: dict | None = None
    last_synced_at: datetime | None = None


class IntegrationRead(IntegrationBase, TenantSchema, IDSchema, TimestampSchema):
    pass