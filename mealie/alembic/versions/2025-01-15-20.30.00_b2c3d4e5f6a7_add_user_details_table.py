"""Add user details table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2025-01-15 20:30:00.000000

"""

import sqlalchemy as sa
from alembic import op

import mealie.db.migration_types

# revision identifiers, used by Alembic.
revision = "b2c3d4e5f6a7"
down_revision: str | None = "a1b2c3d4e5f6"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    # Create user_details table
    op.create_table(
        "user_details",
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("user_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("real_name", sa.String(), nullable=False),
        sa.Column("grade", sa.String(), nullable=True),
        sa.Column("class_name", sa.String(), nullable=True),
        sa.Column("avatar_url", sa.String(), nullable=True),
        sa.Column("is_complete", sa.Boolean(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_user_details_user_id"), "user_details", ["user_id"], unique=True)
    op.create_index(op.f("ix_user_details_real_name"), "user_details", ["real_name"], unique=False)
    op.create_index(op.f("ix_user_details_grade"), "user_details", ["grade"], unique=False)
    op.create_index(op.f("ix_user_details_class_name"), "user_details", ["class_name"], unique=False)
    op.create_index(op.f("ix_user_details_is_complete"), "user_details", ["is_complete"], unique=False)
    op.create_index(op.f("ix_user_details_created_at"), "user_details", ["created_at"], unique=False)
    op.create_foreign_key("fk_details_user", "users", ["user_id"], ["id"])


def downgrade():
    # Drop user_details table
    op.drop_table("user_details")
