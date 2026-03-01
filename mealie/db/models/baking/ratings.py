"""食谱评分和评论模型"""
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text, UniqueConstraint, orm
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models._model_utils.auto_init import auto_init
from mealie.db.models._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..recipe import RecipeModel
    from ..users import User


class RecipeRating(SqlAlchemyBase, BaseMixins):
    """食谱评分和评论表（一个用户对一个食谱只能有一条评论）"""
    __tablename__ = "recipe_ratings"
    __table_args__ = (
        UniqueConstraint("recipe_id", "user_id", name="recipe_user_rating_unique"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="rating_range_check"),
    )
    
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    
    # 关联食谱
    recipe_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("recipes.id"), nullable=False, index=True)
    recipe: Mapped["RecipeModel"] = orm.relationship("RecipeModel", back_populates="ratings")
    
    # 关联用户
    user_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["User"] = orm.relationship("User", back_populates="recipe_ratings", foreign_keys=[user_id])
    
    # 评分和评论
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5星评分
    comment: Mapped[str | None] = mapped_column(Text)  # 文字评论
    
    # 关联信息
    group_id: AssociationProxy[GUID] = association_proxy("recipe", "group_id")
    household_id: AssociationProxy[GUID] = association_proxy("user", "household_id")
    
    @auto_init()
    def __init__(self, **_) -> None:
        pass
