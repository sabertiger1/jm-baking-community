"""食谱评分和评论 Schema"""
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import UUID4, Field, field_validator

from mealie.schema._mealie import MealieModel

if TYPE_CHECKING:
    from mealie.schema.user.user import UserOut


class RecipeRatingBase(MealieModel):
    """评分基础 Schema"""
    recipe_id: UUID4
    rating: int = Field(..., ge=1, le=5, description="评分 1-5星")
    comment: str | None = Field(None, description="文字评论")


class RecipeRatingCreate(RecipeRatingBase):
    """创建评分 Schema"""
    pass


class RecipeRatingUpdate(MealieModel):
    """更新评分 Schema"""
    rating: int | None = Field(None, ge=1, le=5)
    comment: str | None = None


class RecipeRatingOut(RecipeRatingBase):
    """评分输出 Schema"""
    id: UUID4
    user_id: UUID4
    created_at: datetime
    update_at: datetime
    
    # 关联信息
    user_name: str | None = Field(None, description="用户名")
    user_full_name: str | None = Field(None, description="用户全名")
    avatar_url: str | None = Field(None, description="用户头像URL")
    class_name: str | None = Field(None, description="班级名称")
    grade: str | None = Field(None, description="年级")
    
    model_config = {"from_attributes": True}


class RecipeRatingSummary(MealieModel):
    """评分统计 Schema"""
    recipe_id: UUID4
    average_rating: float | None = Field(None, description="平均评分")
    total_ratings: int = Field(default=0, description="总评分数量")
    rating_distribution: dict[int, int] = Field(default_factory=dict, description="评分分布 {1: 数量, 2: 数量, ...}")
