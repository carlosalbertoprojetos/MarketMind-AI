from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.models.base import Base
from app.models.mixins import TenantMixin, TimestampMixin, UUIDMixin


class Product(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "products"

    brand_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("brands.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    website_url: Mapped[str | None] = mapped_column(String(500))
    landing_page_url: Mapped[str | None] = mapped_column(String(500))
    docs_url: Mapped[str | None] = mapped_column(String(500))
    pricing_url: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    extracted_data: Mapped[dict | None] = mapped_column(JSONB)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536))

    brand = relationship("Brand", back_populates="products")
    competitors = relationship("Competitor", back_populates="product")
    personas = relationship("Persona", back_populates="product")
    campaigns = relationship("Campaign", back_populates="product")
    content_items = relationship("ContentItem", back_populates="product")