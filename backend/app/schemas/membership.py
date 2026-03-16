from uuid import UUID

from app.models.enums import MembershipStatus, Role
from app.schemas.common import IDSchema, ORMBase, TenantSchema, TimestampSchema


class MembershipBase(ORMBase):
    user_id: UUID
    workspace_id: UUID
    role: Role = Role.viewer
    status: MembershipStatus = MembershipStatus.active


class MembershipCreate(MembershipBase):
    pass


class MembershipUpdate(ORMBase):
    role: Role | None = None
    status: MembershipStatus | None = None


class MembershipRead(MembershipBase, TenantSchema, IDSchema, TimestampSchema):
    pass