from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import MembershipStatus, Role
from app.models.mixins import TenantMixin, TimestampMixin, UUIDMixin


class Membership(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "memberships"
    __table_args__ = (
        UniqueConstraint("user_id", "workspace_id", name="uq_membership_user_workspace"),
    )

    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    workspace_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False
    )
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.viewer, nullable=False)
    status: Mapped[MembershipStatus] = mapped_column(
        Enum(MembershipStatus), default=MembershipStatus.active, nullable=False
    )

    user = relationship("User", back_populates="memberships")
    workspace = relationship("Workspace", back_populates="memberships")
    organization = relationship("Organization")