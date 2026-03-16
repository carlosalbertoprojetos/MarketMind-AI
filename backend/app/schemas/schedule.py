from datetime import datetime
from uuid import UUID

from app.models.enums import ScheduleStatus
from app.schemas.common import IDSchema, ORMBase, TenantSchema, TimestampSchema


class ScheduleBase(ORMBase):
    post_id: UUID
    scheduled_at: datetime
    timezone: str = "UTC"
    status: ScheduleStatus = ScheduleStatus.scheduled


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleUpdate(ORMBase):
    scheduled_at: datetime | None = None
    timezone: str | None = None
    status: ScheduleStatus | None = None


class ScheduleRead(ScheduleBase, TenantSchema, IDSchema, TimestampSchema):
    pass