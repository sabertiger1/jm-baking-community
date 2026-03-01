"""用户详细资料模型"""
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, orm
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models._model_utils.auto_init import auto_init
from mealie.db.models._model_utils.guid import GUID

if TYPE_CHECKING:
    from .users import User


class UserDetails(SqlAlchemyBase, BaseMixins):
    """用户详细资料表（每个用户一条记录，必须完善）"""
    __tablename__ = "user_details"
    
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    
    # 关联用户（唯一）
    user_id: Mapped[GUID] = mapped_column(
        GUID, ForeignKey("users.id"), nullable=False, unique=True, index=True
    )
    user: Mapped["User"] = orm.relationship("User", back_populates="user_details", uselist=False, foreign_keys=[user_id])
    
    # 必填信息
    real_name: Mapped[str] = mapped_column(String, nullable=False, index=True)  # 真实姓名（不允许假名）
    grade: Mapped[str | None] = mapped_column(String, index=True)  # 年级（如：2024级）
    class_name: Mapped[str | None] = mapped_column(String, index=True)  # 班级（如：烘焙1班）
    avatar_url: Mapped[str | None] = mapped_column(String)  # 头像URL（必须上传）
    
    # 资料完善状态
    is_complete: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)  # 资料是否完善
    
    # 关联信息
    group_id: AssociationProxy[GUID] = association_proxy("user", "group_id")
    household_id: AssociationProxy[GUID] = association_proxy("user", "household_id")
    
    @auto_init()
    def __init__(self, **_) -> None:
        pass
    
    def check_complete(self) -> bool:
        """检查资料是否完善（真实姓名、年级、班级、头像都必须有）"""
        return bool(
            self.real_name and 
            self.grade and 
            self.class_name and 
            self.avatar_url
        )
    
    def update_complete_status(self):
        """更新完善状态"""
        self.is_complete = self.check_complete()
