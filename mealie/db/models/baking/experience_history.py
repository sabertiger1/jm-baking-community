"""用户经验变动历史模型"""
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text, orm
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models._model_utils.auto_init import auto_init
from mealie.db.models._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..users import User


class UserExperienceHistory(SqlAlchemyBase, BaseMixins):
    """用户经验变动历史（事件流水）"""

    __tablename__ = "user_experience_history"

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    user_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["User"] = orm.relationship(
        "User", back_populates="experience_history", foreign_keys=[user_id]
    )

    source: Mapped[str] = mapped_column(String, nullable=False, index=True)
    exp_delta: Mapped[int] = mapped_column(Integer, nullable=False)
    total_exp_after: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[str | None] = mapped_column(Text)

    group_id: AssociationProxy[GUID] = association_proxy("user", "group_id")
    household_id: AssociationProxy[GUID] = association_proxy("user", "household_id")

    @auto_init()
    def __init__(self, **_) -> None:
        pass
