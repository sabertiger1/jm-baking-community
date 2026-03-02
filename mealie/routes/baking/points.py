"""用户积分和签到路由"""
from datetime import date, datetime, timedelta

from fastapi import HTTPException, Query
from sqlalchemy import desc, select

from mealie.db.models.baking.checkins import UserCheckinHistory
from mealie.db.models.baking.experience import UserExperience
from mealie.db.models.baking.experience_history import UserExperienceHistory
from mealie.db.models.baking.points import UserPoints
from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.baking.points import (
    CheckinHistoryResponse,
    CheckinRequest,
    CheckinResponse,
    PointsOut,
    UserExperienceBatchOut,
    UserExperienceHistoryItem,
    UserExperienceHistoryOut,
    UserExperienceOut,
    UserExperienceUpdateIn,
)
from mealie.services.baking.experience import (
    EXP_REWARD,
    EXP_SOURCE_CHECKIN,
    add_experience,
    get_user_experience_profile,
)

router = UserAPIRouter()

CHECKIN_POINTS = 10  # 签到获得的积分


@controller(router)
class PointsController(BaseUserController):
    @router.get("/me", response_model=PointsOut)
    async def get_my_points(self):
        """获取当前用户的积分信息"""
        # 如果用户没有积分记录，创建一条
        user_points = self.repos.user_points.get_one(self.user.id, "user_id")
        if not user_points:
            user_points = self.repos.user_points.create(
                {
                    "user_id": self.user.id,
                    "total_points": 0,
                    "consecutive_days": 0,
                    "last_checkin_date": None,
                }
            )
        return user_points

    @router.post("/checkin", response_model=CheckinResponse)
    async def checkin(self, data: CheckinRequest):
        """每日签到"""
        # 获取或创建积分记录
        user_points_model = (
            self.session.query(UserPoints).filter(UserPoints.user_id == self.user.id).first()
        )
        if not user_points_model:
            user_points_model = UserPoints(
                session=self.session,
                user_id=self.user.id,
                total_points=0,
                consecutive_days=0,
                last_checkin_date=None,
            )
            self.session.add(user_points_model)
            self.session.commit()
            self.session.refresh(user_points_model)

        today = date.today().isoformat()

        # 1. 检查今日是否已签到
        if user_points_model.last_checkin_date == today:
            raise HTTPException(
                status_code=400, detail="今日已经签到过了，请明天再来"
            )

        # 2. 计算连续天数
        consecutive_days = 1
        if user_points_model.last_checkin_date:
            last_date = datetime.fromisoformat(user_points_model.last_checkin_date).date()
            yesterday = date.today() - timedelta(days=1)
            if last_date == yesterday:
                # 连续签到
                consecutive_days = user_points_model.consecutive_days + 1
            # 如果不是昨天，连续天数重置为1

        # 3. 增加积分（+10）
        new_total_points = user_points_model.total_points + CHECKIN_POINTS

        # 4. 更新积分记录
        user_points_model.total_points = new_total_points
        user_points_model.consecutive_days = consecutive_days
        user_points_model.last_checkin_date = today

        # 5. 写入签到历史（每天一条）
        existing_history = (
            self.session.query(UserCheckinHistory)
            .filter(
                UserCheckinHistory.user_id == self.user.id,
                UserCheckinHistory.checkin_date == today,
            )
            .first()
        )
        if not existing_history:
            checkin_history = UserCheckinHistory(
                session=self.session,
                user_id=self.user.id,
                checkin_date=today,
            )
            self.session.add(checkin_history)

        add_experience(
            self.session,
            self.user.id,
            EXP_REWARD[EXP_SOURCE_CHECKIN],
            source=EXP_SOURCE_CHECKIN,
        )
        self.session.commit()
        self.session.refresh(user_points_model)

        return CheckinResponse(
            success=True,
            points_earned=CHECKIN_POINTS,
            total_points=new_total_points,
            consecutive_days=consecutive_days,
            message=f"签到成功！获得 {CHECKIN_POINTS} 积分，已连续签到 {consecutive_days} 天",
        )

    @router.get("/history", response_model=CheckinHistoryResponse)
    async def get_checkin_history(self):
        """获取当前用户签到历史日期"""
        rows = (
            self.session.query(UserCheckinHistory.checkin_date)
            .filter(UserCheckinHistory.user_id == self.user.id)
            .order_by(UserCheckinHistory.checkin_date.desc())
            .all()
        )
        dates = [row[0] for row in rows if row and row[0]]
        return CheckinHistoryResponse(
            checkin_dates=dates,
            daily_points=CHECKIN_POINTS,
        )

    @router.get("/experience/me", response_model=UserExperienceOut)
    async def get_my_experience(self):
        profile = get_user_experience_profile(self.session, self.user.id)
        return UserExperienceOut(user_id=self.user.id, **profile)

    @router.get("/experience/users", response_model=UserExperienceBatchOut)
    async def get_users_experience(self, user_ids: list[str] = Query(default=[])):
        items: list[UserExperienceOut] = []
        for uid in user_ids:
            profile = get_user_experience_profile(self.session, uid)
            items.append(UserExperienceOut(user_id=uid, **profile))
        return UserExperienceBatchOut(items=items)

    @router.put("/experience/users/{user_id}", response_model=UserExperienceOut)
    async def update_user_experience(self, user_id: str, data: UserExperienceUpdateIn):
        if not self.user.admin:
            raise HTTPException(status_code=403, detail="只有管理员可以修改经验值")

        target_user = self.repos.users.get_one(user_id, "id")
        if not target_user:
            raise HTTPException(status_code=404, detail="用户不存在")

        exp_model = (
            self.session.query(UserExperience).filter(UserExperience.user_id == user_id).first()
        )
        if not exp_model:
            exp_model = UserExperience(
                session=self.session,
                user_id=user_id,
                total_exp=data.total_exp,
            )
            self.session.add(exp_model)
        else:
            exp_model.total_exp = data.total_exp

        self.session.commit()
        profile = get_user_experience_profile(self.session, user_id)
        return UserExperienceOut(user_id=user_id, **profile)

    @router.get("/experience/history", response_model=UserExperienceHistoryOut)
    async def get_my_experience_history(
        self,
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=100),
    ):
        base_query = (
            self.session.query(UserExperienceHistory)
            .filter(UserExperienceHistory.user_id == self.user.id)
            .order_by(UserExperienceHistory.created_at.desc())
        )
        total = base_query.count()
        offset = (page - 1) * per_page
        rows = base_query.offset(offset).limit(per_page).all()
        pages = (total + per_page - 1) // per_page if total else 0

        return UserExperienceHistoryOut(
            page=page,
            per_page=per_page,
            total=total,
            pages=pages,
            items=[
                UserExperienceHistoryItem(
                    id=row.id,
                    source=row.source,
                    exp_delta=row.exp_delta,
                    total_exp_after=row.total_exp_after,
                    note=row.note,
                    created_at=row.created_at,
                )
                for row in rows
            ],
        )

    @router.get("/leaderboard", response_model=list[PointsOut])
    async def get_leaderboard(self, limit: int = Query(10, ge=1, le=100)):
        """获取积分排行榜"""
        # 按总积分降序排列（通过用户关联获取 group_id）
        from mealie.db.models.users import User
        query = (
            select(UserPoints)
            .join(User, UserPoints.user_id == User.id)
            .filter(User.group_id == self.group_id)
            .order_by(desc(UserPoints.total_points))
            .limit(limit)
        )

        points_list = self.session.execute(query).scalars().all()
        return [PointsOut.model_validate(p) for p in points_list]
