"""add user role field

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2025-01-15 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    user_columns = {col["name"] for col in inspector.get_columns("users")}
    dialect = bind.dialect.name

    # 添加 role 字段（幂等 + 多数据库兼容）
    if "role" not in user_columns:
        if dialect == "postgresql":
            op.execute(
                "DO $$ BEGIN "
                "IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole') THEN "
                "CREATE TYPE userrole AS ENUM ('student', 'teacher', 'admin'); "
                "END IF; "
                "END $$;"
            )
            op.add_column(
                "users",
                sa.Column(
                    "role",
                    postgresql.ENUM("student", "teacher", "admin", name="userrole", create_type=False),
                    nullable=True,
                    server_default=sa.text("'student'"),
                ),
            )
        else:
            op.add_column("users", sa.Column("role", sa.String(length=20), nullable=True, server_default="student"))

    # 更新现有用户：管理员设置为 admin，其他设置为 student
    op.execute("UPDATE users SET role = 'admin' WHERE admin = true")
    op.execute("UPDATE users SET role = 'student' WHERE role IS NULL")


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    user_columns = {col["name"] for col in inspector.get_columns("users")}
    dialect = bind.dialect.name

    # 删除 role 字段（幂等）
    if "role" in user_columns:
        op.drop_column("users", "role")

    # 删除枚举类型（仅 PostgreSQL）
    if dialect == "postgresql":
        op.execute("DROP TYPE IF EXISTS userrole")
