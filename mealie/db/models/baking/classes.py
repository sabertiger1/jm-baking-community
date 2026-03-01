"""用户班级和小组模型"""
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, orm
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models._model_utils.auto_init import auto_init
from mealie.db.models._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..users import User


class UserClass(SqlAlchemyBase, BaseMixins):
    """用户班级和小组信息表（可选扩展，每个用户一条记录）"""
    __tablename__ = "user_classes"
    
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    
    # 关联用户（唯一）
    user_id: Mapped[GUID] = mapped_column(
        GUID, ForeignKey("users.id"), nullable=False, unique=True, index=True
    )
    user: Mapped["User"] = orm.relationship("User", back_populates="user_class", uselist=False, foreign_keys=[user_id])
    
    # 班级和小组信息
    class_name: Mapped[str | None] = mapped_column(String, index=True)  # 班级名称
    group_name: Mapped[str | None] = mapped_column(String, index=True)  # 小组名称
    
    # 关联信息
    group_id: AssociationProxy[GUID] = association_proxy("user", "group_id")
    household_id: AssociationProxy[GUID] = association_proxy("user", "household_id")
    
    @auto_init()
    def __init__(self, **_) -> None:
        pass
