from app.schemas.common import IDSchema, ORMBase, TenantSchema, TimestampSchema


class WorkspaceBase(ORMBase):
    name: str
    slug: str
    description: str | None = None


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceUpdate(ORMBase):
    name: str | None = None
    slug: str | None = None
    description: str | None = None


class WorkspaceRead(WorkspaceBase, TenantSchema, IDSchema, TimestampSchema):
    pass