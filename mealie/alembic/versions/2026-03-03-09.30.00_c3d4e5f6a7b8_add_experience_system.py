"""add experience system

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-03-03 09:30:00.000000
"""

import sqlalchemy as sa
from alembic import op

import mealie.db.migration_types

# revision identifiers, used by Alembic.
revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    dialect = bind.dialect.name
    tables = set(inspector.get_table_names())

    if "user_experience" not in tables:
        op.create_table(
            "user_experience",
            sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("update_at", sa.DateTime(), nullable=True),
            sa.Column("user_id", mealie.db.migration_types.GUID(), nullable=False),
            sa.Column("total_exp", sa.Integer(), nullable=False, server_default="0"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id"),
        )
        op.create_index(op.f("ix_user_experience_user_id"), "user_experience", ["user_id"], unique=True)
        op.create_index(op.f("ix_user_experience_created_at"), "user_experience", ["created_at"], unique=False)
        if dialect != "sqlite":
            op.create_foreign_key("fk_experience_user", "user_experience", "users", ["user_id"], ["id"])

    baking_columns = {col["name"] for col in inspector.get_columns("user_baking_records")}
    with op.batch_alter_table("user_baking_records", schema=None) as batch_op:
        if "is_excellent" not in baking_columns:
            batch_op.add_column(sa.Column("is_excellent", sa.Boolean(), nullable=False, server_default=sa.false()))
            batch_op.create_index(op.f("ix_user_baking_records_is_excellent"), ["is_excellent"], unique=False)


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    baking_columns = {col["name"] for col in inspector.get_columns("user_baking_records")}
    with op.batch_alter_table("user_baking_records", schema=None) as batch_op:
        if "is_excellent" in baking_columns:
            batch_op.drop_index(op.f("ix_user_baking_records_is_excellent"))
            batch_op.drop_column("is_excellent")

    if "user_experience" in tables:
        op.drop_table("user_experience")
