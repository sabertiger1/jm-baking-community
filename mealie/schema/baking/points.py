"""用户积分 Schema"""
from datetime import datetime

from pydantic import UUID4, Field

from mealie.schema._mealie import MealieModel


class PointsOut(MealieModel):
    """积分输出 Schema"""
    id: UUID4
    user_id: UUID4
    total_points: int = Field(default=0, description="总积分")
    consecutive_days: int = Field(default=0, description="连续签到天数")
    last_checkin_date: str | None = Field(None, description="最后签到日期 YYYY-MM-DD")
    created_at: datetime
    update_at: datetime
    
    model_config = {"from_attributes": True}


class PointsUpdate(MealieModel):
    """更新积分 Schema（通常由系统自动更新）"""
    total_points: int | None = None
    consecutive_days: int | None = None
    last_checkin_date: str | None = None


class CheckinRequest(MealieModel):
    """签到请求 Schema"""
    pass


class CheckinResponse(MealieModel):
    """签到响应 Schema"""
    success: bool
    points_earned: int = Field(default=10, description="获得的积分")
    total_points: int = Field(description="当前总积分")
    consecutive_days: int = Field(description="连续签到天数")
    message: str | None = None


class CheckinHistoryResponse(MealieModel):
    """签到历史响应"""

    checkin_dates: list[str] = Field(default_factory=list, description="签到日期列表 YYYY-MM-DD")
    daily_points: int = Field(default=10, description="每日签到积分")


class UserExperienceOut(MealieModel):
    """用户经验与等级"""

    user_id: UUID4
    total_exp: int = Field(default=1, description="总经验")
    level_key: str = Field(default="level-1", description="等级键")
    level_name: str = Field(default="烘焙小白", description="等级名称")
    level_emoji: str = Field(default="🧈", description="等级表情")
    current_level_min_exp: int = Field(default=0, description="当前等级起始经验")
    next_level_min_exp: int | None = Field(default=None, description="下一等级起始经验")
    next_level_name: str | None = Field(default=None, description="下一等级名称")


class UserExperienceBatchOut(MealieModel):
    items: list[UserExperienceOut]


class UserExperienceUpdateIn(MealieModel):
    total_exp: int = Field(..., ge=1, description="手动设置的总经验（最小为1）")


class UserExperienceHistoryItem(MealieModel):
    id: UUID4
    source: str
    exp_delta: int
    total_exp_after: int
    note: str | None = None
    created_at: datetime


class UserExperienceHistoryOut(MealieModel):
    page: int = 1
    per_page: int = 20
    total: int = 0
    pages: int = 0
    items: list[UserExperienceHistoryItem]
