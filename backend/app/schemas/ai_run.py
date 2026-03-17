from datetime import datetime
from uuid import UUID

from app.models.enums import AiRunStatus
from app.schemas.common import IDSchema, ORMBase, TenantSchema, TimestampSchema


class AiRunBase(ORMBase):
    product_id: UUID
    run_type: str = "pipeline"
    status: AiRunStatus = AiRunStatus.pending
    input_payload: dict | None = None
    output_payload: dict | None = None
    error_message: str | None = None


class AiRunRead(AiRunBase, TenantSchema, IDSchema, TimestampSchema):
    pass


class PipelineRunRequest(ORMBase):
    product_id: UUID
    sources: list[str] = []
    content_types: list[str] | None = None
    persona_count: int = 3
    brief: str | None = None


class PipelineRunResponse(ORMBase):
    run_id: UUID
    status: AiRunStatus
    content_item_ids: list[UUID]
    steps: dict
    output: dict | None = None
