"""用户详细资料路由"""
from fastapi import HTTPException, status
from pydantic import UUID4

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
        # 验证必填字段
        missing_fields = []
        if not data.real_name:
            missing_fields.append("real_name")
        if not data.grade:
            missing_fields.append("grade")
        if not data.class_name:
            missing_fields.append("class_name")
        if not data.avatar_url:
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
            for key, value in update_data.items():
                setattr(existing, key, value)
            existing.update_complete_status()
            self.repos.user_details.update(existing.id, existing)
        else:
            # 创建新资料
            create_data = data.model_dump()
            create_data["user_id"] = self.user.id
            existing = self.repos.user_details.create(create_data)
            existing.update_complete_status()
            self.repos.user_details.update(existing.id, existing)
        
        return UserDetailsOut.model_validate(existing)

    @router.put("/me/details", response_model=UserDetailsOut)
    async def update_my_details(self, data: UserDetailsUpdate):
        """更新个人资料"""
        # 获取现有资料
        user_details = self.repos.user_details.get_one(self.user.id, "user_id")
        if not user_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="请先完善个人资料"
            )
        
        # 更新字段
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(user_details, key, value)
        
        # 重新检查完整性
        user_details.update_complete_status()
        self.repos.user_details.update(user_details.id, user_details)
        
        return UserDetailsOut.model_validate(user_details)

    @router.get("/me/details/check", response_model=UserDetailsCompleteCheck)
    async def check_profile_complete(self):
        """检查资料是否完善"""
        user_details = self.repos.user_details.get_one(self.user.id, "user_id")
        
        if not user_details:
            return UserDetailsCompleteCheck(
                is_complete=False,
                missing_fields=["real_name", "grade", "class_name", "avatar_url"],
                message="请完善个人资料（真实姓名、年级、班级、头像）"
            )
        
        # 检查缺失字段
        missing_fields = []
        if not user_details.real_name:
            missing_fields.append("real_name")
        if not user_details.grade:
            missing_fields.append("grade")
        if not user_details.class_name:
            missing_fields.append("class_name")
        if not user_details.avatar_url:
            missing_fields.append("avatar_url")
        
        is_complete = len(missing_fields) == 0
        
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

    @router.get("/{user_id}/details", response_model=UserDetailsOut)
    async def get_user_details_admin(self, user_id: UUID4):
        """获取用户完整资料（仅管理员/老师）"""
        # 检查权限：只有管理员可以查看完整资料
        if not self.user.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以查看完整资料"
            )
        
        user_details = self.repos.user_details.get_one(user_id, "user_id")
        if not user_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户资料不存在"
            )
        
        return UserDetailsOut.model_validate(user_details)
