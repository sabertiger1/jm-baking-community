"""add user experience history table

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-03-03 12:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

import mealie.db.migration_types

# revision identifiers, used by Alembic.
revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    dialect = bind.dialect.name
    tables = set(inspector.get_table_names())

    if "user_experience_history" not in tables:
        op.create_table(
            "user_experience_history",
            sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("update_at", sa.DateTime(), nullable=True),
            sa.Column("user_id", mealie.db.migration_types.GUID(), nullable=False),
            sa.Column("source", sa.String(), nullable=False),
            sa.Column("exp_delta", sa.Integer(), nullable=False),
            sa.Column("total_exp_after", sa.Integer(), nullable=False),
            sa.Column("note", sa.Text(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_user_experience_history_user_id"),
            "user_experience_history",
            ["user_id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_user_experience_history_source"),
            "user_experience_history",
            ["source"],
            unique=False,
        )
        op.create_index(
            op.f("ix_user_experience_history_created_at"),
            "user_experience_history",
            ["created_at"],
            unique=False,
        )
        if dialect != "sqlite":
            op.create_foreign_key(
                "fk_experience_history_user",
                "user_experience_history",
                "users",
                ["user_id"],
                ["id"],
            )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "user_experience_history" in tables:
        op.drop_table("user_experience_history")
