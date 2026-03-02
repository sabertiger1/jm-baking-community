"""作品投票 Schema"""
from datetime import datetime
from enum import Enum

from pydantic import UUID4, Field

from mealie.schema._mealie import MealieModel


class VoteType(str, Enum):
    """投票类型"""
    FLOWER = "flower"  # 送花
    EGG = "egg"  # 送鸡蛋


class WorkVoteBase(MealieModel):
    """投票基础 Schema"""
    work_id: UUID4
    vote_type: VoteType


class WorkVoteCreate(WorkVoteBase):
    """创建投票 Schema"""
    pass


class WorkVoteOut(WorkVoteBase):
    """投票输出 Schema"""
    id: UUID4
    user_id: UUID4
    created_at: datetime
    update_at: datetime
    
    model_config = {"from_attributes": True}


class VoteRequest(MealieModel):
    """投票请求 Schema"""
    work_id: UUID4
    vote_type: VoteType


class VoteResponse(MealieModel):
    """投票响应 Schema"""
    success: bool
    work_id: UUID4
    vote_type: VoteType
    flower_count: int = Field(default=0, description="当前鲜花数")
    egg_count: int = Field(default=0, description="当前鸡蛋数")
    points_remaining: int = Field(description="剩余积分")
    message: str | None = None


class ReceivedVoteRecord(MealieModel):
    """我收到的投票明细"""
    vote_id: UUID4
    work_id: UUID4
    recipe_id: UUID4
    recipe_name: str | None = None
    vote_type: VoteType
    voter_user_id: UUID4
    voter_name: str | None = None
    created_at: datetime


class ReceivedVoteRecords(MealieModel):
    items: list[ReceivedVoteRecord]
