"""用户烘焙作品记录模型"""
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text, orm
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models._model_utils.auto_init import auto_init
from mealie.db.models._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..recipe import RecipeModel
    from ..users import User
    from .votes import WorkVote


class UserBakingRecord(SqlAlchemyBase, BaseMixins):
    """用户烘焙作品记录表"""
    __tablename__ = "user_baking_records"
    
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    
    # 关联食谱
    recipe_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("recipes.id"), nullable=False, index=True)
    recipe: Mapped["RecipeModel"] = orm.relationship("RecipeModel", back_populates="baking_records")
    
    # 关联用户
    user_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["User"] = orm.relationship("User", back_populates="baking_records", foreign_keys=[user_id])
    
    # 作品信息
    image_url: Mapped[str] = mapped_column(String, nullable=False)  # 成品图片URL
    notes: Mapped[str | None] = mapped_column(Text)  # 制作心得
    
    # 统计信息（冗余字段，提高查询性能）
    flower_count: Mapped[int] = mapped_column(Integer, default=0, index=True)  # 鲜花数
    egg_count: Mapped[int] = mapped_column(Integer, default=0, index=True)  # 鸡蛋数
    
    # 关联信息（通过association_proxy获取）
    group_id: AssociationProxy[GUID] = association_proxy("recipe", "group_id")
    household_id: AssociationProxy[GUID] = association_proxy("user", "household_id")
    
    # 投票关系
    votes: Mapped[list["WorkVote"]] = orm.relationship(
        "WorkVote", back_populates="work", cascade="all, delete, delete-orphan"
    )
    
    @auto_init()
    def __init__(self, **_) -> None:
        pass
