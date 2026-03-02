"""用户详细资料路由"""
from fastapi import HTTPException, status
from pydantic import UUID4

from mealie.db.models.users.users import UserRole
from mealie.db.models.users.user_details import UserDetails
from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.user.user_details import (
    CompleteProfileRequest,
    UserDetailsCompleteCheck,
    UserDetailsOut,
    UserDetailsPublic,
    UserDetailsUpdate,
)

router = UserAPIRouter()


@controller(router)
class UserDetailsController(BaseUserController):
    ADMIN_GRADE = "管理员"
    ADMIN_CLASS_NAME = "老师"
    @staticmethod
    def _normalize_text(value: str | None) -> str:
        return (value or "").strip()

    @staticmethod
    def _compute_is_complete(real_name: str | None, grade: str | None, class_name: str | None, avatar_url: str | None) -> bool:
        return bool(
            (real_name or "").strip()
            and (grade or "").strip()
            and (class_name or "").strip()
            and (avatar_url or "").strip()
        )

    @classmethod
    def _sync_complete_status(cls, target) -> None:
        target.is_complete = cls._compute_is_complete(
            getattr(target, "real_name", None),
            getattr(target, "grade", None),
            getattr(target, "class_name", None),
            getattr(target, "avatar_url", None),
        )

    @classmethod
    def _enforce_grade_class_one_time_lock(cls, existing, update_data: dict) -> None:
        has_grade_input = "grade" in update_data and update_data.get("grade") is not None
        has_class_input = "class_name" in update_data and update_data.get("class_name") is not None

        old_grade = cls._normalize_text(getattr(existing, "grade", None))
        old_class_name = cls._normalize_text(getattr(existing, "class_name", None))
        new_grade = cls._normalize_text(update_data.get("grade"))
        new_class_name = cls._normalize_text(update_data.get("class_name"))

        if has_grade_input and old_grade and new_grade != old_grade:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="年级已填写且已锁定，不可再次修改",
            )

        if has_class_input and old_class_name and new_class_name != old_class_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="班级已填写且已锁定，不可再次修改",
            )

    def _persist_user_details(self, user_details):
        """
        持久化用户资料。
        说明：
        - 之前通过通用仓库的 update 方法更新，内部依赖 _query_one，
          在某些带 group/household 作用域的场景下可能抛出 NoResultFound。
        - 这里改为直接使用 ORM 会话按主键更新，避免额外作用域过滤导致查不到记录。
        """
        # 从 Pydantic 模型中提取字段
        data = user_details.model_dump()

        # 仅保留 ORM 上真实存在且需要更新的字段
        allowed_keys = {
            "real_name",
            "grade",
            "class_name",
            "avatar_url",
            "is_complete",
        }

        # 通过主键获取 ORM 实体；这里不附加 group/household 过滤，避免查不到
        orm_obj = self.session.get(UserDetails, data["id"])
        if not orm_obj:
            # 理论上不应发生，如果发生则创建一条兜底记录
            orm_obj = UserDetails(session=self.session, **{
                "id": data["id"],
                "user_id": data["user_id"],
                **{k: v for k, v in data.items() if k in allowed_keys},
            })
            self.session.add(orm_obj)
        else:
            for key in allowed_keys:
                if key in data:
                    setattr(orm_obj, key, data[key])

        orm_obj.update_complete_status()

        self.session.add(orm_obj)
        self.session.commit()

        return UserDetailsOut.model_validate(orm_obj)

    @router.get("/me/details", response_model=UserDetailsOut | None)
    async def get_my_details(self):
        """获取当前用户的详细资料"""
        user_details = self.repos.user_details.get_one(self.user.id, "user_id")
        if not user_details:
            return None
        return UserDetailsOut.model_validate(user_details)

    @router.post("/me/details/complete", response_model=UserDetailsOut, status_code=201)
    async def complete_profile(self, data: CompleteProfileRequest):
        """完善个人资料（首次登录强制调用）"""
        # 管理员的年级/班级固定为“管理员/老师”
        if self.user.admin:
            data.grade = self.ADMIN_GRADE
            data.class_name = self.ADMIN_CLASS_NAME

        # 验证必填字段
        missing_fields = []
        if not (data.real_name or "").strip():
            missing_fields.append("real_name")
        if not (data.grade or "").strip():
            missing_fields.append("grade")
        if not (data.class_name or "").strip():
            missing_fields.append("class_name")
        if not (data.avatar_url or "").strip():
            missing_fields.append("avatar_url")
        
        if missing_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"请完善以下必填字段：{', '.join(missing_fields)}"
            )
        
        # 检查是否已存在资料
        existing = self.repos.user_details.get_one(self.user.id, "user_id")
        
        if existing:
            # 更新现有资料
            update_data = data.model_dump(exclude_unset=True)
            if not self.user.admin:
                self._enforce_grade_class_one_time_lock(existing, update_data)
            for key, value in update_data.items():
                setattr(existing, key, value)
            self._sync_complete_status(existing)
            self._persist_user_details(existing)
        else:
            # 创建新资料
            create_data = data.model_dump()
            create_data["user_id"] = self.user.id
            create_data["is_complete"] = self._compute_is_complete(
                create_data.get("real_name"),
                create_data.get("grade"),
                create_data.get("class_name"),
                create_data.get("avatar_url"),
            )
            existing = self.repos.user_details.create(create_data)
        
        return UserDetailsOut.model_validate(existing)

    @router.put("/me/details", response_model=UserDetailsOut)
    async def update_my_details(self, data: UserDetailsUpdate):
        """更新个人资料"""
        # 管理员的年级/班级固定为“管理员/老师”
        if self.user.admin:
            data.grade = self.ADMIN_GRADE
            data.class_name = self.ADMIN_CLASS_NAME

        # 获取现有资料
        user_details = self.repos.user_details.get_one(self.user.id, "user_id")
        if not user_details:
            create_data = data.model_dump(exclude_unset=True)
            fallback_real_name = (self.user.full_name or self.user.username or "").strip()
            real_name = (create_data.get("real_name") or fallback_real_name or "").strip()
            if not real_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="请先填写真实姓名"
                )

            user_details = self.repos.user_details.create({
                "user_id": self.user.id,
                "real_name": real_name,
                "grade": create_data.get("grade"),
                "class_name": create_data.get("class_name"),
                "avatar_url": create_data.get("avatar_url"),
                "is_complete": self._compute_is_complete(
                    real_name,
                    create_data.get("grade"),
                    create_data.get("class_name"),
                    create_data.get("avatar_url"),
                ),
            })

            return UserDetailsOut.model_validate(user_details)
        
        # 更新字段
        update_data = data.model_dump(exclude_unset=True)
        if not self.user.admin:
            self._enforce_grade_class_one_time_lock(user_details, update_data)
        for key, value in update_data.items():
            if value is not None:
                setattr(user_details, key, value)
        
        # 重新检查完整性
        self._sync_complete_status(user_details)
        self._persist_user_details(user_details)
        
        return UserDetailsOut.model_validate(user_details)

    @router.get("/me/details/check", response_model=UserDetailsCompleteCheck)
    async def check_profile_complete(self):
        """检查资料是否完善"""
        # 管理员始终视为已完善
        if self.user.admin:
            return UserDetailsCompleteCheck(
                is_complete=True,
                missing_fields=[],
                message=None,
            )

        # 仅学生需要强制完善资料，老师视为已完善
        is_student = self.user.role == UserRole.STUDENT or self.user.role is None
        if not is_student:
            return UserDetailsCompleteCheck(
                is_complete=True,
                missing_fields=[],
                message=None,
            )

        user_details = self.repos.user_details.get_one(self.user.id, "user_id")
        
        if not user_details:
            return UserDetailsCompleteCheck(
                is_complete=False,
                missing_fields=["real_name", "grade", "class_name", "avatar_url"],
                message="请完善个人资料（真实姓名、年级、班级、头像）"
            )

        # 与 require_complete_profile 使用同一套规则（strip 后非空）
        missing_fields = [
            field
            for field, value in [
                ("real_name", user_details.real_name),
                ("grade", user_details.grade),
                ("class_name", user_details.class_name),
                ("avatar_url", user_details.avatar_url),
            ]
            if not (value or "").strip()
        ]

        is_complete = self._compute_is_complete(
            user_details.real_name,
            user_details.grade,
            user_details.class_name,
            user_details.avatar_url,
        )

        # 自动修复历史脏数据：字段齐全但 is_complete 未同步
        if is_complete and not user_details.is_complete:
            user_details.is_complete = True
            # 这里直接使用 session 持久化，避免仓库 update 在部分作用域下查询不到记录
            self.session.add(user_details)
            self.session.commit()
        
        message = None
        if not is_complete:
            field_names = {
                "real_name": "真实姓名",
                "grade": "年级",
                "class_name": "班级",
                "avatar_url": "头像"
            }
            missing_names = [field_names.get(f, f) for f in missing_fields]
            message = f"请完善以下字段：{', '.join(missing_names)}"
        
        return UserDetailsCompleteCheck(
            is_complete=is_complete,
            missing_fields=missing_fields,
            message=message
        )

    @router.get("/{user_id}/details/public", response_model=UserDetailsPublic)
    async def get_user_details_public(self, user_id: UUID4):
        """获取用户公开资料（学生可见：姓名、年级、班级、头像）"""
        user_details = self.repos.user_details.get_one(user_id, "user_id")
        if not user_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户资料不存在"
            )
        
        return UserDetailsPublic(
            real_name=user_details.real_name,
            grade=user_details.grade,
            class_name=user_details.class_name,
            avatar_url=user_details.avatar_url
        )

    @router.get("/{user_id}/details", response_model=UserDetailsOut | None)
    async def get_user_details_admin(self, user_id: UUID4):
        """获取用户完整资料（仅管理员）"""
        # 检查权限：只有管理员可以查看完整资料
        if not self.user.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以查看完整资料"
            )
        
        user_details = self.repos.user_details.get_one(user_id, "user_id")
        if not user_details:
            return None
        
        return UserDetailsOut.model_validate(user_details)

    @router.put("/{user_id}/details", response_model=UserDetailsOut)
    async def update_user_details_admin(self, user_id: UUID4, data: UserDetailsUpdate):
        """管理员更新指定用户资料（年级、班级等）"""
        if not self.user.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以修改用户资料"
            )

        target_user = self.repos.users.get_one(user_id, "id")
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        user_details = self.repos.user_details.get_one(user_id, "user_id")
        update_data = data.model_dump(exclude_unset=True)

        # 被修改用户是管理员时，强制写入固定年级/班级
        if target_user.admin:
            update_data["grade"] = self.ADMIN_GRADE
            update_data["class_name"] = self.ADMIN_CLASS_NAME

        if not user_details:
            real_name = (update_data.get("real_name") or target_user.full_name or target_user.username or "").strip()
            if not real_name:
                real_name = str(target_user.email)

            user_details = self.repos.user_details.create({
                "user_id": user_id,
                "real_name": real_name,
                "grade": update_data.get("grade"),
                "class_name": update_data.get("class_name"),
                "avatar_url": update_data.get("avatar_url"),
                "is_complete": self._compute_is_complete(
                    real_name,
                    update_data.get("grade"),
                    update_data.get("class_name"),
                    update_data.get("avatar_url"),
                ),
            })
            return UserDetailsOut.model_validate(user_details)

        for key, value in update_data.items():
            if value is not None:
                setattr(user_details, key, value)

        self._sync_complete_status(user_details)
        self._persist_user_details(user_details)
        return UserDetailsOut.model_validate(user_details)
