from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.models.base import Base
from app.models.enums import ContentType
from app.models.mixins import TenantMixin, TimestampMixin, UUIDMixin


class ContentItem(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "content_items"

    campaign_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("campaigns.id"))
    product_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"))
    persona_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("personas.id"))
    parent_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("content_items.id"))
    content_type: Mapped[ContentType] = mapped_column(Enum(ContentType), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255))
    brief: Mapped[str | None] = mapped_column(Text)

    short_version: Mapped[str | None] = mapped_column(Text)
    medium_version: Mapped[str | None] = mapped_column(Text)
    long_version: Mapped[str | None] = mapped_column(Text)
    technical_version: Mapped[str | None] = mapped_column(Text)
    sales_version: Mapped[str | None] = mapped_column(Text)

    meta: Mapped[dict | None] = mapped_column("metadata", JSONB)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536))

    campaign = relationship("Campaign", back_populates="content_items")
    product = relationship("Product", back_populates="content_items")
    persona = relationship("Persona", back_populates="content_items")
    parent = relationship("ContentItem", remote_side="ContentItem.id")
    posts = relationship("Post", back_populates="content_item")
    media_assets = relationship("MediaAsset", back_populates="content_item")
