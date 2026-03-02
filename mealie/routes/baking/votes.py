"""作品投票路由（送花/送鸡蛋）"""
from fastapi import Depends, HTTPException, Query, status
from pydantic import UUID4
from sqlalchemy import and_
from sqlalchemy.orm import joinedload

from mealie.core.dependencies.dependencies import require_complete_profile
from mealie.db.models.baking.baking_records import UserBakingRecord
from mealie.db.models.baking.points import UserPoints
from mealie.db.models.baking.votes import VoteType, WorkVote
from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.baking.votes import ReceivedVoteRecord, ReceivedVoteRecords, VoteRequest, VoteResponse
from mealie.services.baking.experience import EXP_REWARD, EXP_SOURCE_RECEIVE_FLOWER, add_experience

router = UserAPIRouter()

VOTE_COST = 5  # 投票消耗的积分


@controller(router)
class VotesController(BaseUserController):
    @router.get("/received", response_model=ReceivedVoteRecords)
    async def get_received_votes(
        self,
        vote_type: VoteType | None = Query(None, description="过滤投票类型 flower/egg"),
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=100),
    ):
        """获取当前用户收到的鲜花/鸡蛋记录（分页）"""
        query = (
            self.session.query(WorkVote)
            .join(UserBakingRecord, WorkVote.work_id == UserBakingRecord.id)
            .filter(UserBakingRecord.user_id == self.user.id)
            .options(
                joinedload(WorkVote.user),
                joinedload(WorkVote.work).joinedload(UserBakingRecord.recipe),
            )
            .order_by(WorkVote.created_at.desc())
        )
        if vote_type is not None:
            query = query.filter(WorkVote.vote_type == vote_type)

        total = query.count()
        offset = (page - 1) * per_page
        votes = query.offset(offset).limit(per_page).all()
        items = [
            ReceivedVoteRecord(
                vote_id=vote.id,
                work_id=vote.work_id,
                recipe_id=vote.work.recipe_id,
                recipe_name=vote.work.recipe.name if vote.work and vote.work.recipe else None,
                vote_type=VoteType(vote.vote_type.value) if hasattr(vote.vote_type, "value") else vote.vote_type,
                voter_user_id=vote.user_id,
                voter_name=(vote.user.full_name or vote.user.username) if vote.user else None,
                created_at=vote.created_at,
            )
            for vote in votes
        ]
        pages = (total + per_page - 1) // per_page if total else 0
        return ReceivedVoteRecords(
            page=page,
            per_page=per_page,
            total=total,
            pages=pages,
            items=items,
        )

    @router.post("/", response_model=VoteResponse, dependencies=[Depends(require_complete_profile)])
    async def vote(self, data: VoteRequest):
        """给作品送花或送鸡蛋（需要完善资料）"""
        # 1. 验证作品存在
        work = self.session.query(UserBakingRecord).filter(UserBakingRecord.id == data.work_id).first()
        if not work:
            raise HTTPException(status_code=404, detail="作品不存在")

        # 不能给自己的作品投票
        if work.user_id == self.user.id:
            raise HTTPException(status_code=400, detail="不能给自己的作品投票")

        # 2. 检查是否已投票（一个用户对一个作品每种类型只能投一次）
        existing_vote = (
            self.session.query(WorkVote)
            .filter(
                and_(
                    WorkVote.work_id == data.work_id,
                    WorkVote.user_id == self.user.id,
                    WorkVote.vote_type == data.vote_type,
                )
            )
            .first()
        )
        if existing_vote:
            raise HTTPException(status_code=400, detail="您已经对该作品投过票了")

        # 3. 检查积分是否足够（-5积分）
        user_points = (
            self.session.query(UserPoints).filter(UserPoints.user_id == self.user.id).first()
        )
        if not user_points:
            user_points = UserPoints(
                session=self.session,
                user_id=self.user.id,
                total_points=0,
                consecutive_days=0,
            )
            self.session.add(user_points)
            self.session.commit()

        if user_points.total_points < VOTE_COST:
            raise HTTPException(
                status_code=400,
                detail=f"积分不足，需要 {VOTE_COST} 积分，当前只有 {user_points.total_points} 积分",
            )

        # 4. 创建投票记录
        vote = WorkVote(
            session=self.session,
            work_id=data.work_id,
            user_id=self.user.id,
            vote_type=data.vote_type,
        )
        self.session.add(vote)

        # 5. 更新作品的鲜花/鸡蛋数
        if data.vote_type == VoteType.FLOWER:
            work.flower_count += 1
            add_experience(
                self.session,
                work.user_id,
                EXP_REWARD[EXP_SOURCE_RECEIVE_FLOWER],
                source=EXP_SOURCE_RECEIVE_FLOWER,
            )
        elif data.vote_type == VoteType.EGG:
            work.egg_count += 1

        # 6. 扣除积分
        user_points.total_points -= VOTE_COST

        self.session.commit()
        self.session.refresh(work)
        self.session.refresh(user_points)

        return VoteResponse(
            success=True,
            work_id=data.work_id,
            vote_type=data.vote_type,
            flower_count=work.flower_count,
            egg_count=work.egg_count,
            points_remaining=user_points.total_points,
            message=f"投票成功！消耗 {VOTE_COST} 积分",
        )

    @router.delete("/{work_id}/{vote_type}", response_model=VoteResponse)
    async def cancel_vote(self, work_id: UUID4, vote_type: str):
        """取消投票（退还积分）"""
        # 验证投票类型
        try:
            vote_type_enum = VoteType(vote_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的投票类型: {vote_type}")

        # 查找投票记录
        vote = (
            self.session.query(WorkVote)
            .filter(
                and_(
                    WorkVote.work_id == work_id,
                    WorkVote.user_id == self.user.id,
                    WorkVote.vote_type == vote_type_enum,
                )
            )
            .first()
        )

        if not vote:
            raise HTTPException(status_code=404, detail="未找到投票记录")

        # 获取作品
        work = self.session.query(UserBakingRecord).filter(UserBakingRecord.id == work_id).first()
        if not work:
            raise HTTPException(status_code=404, detail="作品不存在")

        # 获取用户积分
        user_points = (
            self.session.query(UserPoints).filter(UserPoints.user_id == self.user.id).first()
        )
        if not user_points:
            user_points = UserPoints(
                session=self.session,
                user_id=self.user.id,
                total_points=0,
                consecutive_days=0,
            )
            self.session.add(user_points)

        # 更新作品的鲜花/鸡蛋数
        if vote_type_enum == VoteType.FLOWER and work.flower_count > 0:
            work.flower_count -= 1
        elif vote_type_enum == VoteType.EGG and work.egg_count > 0:
            work.egg_count -= 1

        # 退还积分
        user_points.total_points += VOTE_COST

        # 删除投票记录
        self.session.delete(vote)

        self.session.commit()
        self.session.refresh(work)
        self.session.refresh(user_points)

        return VoteResponse(
            success=True,
            work_id=work_id,
            vote_type=vote_type_enum,
            flower_count=work.flower_count,
            egg_count=work.egg_count,
            points_remaining=user_points.total_points,
            message=f"已取消投票，退还 {VOTE_COST} 积分",
        )
