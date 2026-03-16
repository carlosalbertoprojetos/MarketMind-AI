from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import PostStatus, SocialPlatform
from app.models.mixins import TenantMixin, TimestampMixin, UUIDMixin


class Post(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "posts"

    content_item_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("content_items.id"))
    social_account_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("social_accounts.id")
    )
    platform: Mapped[SocialPlatform] = mapped_column(Enum(SocialPlatform), nullable=False)
    status: Mapped[PostStatus] = mapped_column(Enum(PostStatus), default=PostStatus.draft)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    external_id: Mapped[str | None] = mapped_column(String(255))
    url: Mapped[str | None] = mapped_column(String(500))

    content_item = relationship("ContentItem", back_populates="posts")
    social_account = relationship("SocialAccount", back_populates="posts")
    schedules = relationship("Schedule", back_populates="post")
    analytics_events = relationship("AnalyticsEvent", back_populates="post")
