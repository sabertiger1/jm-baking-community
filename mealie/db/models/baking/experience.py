"""用户经验值模型"""
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, orm
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models._model_utils.auto_init import auto_init
from mealie.db.models._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..users import User


class UserExperience(SqlAlchemyBase, BaseMixins):
    """用户经验值（每个用户一条）"""

    __tablename__ = "user_experience"

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    user_id: Mapped[GUID] = mapped_column(
        GUID, ForeignKey("users.id"), nullable=False, unique=True, index=True
    )
    user: Mapped["User"] = orm.relationship("User", back_populates="experience", uselist=False, foreign_keys=[user_id])

    total_exp: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    group_id: AssociationProxy[GUID] = association_proxy("user", "group_id")
    household_id: AssociationProxy[GUID] = association_proxy("user", "household_id")

    @auto_init()
    def __init__(self, **_) -> None:
        pass
