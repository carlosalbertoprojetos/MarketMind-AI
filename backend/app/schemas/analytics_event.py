from datetime import datetime
from uuid import UUID

from app.models.enums import AnalyticsEventType
from app.schemas.common import IDSchema, ORMBase, TenantSchema, TimestampSchema


class AnalyticsEventBase(ORMBase):
    post_id: UUID | None = None
    event_type: AnalyticsEventType
    occurred_at: datetime
    metadata: dict | None = None


class AnalyticsEventCreate(AnalyticsEventBase):
    pass


class AnalyticsEventRead(AnalyticsEventBase, TenantSchema, IDSchema, TimestampSchema):
    pass