from datetime import date
from uuid import UUID

from app.models.enums import CampaignStage, CampaignStatus
from app.schemas.common import IDSchema, ORMBase, TenantSchema, TimestampSchema


class CampaignBase(ORMBase):
    workspace_id: UUID
    product_id: UUID
    name: str
    objective: str | None = None
    stage: CampaignStage
    status: CampaignStatus = CampaignStatus.draft
    start_date: date | None = None
    end_date: date | None = None


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(ORMBase):
    name: str | None = None
    objective: str | None = None
    stage: CampaignStage | None = None
    status: CampaignStatus | None = None
    start_date: date | None = None
    end_date: date | None = None


class CampaignRead(CampaignBase, TenantSchema, IDSchema, TimestampSchema):
    pass