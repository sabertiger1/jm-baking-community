"""用户详细资料 Schema"""
from datetime import datetime

from pydantic import UUID4, Field, field_validator

from mealie.schema._mealie import MealieModel


class UserDetailsBase(MealieModel):
    """用户资料基础 Schema"""
    real_name: str = Field(..., min_length=1, max_length=50, description="真实姓名（不允许假名、昵称）")
    grade: str | None = Field(None, max_length=20, description="年级（如：2024级）")
    class_name: str | None = Field(None, max_length=50, description="班级（如：烘焙1班）")
    avatar_url: str | None = Field(None, description="头像URL（必须上传）")
    
    @field_validator("real_name")
    @classmethod
    def validate_real_name(cls, v: str) -> str:
        """验证真实姓名（不允许明显的假名、昵称）"""
        v = v.strip()
        if not v:
            raise ValueError("真实姓名不能为空")
        # 可以添加更多验证规则，如不允许特殊字符、数字等
        if len(v) < 2:
            raise ValueError("真实姓名至少需要2个字符")
        return v


class UserDetailsCreate(UserDetailsBase):
    """创建用户资料 Schema"""
    user_id: UUID4


class UserDetailsUpdate(MealieModel):
    """更新用户资料 Schema"""
    real_name: str | None = Field(None, min_length=1, max_length=50)
    grade: str | None = Field(None, max_length=20)
    class_name: str | None = Field(None, max_length=50)
    avatar_url: str | None = None


class UserDetailsOut(UserDetailsBase):
    """用户资料输出 Schema"""
    id: UUID4
    user_id: UUID4
    is_complete: bool = Field(description="资料是否完善")
    created_at: datetime
    update_at: datetime
    
    model_config = {"from_attributes": True}


class UserDetailsPublic(MealieModel):
    """用户资料公开信息（学生可见）"""
    real_name: str = Field(description="真实姓名")
    grade: str | None = Field(None, description="年级")
    class_name: str | None = Field(None, description="班级")
    avatar_url: str | None = Field(None, description="头像URL")
    
    model_config = {"from_attributes": True}


class UserDetailsCompleteCheck(MealieModel):
    """资料完整性检查响应"""
    is_complete: bool = Field(description="资料是否完善")
    missing_fields: list[str] = Field(default_factory=list, description="缺失的必填字段")
    message: str | None = Field(None, description="提示信息")


class CompleteProfileRequest(UserDetailsBase):
    """完善资料请求（首次登录强制完善）"""
    pass
