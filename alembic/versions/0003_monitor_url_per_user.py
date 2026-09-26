"""make monitor url unique per user

Revision ID: 0003_monitor_url_per_user
Revises: 0002_users_and_monitor_owner
Create Date: 2026-09-26
"""

from alembic import op


revision = "0003_monitor_url_per_user"
down_revision = "0002_users_and_monitor_owner"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint(
        "monitors_url_key",
        "monitors",
        type_="unique",
    )

    op.create_index(
        "ix_monitors_user_id_url",
        "monitors",
        ["user_id", "url"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_monitors_user_id_url",
        table_name="monitors",
    )

    op.create_unique_constraint(
        "monitors_url_key",
        "monitors",
        ["url"],
    )