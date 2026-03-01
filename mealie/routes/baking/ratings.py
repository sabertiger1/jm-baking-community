"""食谱评分和评论路由"""
from collections import Counter

from fastapi import Depends, HTTPException, status
from pydantic import UUID4
from sqlalchemy import and_, func, select
from sqlalchemy.orm import joinedload

from mealie.core.dependencies.dependencies import require_complete_profile
from mealie.db.models.baking.ratings import RecipeRating
from mealie.db.models.users.user_details import UserDetails
from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.baking.ratings import (
    RecipeRatingCreate,
    RecipeRatingOut,
    RecipeRatingSummary,
    RecipeRatingUpdate,
)

router = UserAPIRouter()


@controller(router)
class RecipeRatingsController(BaseUserController):
    @router.post("/{recipe_id}/ratings", response_model=RecipeRatingOut, status_code=201, dependencies=[Depends(require_complete_profile)])
    async def create_rating(self, recipe_id: UUID4, data: RecipeRatingCreate):
        """创建评分和评论（需要完善资料，一个用户对一个食谱只能有一条）"""
        # 1. 验证食谱存在
        recipe = self.repos.recipes.get_one(recipe_id, "id")
        if not recipe:
            raise HTTPException(status_code=404, detail="食谱不存在")

        # 2. 检查是否已存在评分（确保唯一性）
        existing_rating = (
            self.session.query(RecipeRating)
            .filter(and_(RecipeRating.recipe_id == recipe_id, RecipeRating.user_id == self.user.id))
            .first()
        )
        if existing_rating:
            raise HTTPException(
                status_code=400, detail="您已经对该食谱进行过评分，只能修改不能重复创建"
            )

        # 3. 创建新评分
        rating_data = data.model_dump()
        rating_data["recipe_id"] = recipe_id
        rating_data["user_id"] = self.user.id

        rating = self.repos.recipe_ratings.create(rating_data)
        return self._enrich_rating(rating)

    @router.put("/{recipe_id}/ratings/{rating_id}", response_model=RecipeRatingOut)
    async def update_rating(self, recipe_id: UUID4, rating_id: UUID4, data: RecipeRatingUpdate):
        """更新评分和评论（只能更新自己的）"""
        # 验证评分存在
        rating = self.repos.recipe_ratings.get_one(rating_id, "id")
        if not rating:
            raise HTTPException(status_code=404, detail="评分不存在")

        # 验证属于当前用户
        if rating.user_id != self.user.id:
            raise HTTPException(status_code=403, detail="只能修改自己的评分")

        # 验证属于指定食谱
        if rating.recipe_id != recipe_id:
            raise HTTPException(status_code=400, detail="评分与食谱不匹配")

        # 更新评分
        updated = self.repos.recipe_ratings.update(rating_id, data.model_dump(exclude_unset=True))
        return self._enrich_rating(updated)

    @router.get("/{recipe_id}/ratings", response_model=list[RecipeRatingOut])
    async def get_recipe_ratings(self, recipe_id: UUID4):
        """获取食谱的所有评分和评论"""
        ratings = self.repos.recipe_ratings.multi_query({"recipe_id": recipe_id})
        return [self._enrich_rating(rating) for rating in ratings]

    @router.get("/{recipe_id}/ratings/summary", response_model=RecipeRatingSummary)
    async def get_rating_summary(self, recipe_id: UUID4):
        """获取评分统计信息"""
        # 获取所有评分
        ratings = (
            self.session.query(RecipeRating.rating)
            .filter(RecipeRating.recipe_id == recipe_id)
            .all()
        )

        if not ratings:
            return RecipeRatingSummary(
                recipe_id=recipe_id,
                average_rating=None,
                total_ratings=0,
                rating_distribution={},
            )

        rating_values = [r[0] for r in ratings if r[0] is not None]
        if not rating_values:
            return RecipeRatingSummary(
                recipe_id=recipe_id,
                average_rating=None,
                total_ratings=len(ratings),
                rating_distribution={},
            )

        # 计算平均分
        average_rating = sum(rating_values) / len(rating_values)

        # 计算分布
        distribution = Counter(rating_values)
        rating_distribution = {i: distribution.get(i, 0) for i in range(1, 6)}

        return RecipeRatingSummary(
            recipe_id=recipe_id,
            average_rating=round(average_rating, 2),
            total_ratings=len(rating_values),
            rating_distribution=rating_distribution,
        )

    @router.get("/{recipe_id}/ratings/my", response_model=RecipeRatingOut | None)
    async def get_my_rating(self, recipe_id: UUID4):
        """获取当前用户对该食谱的评分"""
        rating = (
            self.session.query(RecipeRating)
            .filter(and_(RecipeRating.recipe_id == recipe_id, RecipeRating.user_id == self.user.id))
            .first()
        )

        if not rating:
            return None

        return self._enrich_rating_model(rating)

    def _enrich_rating(self, rating: RecipeRatingOut) -> RecipeRatingOut:
        """丰富评分信息"""
        rating_model = self.session.get(RecipeRating, rating.id) if hasattr(rating, "id") else None
        return self._enrich_rating_model(rating_model) if rating_model else rating

    def _enrich_rating_model(self, rating: RecipeRating) -> RecipeRatingOut:
        """从模型丰富评分信息"""
        if not rating:
            raise HTTPException(status_code=404, detail="评分不存在")

        # 获取用户详细信息
        user_details = self.session.query(UserDetails).filter(UserDetails.user_id == rating.user_id).first()

        rating_dict = {
            "id": rating.id,
            "recipe_id": rating.recipe_id,
            "user_id": rating.user_id,
            "rating": rating.rating,
            "comment": rating.comment,
            "created_at": rating.created_at,
            "update_at": rating.update_at,
            "user_name": rating.user.username if rating.user else None,
            "user_full_name": rating.user.full_name if rating.user else None,
            "avatar_url": user_details.avatar_url if user_details else None,
            "class_name": user_details.class_name if user_details else None,
            "grade": user_details.grade if user_details else None,
        }

        return RecipeRatingOut(**rating_dict)
