"""Add baking community features

Revision ID: a1b2c3d4e5f6
Revises: 1d9a002d7234
Create Date: 2025-01-15 20:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

import mealie.db.migration_types

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision: str | None = "1d9a002d7234"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    # Add video fields to recipes table
    with op.batch_alter_table("recipes", schema=None) as batch_op:
        batch_op.add_column(sa.Column("making_video_url", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("key_points_video_url", sa.String(), nullable=True))

    # Create user_baking_records table
    op.create_table(
        "user_baking_records",
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("recipe_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("user_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("image_url", sa.String(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("flower_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("egg_count", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_baking_records_recipe_id"), "user_baking_records", ["recipe_id"], unique=False)
    op.create_index(op.f("ix_user_baking_records_user_id"), "user_baking_records", ["user_id"], unique=False)
    op.create_index(op.f("ix_user_baking_records_flower_count"), "user_baking_records", ["flower_count"], unique=False)
    op.create_index(op.f("ix_user_baking_records_egg_count"), "user_baking_records", ["egg_count"], unique=False)
    op.create_index(
        op.f("ix_user_baking_records_created_at"), "user_baking_records", ["created_at"], unique=False
    )
    op.create_foreign_key("fk_baking_record_recipe", "recipes", ["recipe_id"], ["id"])
    op.create_foreign_key("fk_baking_record_user", "users", ["user_id"], ["id"])

    # Create recipe_ratings table
    op.create_table(
        "recipe_ratings",
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("recipe_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("user_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("recipe_id", "user_id", name="recipe_user_rating_unique"),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="rating_range_check"),
    )
    op.create_index(op.f("ix_recipe_ratings_recipe_id"), "recipe_ratings", ["recipe_id"], unique=False)
    op.create_index(op.f("ix_recipe_ratings_user_id"), "recipe_ratings", ["user_id"], unique=False)
    op.create_index(op.f("ix_recipe_ratings_created_at"), "recipe_ratings", ["created_at"], unique=False)
    op.create_foreign_key("fk_rating_recipe", "recipes", ["recipe_id"], ["id"])
    op.create_foreign_key("fk_rating_user", "users", ["user_id"], ["id"])

    # Create user_points table
    op.create_table(
        "user_points",
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("user_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("total_points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("consecutive_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_checkin_date", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_user_points_user_id"), "user_points", ["user_id"], unique=True)
    op.create_index(op.f("ix_user_points_created_at"), "user_points", ["created_at"], unique=False)
    op.create_foreign_key("fk_points_user", "users", ["user_id"], ["id"])

    # Create work_votes table
    op.create_table(
        "work_votes",
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("work_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("user_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("vote_type", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("work_id", "user_id", "vote_type", name="work_user_vote_type_unique"),
    )
    op.create_index(op.f("ix_work_votes_work_id"), "work_votes", ["work_id"], unique=False)
    op.create_index(op.f("ix_work_votes_user_id"), "work_votes", ["user_id"], unique=False)
    op.create_index(op.f("ix_work_votes_vote_type"), "work_votes", ["vote_type"], unique=False)
    op.create_index(op.f("ix_work_votes_created_at"), "work_votes", ["created_at"], unique=False)
    op.create_foreign_key("fk_vote_work", "user_baking_records", ["work_id"], ["id"])
    op.create_foreign_key("fk_vote_user", "users", ["user_id"], ["id"])

    # Create user_classes table
    op.create_table(
        "user_classes",
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("user_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("class_name", sa.String(), nullable=True),
        sa.Column("group_name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_user_classes_user_id"), "user_classes", ["user_id"], unique=True)
    op.create_index(op.f("ix_user_classes_class_name"), "user_classes", ["class_name"], unique=False)
    op.create_index(op.f("ix_user_classes_group_name"), "user_classes", ["group_name"], unique=False)
    op.create_index(op.f("ix_user_classes_created_at"), "user_classes", ["created_at"], unique=False)
    op.create_foreign_key("fk_class_user", "users", ["user_id"], ["id"])


def downgrade():
    # Drop user_classes table
    op.drop_table("user_classes")

    # Drop work_votes table
    op.drop_table("work_votes")

    # Drop user_points table
    op.drop_table("user_points")

    # Drop recipe_ratings table
    op.drop_table("recipe_ratings")

    # Drop user_baking_records table
    op.drop_table("user_baking_records")

    # Remove video fields from recipes table
    with op.batch_alter_table("recipes", schema=None) as batch_op:
        batch_op.drop_column("key_points_video_url")
        batch_op.drop_column("making_video_url")
