"""烘焙作品记录 Schema"""
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import UUID4, Field, field_validator

from mealie.schema._mealie import MealieModel
from mealie.schema.response.pagination import PaginationBase

if TYPE_CHECKING:
    from mealie.schema.user.user import UserOut


class BakingRecordBase(MealieModel):
    """烘焙作品基础 Schema"""
    recipe_id: UUID4
    image_url: str = Field(..., description="成品图片URL")
    notes: str | None = Field(None, description="制作心得")


class BakingRecordCreate(BakingRecordBase):
    """创建烘焙作品 Schema"""
    pass


class BakingRecordUpdate(MealieModel):
    """更新烘焙作品 Schema"""
    image_url: str | None = None
    notes: str | None = None


class BakingRecordOut(BakingRecordBase):
    """烘焙作品输出 Schema"""
    id: UUID4
    user_id: UUID4
    flower_count: int = Field(default=0, description="鲜花数")
    egg_count: int = Field(default=0, description="鸡蛋数")
    created_at: datetime
    update_at: datetime
    
    # 关联信息
    user_name: str | None = Field(None, description="用户名")
    user_full_name: str | None = Field(None, description="用户全名")
    avatar_url: str | None = Field(None, description="用户头像URL")
    grade: str | None = Field(None, description="年级")
    class_name: str | None = Field(None, description="班级名称")
    group_name: str | None = Field(None, description="小组名称")
    recipe_name: str | None = Field(None, description="食谱名称")
    
    # 当前用户是否已投票
    has_flowered: bool = Field(default=False, description="是否已送花")
    has_egged: bool = Field(default=False, description="是否已送鸡蛋")
    
    model_config = {"from_attributes": True}


class BakingRecordPagination(PaginationBase):
    """烘焙作品分页 Schema"""
    items: list[BakingRecordOut]


class BakingRecordQuery(MealieModel):
    """烘焙作品查询 Schema"""
    recipe_id: UUID4 | None = None
    user_id: UUID4 | None = None
    class_name: str | None = None
    group_name: str | None = None
    sort_by: str = Field(default="created_at", description="排序字段: created_at, flower_count, egg_count")
    order: str = Field(default="desc", description="排序方向: asc, desc")
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
