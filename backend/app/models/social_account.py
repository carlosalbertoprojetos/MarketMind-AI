from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import SocialPlatform
from app.models.mixins import TenantMixin, TimestampMixin, UUIDMixin


class SocialAccount(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "social_accounts"

    workspace_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id"))
    platform: Mapped[SocialPlatform] = mapped_column(Enum(SocialPlatform), nullable=False)
    handle: Mapped[str | None] = mapped_column(String(255))
    external_id: Mapped[str | None] = mapped_column(String(255))
    access_token_encrypted: Mapped[str | None] = mapped_column(String(2048))
    refresh_token_encrypted: Mapped[str | None] = mapped_column(String(2048))
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    meta: Mapped[dict | None] = mapped_column("metadata", JSONB)

    posts = relationship("Post", back_populates="social_account")
