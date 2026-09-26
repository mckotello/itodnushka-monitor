"""create monitors and check results

Revision ID: 0001_create_monitors
Revises:
Create Date: 2026-09-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_create_monitors"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "monitors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("last_status", sa.String(length=20), nullable=True),
        sa.Column("last_status_code", sa.Integer(), nullable=True),
        sa.Column("last_response_time_ms", sa.Integer(), nullable=True),
        sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url"),
    )

    op.create_index(
        "ix_monitors_url",
        "monitors",
        ["url"],
        unique=True,
    )

    op.create_index(
        "ix_monitors_is_active",
        "monitors",
        ["is_active"],
        unique=False,
    )

    op.create_table(
        "check_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("monitor_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("response_time_ms", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "checked_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["monitor_id"],
            ["monitors.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_check_results_monitor_id",
        "check_results",
        ["monitor_id"],
        unique=False,
    )

    op.create_index(
        "ix_check_results_checked_at",
        "check_results",
        ["checked_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_check_results_checked_at",
        table_name="check_results",
    )

    op.drop_index(
        "ix_check_results_monitor_id",
        table_name="check_results",
    )

    op.drop_table("check_results")

    op.drop_index(
        "ix_monitors_is_active",
        table_name="monitors",
    )

    op.drop_index(
        "ix_monitors_url",
        table_name="monitors",
    )

    op.drop_table("monitors")