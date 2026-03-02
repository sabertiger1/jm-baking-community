"""作品投票记录模型（送花/送鸡蛋）"""
import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum, ForeignKey, Integer, UniqueConstraint, orm
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models._model_utils.auto_init import auto_init
from mealie.db.models._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..users import User


class VoteType(enum.Enum):
    """投票类型"""
    FLOWER = "flower"  # 送花
    EGG = "egg"  # 送鸡蛋


class WorkVote(SqlAlchemyBase, BaseMixins):
    """作品投票记录表（一个用户对一个作品每种类型只能投一次）"""
    __tablename__ = "work_votes"
    __table_args__ = (
        UniqueConstraint("work_id", "user_id", "vote_type", name="work_user_vote_type_unique"),
    )
    
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    
    # 关联作品
    work_id: Mapped[GUID] = mapped_column(
        GUID, ForeignKey("user_baking_records.id"), nullable=False, index=True
    )
    work: Mapped["UserBakingRecord"] = orm.relationship(
        "UserBakingRecord", back_populates="votes", foreign_keys=[work_id]
    )
    
    # 关联用户（投票者）
    user_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["User"] = orm.relationship("User", back_populates="work_votes", foreign_keys=[user_id])
    
    # 投票类型
    # 说明：
    # - 早期数据库中该字段以字符串形式存储为 "flower"/"egg"
    # - 这里通过 values_callable 显式指定使用 Enum.value（小写字符串）作为持久化值
    #   避免 SQLAlchemy 默认使用枚举名称 "FLOWER"/"EGG" 导致 LookupError
    vote_type: Mapped[VoteType] = mapped_column(
        SQLEnum(
            VoteType,
            values_callable=lambda x: [e.value for e in x],
            name="votetype",
        ),
        nullable=False,
        index=True,
    )
    
    # 关联信息
    group_id: AssociationProxy[GUID] = association_proxy("work", "group_id")
    household_id: AssociationProxy[GUID] = association_proxy("user", "household_id")
    
    @auto_init()
    def __init__(self, **_) -> None:
        pass
