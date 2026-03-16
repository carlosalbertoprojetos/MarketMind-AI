from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import ScheduleStatus
from app.models.mixins import TenantMixin, TimestampMixin, UUIDMixin


class Schedule(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "schedules"

    post_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("posts.id"))
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    status: Mapped[ScheduleStatus] = mapped_column(
        Enum(ScheduleStatus), default=ScheduleStatus.scheduled
    )

    post = relationship("Post", back_populates="schedules")
