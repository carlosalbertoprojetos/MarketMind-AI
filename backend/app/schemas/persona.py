from uuid import UUID

from app.schemas.common import IDSchema, ORMBase, TenantSchema, TimestampSchema


class PersonaBase(ORMBase):
    product_id: UUID
    name: str
    profile: str | None = None
    problems: str | None = None
    goals: str | None = None
    communication_style: str | None = None


class PersonaCreate(PersonaBase):
    pass


class PersonaUpdate(ORMBase):
    name: str | None = None
    profile: str | None = None
    problems: str | None = None
    goals: str | None = None
    communication_style: str | None = None


class PersonaRead(PersonaBase, TenantSchema, IDSchema, TimestampSchema):
    pass