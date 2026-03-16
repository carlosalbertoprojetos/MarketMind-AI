from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class IDSchema(ORMBase):
    id: UUID


class TimestampSchema(ORMBase):
    created_at: datetime
    updated_at: datetime


class TenantSchema(ORMBase):
    organization_id: UUID