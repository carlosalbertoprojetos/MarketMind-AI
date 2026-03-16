from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TenantMixin, TimestampMixin, UUIDMixin


class Workspace(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    organization = relationship("Organization", back_populates="workspaces")
    memberships = relationship("Membership", back_populates="workspace")
    brands = relationship("Brand", back_populates="workspace")