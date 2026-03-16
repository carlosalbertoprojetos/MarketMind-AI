from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import MediaType
from app.models.mixins import TenantMixin, TimestampMixin, UUIDMixin


class MediaAsset(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "media_assets"

    content_item_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("content_items.id")
    )
    asset_type: Mapped[MediaType] = mapped_column(Enum(MediaType), nullable=False)
    url: Mapped[str | None] = mapped_column(String(500))
    storage_key: Mapped[str | None] = mapped_column(String(500))
    meta: Mapped[dict | None] = mapped_column("metadata", JSONB)

    content_item = relationship("ContentItem", back_populates="media_assets")
