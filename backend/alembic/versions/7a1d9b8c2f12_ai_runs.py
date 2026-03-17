"""Add ai_runs table

Revision ID: 7a1d9b8c2f12
Revises: 4f2c6b8b9c2a
Create Date: 2026-03-17 01:10:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "7a1d9b8c2f12"
down_revision = "4f2c6b8b9c2a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.Enum("pending", "running", "completed", "failed", name="airunstatus"), nullable=False),
        sa.Column("input", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("output", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_runs_organization_id", "ai_runs", ["organization_id"])
    op.create_index("ix_ai_runs_product_id", "ai_runs", ["product_id"])


def downgrade() -> None:
    op.drop_index("ix_ai_runs_product_id", table_name="ai_runs")
    op.drop_index("ix_ai_runs_organization_id", table_name="ai_runs")
    op.drop_table("ai_runs")
    op.execute("DROP TYPE IF EXISTS airunstatus")
