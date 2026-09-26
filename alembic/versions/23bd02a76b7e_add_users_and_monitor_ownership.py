"""add users and monitor ownership

Revision ID: 0002_users_and_monitor_owner
Revises: 0001_create_monitors
Create Date: 2026-09-26
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_users_and_monitor_owner"
down_revision = "0001_create_monitors"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),
        sa.Column(
            "email",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "hashed_password",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_users_email",
        "users",
        ["email"],
        unique=True,
    )

    op.add_column(
        "monitors",
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_monitors_user_id",
        "monitors",
        ["user_id"],
    )

    op.create_foreign_key(
        "fk_monitors_user_id_users",
        "monitors",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_monitors_user_id_users",
        "monitors",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_monitors_user_id",
        table_name="monitors",
    )

    op.drop_column(
        "monitors",
        "user_id",
    )

    op.drop_index(
        "ix_users_email",
        table_name="users",
    )

    op.drop_table("users")