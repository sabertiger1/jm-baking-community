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
