"""用户班级和小组 Schema"""
from datetime import datetime

from pydantic import UUID4, Field

from mealie.schema._mealie import MealieModel


class UserClassBase(MealieModel):
    """班级基础 Schema"""
    class_name: str | None = Field(None, description="班级名称")
    group_name: str | None = Field(None, description="小组名称")


class UserClassCreate(UserClassBase):
    """创建班级信息 Schema"""
    user_id: UUID4


class UserClassUpdate(UserClassBase):
    """更新班级信息 Schema"""
    pass


class UserClassOut(UserClassBase):
    """班级信息输出 Schema"""
    id: UUID4
    user_id: UUID4
    created_at: datetime
    update_at: datetime
    
    model_config = {"from_attributes": True}
