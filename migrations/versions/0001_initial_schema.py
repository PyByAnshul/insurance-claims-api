"""initial schema

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("customer_id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("city", sa.String(), nullable=False),
        sa.Column("state", sa.String(), nullable=False),
    )
    op.create_index("ix_customers_state", "customers", ["state"])
    op.create_index("ix_customers_city", "customers", ["city"])

    op.create_table(
        "policies",
        sa.Column("policy_id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.customer_id"), nullable=False),
        sa.Column("policy_issue_date", sa.Date(), nullable=False),
        sa.Column("coverage_limit", sa.Float(), nullable=False),
        sa.Column("deductible", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(), nullable=False),
    )
    op.create_index("ix_policies_policy_id", "policies", ["policy_id"])

    op.create_table(
        "claims",
        sa.Column("claim_id", sa.Integer(), primary_key=True),
        sa.Column("policy_id", sa.Integer(), sa.ForeignKey("policies.policy_id"), nullable=False),
        sa.Column("loss_date", sa.Date(), nullable=False),
        sa.Column("loss_amount", sa.Float(), nullable=False),
        sa.Column("cause", sa.String(), nullable=False),
        sa.Column("final_payout", sa.Float(), nullable=False),
        sa.Column("fraud_flag", sa.Boolean(), default=False),
    )
    op.create_index("ix_claims_cause", "claims", ["cause"])
    op.create_index("ix_claims_loss_date", "claims", ["loss_date"])


def downgrade() -> None:
    op.drop_table("claims")
    op.drop_table("policies")
    op.drop_table("customers")
