from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import AiRunStatus
from app.models.mixins import TenantMixin, TimestampMixin, UUIDMixin


class AiRun(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "ai_runs"

    product_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"))
    run_type: Mapped[str] = mapped_column(String(50), nullable=False, default="pipeline")
    status: Mapped[AiRunStatus] = mapped_column(Enum(AiRunStatus), default=AiRunStatus.pending)
    input_payload: Mapped[dict | None] = mapped_column("input", JSONB)
    output_payload: Mapped[dict | None] = mapped_column("output", JSONB)
    error_message: Mapped[str | None] = mapped_column(String(500))

    product = relationship("Product")
