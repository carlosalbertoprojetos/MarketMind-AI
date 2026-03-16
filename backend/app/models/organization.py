from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class Organization(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    plan: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    settings: Mapped[dict | None] = mapped_column(JSONB)

    users = relationship("User", back_populates="organization")
    workspaces = relationship("Workspace", back_populates="organization")