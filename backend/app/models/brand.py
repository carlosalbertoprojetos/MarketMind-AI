from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TenantMixin, TimestampMixin, UUIDMixin


class Brand(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "brands"

    workspace_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    website_url: Mapped[str | None] = mapped_column(String(500))

    workspace = relationship("Workspace", back_populates="brands")
    products = relationship("Product", back_populates="brand")