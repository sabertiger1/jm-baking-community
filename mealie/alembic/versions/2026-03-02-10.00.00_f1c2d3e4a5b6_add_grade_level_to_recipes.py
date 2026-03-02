"""add grade_level to recipes

Revision ID: f1c2d3e4a5b6
Revises: c3d4e5f6a7b8
Create Date: 2026-03-02 10:00:00.000000
"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "f1c2d3e4a5b6"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    recipe_columns = {col["name"] for col in inspector.get_columns("recipes")}

    with op.batch_alter_table("recipes", schema=None) as batch_op:
        if "grade_level" not in recipe_columns:
            batch_op.add_column(sa.Column("grade_level", sa.String(), nullable=True))
            batch_op.create_index(batch_op.f("ix_recipes_grade_level"), ["grade_level"], unique=False)


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    recipe_columns = {col["name"] for col in inspector.get_columns("recipes")}

    with op.batch_alter_table("recipes", schema=None) as batch_op:
        if "grade_level" in recipe_columns:
            batch_op.drop_index(batch_op.f("ix_recipes_grade_level"))
            batch_op.drop_column("grade_level")
