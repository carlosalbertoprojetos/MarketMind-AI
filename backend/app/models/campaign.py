from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import CampaignStage, CampaignStatus
from app.models.mixins import TenantMixin, TimestampMixin, UUIDMixin


class Campaign(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "campaigns"

    workspace_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id"))
    product_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    objective: Mapped[str | None] = mapped_column(Text)
    stage: Mapped[CampaignStage] = mapped_column(Enum(CampaignStage), nullable=False)
    status: Mapped[CampaignStatus] = mapped_column(
        Enum(CampaignStatus), default=CampaignStatus.draft, nullable=False
    )
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)

    product = relationship("Product", back_populates="campaigns")
    content_items = relationship("ContentItem", back_populates="campaign")
