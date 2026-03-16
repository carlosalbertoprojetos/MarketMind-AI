from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.models.enums import AnalyticsEventType
from app.schemas.common import IDSchema, ORMBase, TenantSchema, TimestampSchema


class AnalyticsEventBase(ORMBase):
    post_id: UUID | None = None
    event_type: AnalyticsEventType
    occurred_at: datetime
    meta: dict | None = Field(default=None, validation_alias="metadata", serialization_alias="metadata")


class AnalyticsEventCreate(AnalyticsEventBase):
    pass


class AnalyticsEventRead(AnalyticsEventBase, TenantSchema, IDSchema, TimestampSchema):
    pass
