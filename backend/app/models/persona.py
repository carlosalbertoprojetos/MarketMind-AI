from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TenantMixin, TimestampMixin, UUIDMixin


class Persona(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "personas"

    product_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    profile: Mapped[str | None] = mapped_column(Text)
    problems: Mapped[str | None] = mapped_column(Text)
    goals: Mapped[str | None] = mapped_column(Text)
    communication_style: Mapped[str | None] = mapped_column(Text)

    product = relationship("Product", back_populates="personas")
    content_items = relationship("ContentItem", back_populates="persona")