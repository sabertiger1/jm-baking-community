"""用户签到历史模型"""
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint, orm
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models._model_utils.auto_init import auto_init
from mealie.db.models._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..users import User


class UserCheckinHistory(SqlAlchemyBase, BaseMixins):
    """用户每日签到历史（每天一条）"""

    __tablename__ = "user_checkin_history"
    __table_args__ = (
        UniqueConstraint("user_id", "checkin_date", name="user_checkin_date_unique"),
    )

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    user_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["User"] = orm.relationship("User", back_populates="checkin_history", foreign_keys=[user_id])

    # YYYY-MM-DD
    checkin_date: Mapped[str] = mapped_column(String, nullable=False, index=True)

    group_id: AssociationProxy[GUID] = association_proxy("user", "group_id")
    household_id: AssociationProxy[GUID] = association_proxy("user", "household_id")

    @auto_init()
    def __init__(self, **_) -> None:
        pass
