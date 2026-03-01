"""用户积分模型"""
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, orm
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models._model_utils.auto_init import auto_init
from mealie.db.models._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..users import User


class UserPoints(SqlAlchemyBase, BaseMixins):
    """用户积分表（每个用户一条记录）"""
    __tablename__ = "user_points"
    
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    
    # 关联用户（唯一）
    user_id: Mapped[GUID] = mapped_column(
        GUID, ForeignKey("users.id"), nullable=False, unique=True, index=True
    )
    user: Mapped["User"] = orm.relationship("User", back_populates="points", uselist=False, foreign_keys=[user_id])
    
    # 积分信息
    total_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 总积分
    consecutive_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 连续签到天数
    last_checkin_date: Mapped[str | None] = mapped_column(String)  # 最后签到日期（YYYY-MM-DD格式）
    
    # 关联信息
    group_id: AssociationProxy[GUID] = association_proxy("user", "group_id")
    household_id: AssociationProxy[GUID] = association_proxy("user", "household_id")
    
    @auto_init()
    def __init__(self, **_) -> None:
        pass
