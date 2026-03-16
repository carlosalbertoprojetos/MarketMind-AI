from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import AnalyticsEventType
from app.models.mixins import TenantMixin, TimestampMixin, UUIDMixin


class AnalyticsEvent(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "analytics_events"

    post_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("posts.id"))
    event_type: Mapped[AnalyticsEventType] = mapped_column(Enum(AnalyticsEventType))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    metadata: Mapped[dict | None] = mapped_column(JSONB)

    post = relationship("Post", back_populates="analytics_events")
