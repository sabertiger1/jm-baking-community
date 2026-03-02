"""adjust experience default to 1

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-03-04 09:00:00.000000
"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "e5f6a7b8c9d0"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    if "user_experience" not in tables:
        return

    with op.batch_alter_table("user_experience", schema=None) as batch_op:
        batch_op.alter_column("total_exp", server_default="1")

    bind.execute(sa.text("UPDATE user_experience SET total_exp = 1 WHERE total_exp < 1"))


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    if "user_experience" not in tables:
        return

    with op.batch_alter_table("user_experience", schema=None) as batch_op:
        batch_op.alter_column("total_exp", server_default="0")
