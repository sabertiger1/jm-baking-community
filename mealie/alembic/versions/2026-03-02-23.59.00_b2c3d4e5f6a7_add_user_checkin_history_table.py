"""add user checkin history table

Revision ID: b2c3d4e5f6a7
Revises: a7e8f9a0b1c2
Create Date: 2026-03-02 23:59:00.000000
"""

import sqlalchemy as sa
from alembic import op

import mealie.db.migration_types

# revision identifiers, used by Alembic.
revision = "b2c3d4e5f6a7"
down_revision = "a7e8f9a0b1c2"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    dialect = bind.dialect.name
    tables = set(inspector.get_table_names())

    if "user_checkin_history" not in tables:
        op.create_table(
            "user_checkin_history",
            sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("update_at", sa.DateTime(), nullable=True),
            sa.Column("user_id", mealie.db.migration_types.GUID(), nullable=False),
            sa.Column("checkin_date", sa.String(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id", "checkin_date", name="user_checkin_date_unique"),
        )
        op.create_index(op.f("ix_user_checkin_history_user_id"), "user_checkin_history", ["user_id"], unique=False)
        op.create_index(
            op.f("ix_user_checkin_history_checkin_date"),
            "user_checkin_history",
            ["checkin_date"],
            unique=False,
        )
        op.create_index(op.f("ix_user_checkin_history_created_at"), "user_checkin_history", ["created_at"], unique=False)
        if dialect != "sqlite":
            op.create_foreign_key("fk_checkin_history_user", "user_checkin_history", "users", ["user_id"], ["id"])


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "user_checkin_history" in tables:
        op.drop_table("user_checkin_history")
