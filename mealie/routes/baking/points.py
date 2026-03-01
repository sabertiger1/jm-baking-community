"""用户积分和签到路由"""
from datetime import date, datetime, timedelta

from fastapi import HTTPException, Query, status
from sqlalchemy import desc, func, select

from mealie.db.models.baking.points import UserPoints
from mealie.db.models._model_utils.guid import GUID
from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.baking.points import CheckinRequest, CheckinResponse, PointsOut

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
        self.session.commit()
        self.session.refresh(user_points_model)

        return CheckinResponse(
            success=True,
            points_earned=CHECKIN_POINTS,
            total_points=new_total_points,
            consecutive_days=consecutive_days,
            message=f"签到成功！获得 {CHECKIN_POINTS} 积分，已连续签到 {consecutive_days} 天",
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
