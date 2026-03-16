from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins import TenantMixin, TimestampMixin, UUIDMixin


class Integration(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "integrations"

    provider: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    config: Mapped[dict | None] = mapped_column(JSONB)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
