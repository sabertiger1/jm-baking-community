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
    # 创建用户角色枚举类型（PostgreSQL）
    op.execute("CREATE TYPE userrole AS ENUM ('student', 'teacher', 'admin')")
    
    # 添加role字段到users表
    op.add_column("users", sa.Column("role", postgresql.ENUM("student", "teacher", "admin", name="userrole", create_type=False), nullable=True, server_default="'student'"))
    
    # 更新现有用户：管理员设置为admin，其他设置为student
    op.execute("UPDATE users SET role = 'admin' WHERE admin = true")
    op.execute("UPDATE users SET role = 'student' WHERE role IS NULL")


def downgrade():
    # 删除role字段
    op.drop_column("users", "role")
    
    # 删除枚举类型
    op.execute("DROP TYPE IF EXISTS userrole")
