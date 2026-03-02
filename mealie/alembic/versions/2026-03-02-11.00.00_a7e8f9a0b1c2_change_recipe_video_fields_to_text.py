"""change recipe video fields to Text

Revision ID: a7e8f9a0b1c2
Revises: f1c2d3e4a5b6
Create Date: 2026-03-02 11:00:00.000000
"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "a7e8f9a0b1c2"
down_revision = "f1c2d3e4a5b6"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    recipe_columns = {col["name"] for col in inspector.get_columns("recipes")}

    with op.batch_alter_table("recipes", schema=None) as batch_op:
        if "making_video_url" in recipe_columns:
            batch_op.alter_column("making_video_url", existing_type=sa.String(), type_=sa.Text(), existing_nullable=True)
        if "key_points_video_url" in recipe_columns:
            batch_op.alter_column("key_points_video_url", existing_type=sa.String(), type_=sa.Text(), existing_nullable=True)


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    recipe_columns = {col["name"] for col in inspector.get_columns("recipes")}

    with op.batch_alter_table("recipes", schema=None) as batch_op:
        if "key_points_video_url" in recipe_columns:
            batch_op.alter_column("key_points_video_url", existing_type=sa.Text(), type_=sa.String(), existing_nullable=True)
        if "making_video_url" in recipe_columns:
            batch_op.alter_column("making_video_url", existing_type=sa.Text(), type_=sa.String(), existing_nullable=True)
