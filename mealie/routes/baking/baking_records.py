"""烘焙作品集路由"""
from datetime import datetime

from fastapi import Depends, HTTPException, Query, status
from pydantic import UUID4
from sqlalchemy import and_, desc, distinct, func, select
from sqlalchemy.orm import joinedload

from mealie.core.dependencies.dependencies import require_complete_profile
from mealie.db.models.baking.baking_records import UserBakingRecord
from mealie.db.models.baking.votes import VoteType, WorkVote
from mealie.db.models.users import User
from mealie.db.models.users.user_details import UserDetails
from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.baking.baking_records import (
    BakingRecordCreate,
    BakingRecordOut,
    BakingRecordPagination,
    BakingRecordUpdate,
)
from mealie.schema.response.pagination import PaginationBase

router = UserAPIRouter()


@controller(router)
class BakingRecordsController(BaseUserController):
    @router.post("/", response_model=BakingRecordOut, status_code=201, dependencies=[Depends(require_complete_profile)])
    async def create_baking_record(self, data: BakingRecordCreate):
        """提交烘焙作品（需要完善资料，一个用户对一个配方只能上传一次）"""
        # 1. 验证食谱存在
        recipe = self.repos.recipes.get_one(data.recipe_id, "id")
        if not recipe:
            raise HTTPException(status_code=404, detail="食谱不存在")

        # 2. 检查是否已经上传过作品（一个用户对一个配方只能上传一次）
        existing_record = (
            self.session.query(UserBakingRecord)
            .filter(
                and_(
                    UserBakingRecord.recipe_id == data.recipe_id,
                    UserBakingRecord.user_id == self.user.id,
                )
            )
            .first()
        )
        if existing_record:
            raise HTTPException(
                status_code=400,
                detail="您已经对该配方提交过作品，每个配方只能提交一次"
            )

        # 3. 初始化积分（如果用户没有积分记录）
        user_points = self.repos.user_points.get_one(self.user.id, "user_id")
        if not user_points:
            self.repos.user_points.create({"user_id": self.user.id, "total_points": 0, "consecutive_days": 0})

        # 4. 创建作品记录
        record_data = data.model_dump()
        record_data["user_id"] = self.user.id
        record_data["flower_count"] = 0
        record_data["egg_count"] = 0

        record = self.repos.baking_records.create(record_data)
        return self._enrich_baking_record(record)

    @router.get("/grades", response_model=list[str])
    async def get_grade_list(self):
        """获取作品作者的年级列表（用于筛选）"""
        stmt = (
            select(distinct(UserDetails.grade))
            .select_from(UserBakingRecord)
            .join(UserDetails, UserBakingRecord.user_id == UserDetails.user_id)
            .where(UserDetails.grade.isnot(None), UserDetails.grade != "")
        )
        result = self.session.execute(stmt).scalars().all()
        return sorted([grade for grade in result if grade])

    @router.get("/classes", response_model=list[str])
    async def get_baking_class_list(self, grade: str | None = Query(None, description="按年级过滤班级")):
        """获取作品作者的班级列表（可按年级筛选）"""
        stmt = (
            select(distinct(UserDetails.class_name))
            .select_from(UserBakingRecord)
            .join(UserDetails, UserBakingRecord.user_id == UserDetails.user_id)
            .where(UserDetails.class_name.isnot(None), UserDetails.class_name != "")
        )
        if grade:
            stmt = stmt.where(UserDetails.grade == grade)
        result = self.session.execute(stmt).scalars().all()
        return sorted([class_name for class_name in result if class_name])

    @router.get("/{work_id}", response_model=BakingRecordOut)
    async def get_baking_record(self, work_id: UUID4):
        """获取单个作品详情"""
        record = self.repos.baking_records.get_one(work_id, "id")
        if not record:
            raise HTTPException(status_code=404, detail="作品不存在")

        return self._enrich_baking_record(record)

    @router.put("/{work_id}", response_model=BakingRecordOut)
    async def update_baking_record(self, work_id: UUID4, data: BakingRecordUpdate):
        """更新作品（只能更新自己的作品）"""
        record = self.repos.baking_records.get_one(work_id, "id")
        if not record:
            raise HTTPException(status_code=404, detail="作品不存在")

        # 检查权限：只能更新自己的作品
        if record.user_id != self.user.id:
            raise HTTPException(status_code=403, detail="只能更新自己的作品")

        # 更新作品
        updated = self.repos.baking_records.update(work_id, data.model_dump(exclude_unset=True))
        return self._enrich_baking_record(updated)

    @router.get("/", response_model=BakingRecordPagination)
    async def get_baking_records(
        self,
        recipe_id: UUID4 | None = Query(None, description="食谱ID"),
        user_id: UUID4 | None = Query(None, description="用户ID"),
        grade: str | None = Query(None, description="年级"),
        class_name: str | None = Query(None, description="班级名称"),
        sort_by: str = Query("created_at", description="排序字段"),
        order: str = Query("desc", description="排序方向"),
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=100),
    ):
        """获取作品列表（支持筛选和排序）"""
        # 构建基础查询
        query = select(UserBakingRecord).options(
            joinedload(UserBakingRecord.user).joinedload(User.user_details),
            joinedload(UserBakingRecord.recipe),
        )

        # 筛选条件
        filters = []
        if recipe_id:
            filters.append(UserBakingRecord.recipe_id == recipe_id)
        if user_id:
            filters.append(UserBakingRecord.user_id == user_id)

        # 按年级/班级筛选（通过 user_details 关联）
        if grade or class_name:
            query = query.join(UserDetails, UserBakingRecord.user_id == UserDetails.user_id)
            if grade:
                filters.append(UserDetails.grade == grade)
            if class_name:
                filters.append(UserDetails.class_name == class_name)

        if filters:
            query = query.filter(and_(*filters))

        # 排序
        if sort_by == "flower_count":
            order_by = UserBakingRecord.flower_count
        elif sort_by == "egg_count":
            order_by = UserBakingRecord.egg_count
        else:  # created_at
            order_by = UserBakingRecord.created_at

        if order.lower() == "asc":
            query = query.order_by(order_by)
        else:
            query = query.order_by(desc(order_by))

        # 分页
        total = self.session.scalar(select(func.count()).select_from(query.subquery()))
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)

        records = self.session.execute(query).unique().scalars().all()

        # 转换为输出格式
        items = [self._enrich_baking_record_model(record) for record in records]

        return BakingRecordPagination(
            items=items,
            total=total or 0,
            page=page,
            per_page=per_page,
            pages=(total + per_page - 1) // per_page if total else 0,
        )

    def _enrich_baking_record(self, record: BakingRecordOut) -> BakingRecordOut:
        """丰富作品信息（添加用户信息、投票状态等）"""
        if hasattr(record, "id"):
            record_model = self.session.get(UserBakingRecord, record.id)
            if record_model:
                return self._enrich_baking_record_model(record_model)
        return record

    def _enrich_baking_record_model(self, record: UserBakingRecord | None) -> BakingRecordOut:
        """从模型丰富作品信息"""
        if not record:
            raise HTTPException(status_code=404, detail="作品不存在")

        # 获取用户详细信息
        user_details = self.session.query(UserDetails).filter(UserDetails.user_id == record.user_id).first()

        # 检查当前用户是否已投票
        has_flowered = False
        has_egged = False
        if self.user:
            flower_vote = (
                self.session.query(WorkVote)
                .filter(
                    and_(
                        WorkVote.work_id == record.id,
                        WorkVote.user_id == self.user.id,
                        WorkVote.vote_type == VoteType.FLOWER,
                    )
                )
                .first()
            )
            egg_vote = (
                self.session.query(WorkVote)
                .filter(
                    and_(
                        WorkVote.work_id == record.id,
                        WorkVote.user_id == self.user.id,
                        WorkVote.vote_type == VoteType.EGG,
                    )
                )
                .first()
            )
            has_flowered = flower_vote is not None
            has_egged = egg_vote is not None

        # 获取食谱名称
        recipe_name = None
        if record.recipe:
            recipe_name = record.recipe.name

        # 构建输出
        record_dict = {
            "id": record.id,
            "recipe_id": record.recipe_id,
            "user_id": record.user_id,
            "image_url": record.image_url,
            "notes": record.notes,
            "flower_count": record.flower_count,
            "egg_count": record.egg_count,
            "created_at": record.created_at,
            "update_at": record.update_at,
            "user_name": record.user.username if record.user else None,
            "user_full_name": record.user.full_name if record.user else None,
            "avatar_url": user_details.avatar_url if user_details else None,
            "grade": user_details.grade if user_details else None,
            "class_name": user_details.class_name if user_details else None,
            "group_name": self._get_user_group_name(record.user_id),
            "recipe_name": recipe_name,
            "has_flowered": has_flowered,
            "has_egged": has_egged,
        }

        return BakingRecordOut(**record_dict)

    def _get_user_group_name(self, user_id) -> str | None:
        """获取用户的小组名称"""
        from mealie.db.models.baking.classes import UserClass
        user_class = self.session.query(UserClass).filter(UserClass.user_id == user_id).first()
        return user_class.group_name if user_class else None
