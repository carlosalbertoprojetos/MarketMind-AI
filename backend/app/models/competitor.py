from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TenantMixin, TimestampMixin, UUIDMixin


class Competitor(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "competitors"

    product_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    website_url: Mapped[str | None] = mapped_column(String(500))
    positioning: Mapped[str | None] = mapped_column(Text)
    marketing_language: Mapped[str | None] = mapped_column(Text)
    differentiators: Mapped[dict | None] = mapped_column(JSONB)
    summary: Mapped[str | None] = mapped_column(Text)

    product = relationship("Product", back_populates="competitors")