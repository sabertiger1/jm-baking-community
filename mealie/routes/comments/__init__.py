from functools import cached_property

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from mealie.core.dependencies.dependencies import require_complete_profile
from mealie.db.models.baking.baking_records import UserBakingRecord
from mealie.db.models.recipe.comment import RecipeComment
from mealie.routes._base.base_controllers import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes._base.mixins import HttpRepo
from mealie.schema.recipe.recipe_comments import (
    RecipeCommentCreate,
    RecipeCommentOut,
    RecipeCommentPagination,
    RecipeCommentSave,
    RecipeCommentUpdate,
)
from mealie.schema.response.pagination import PaginationQuery
from mealie.schema.response.responses import ErrorResponse, SuccessResponse

router = APIRouter(prefix="/comments", tags=["Recipe: Comments"])


@controller(router)
class RecipeCommentRoutes(BaseUserController):
    @cached_property
    def repo(self):
        return self.repos.comments

    # =======================================================================
    # CRUD Operations

    @property
    def mixins(self) -> HttpRepo:
        return HttpRepo(self.repo, self.logger, self.registered_exceptions, self.t("generic.server-error"))

    def _check_comment_belongs_to_user(self, item_id: UUID4) -> None:
        comment = self.repo.get_one(item_id)
        if comment.user_id != self.user.id and not self.user.admin:
            raise HTTPException(
                status_code=403,
                detail=ErrorResponse(message="Comment does not belong to user"),
            )

    @router.get("", response_model=RecipeCommentPagination)
    def get_all(self, q: PaginationQuery = Depends(PaginationQuery)):
        response = self.repo.page_all(
            pagination=q,
            override=RecipeCommentOut,
        )

        response.set_pagination_guides(router.url_path_for("get_all"), q.model_dump())
        return response

    @router.post("", response_model=RecipeCommentOut, status_code=201, dependencies=[Depends(require_complete_profile)])
    def create_one(self, data: RecipeCommentCreate):
        content = (data.text or "").strip()
        if len(content) < 5:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse.respond(message="评论不能少于5字"),
            )

        user_rating = self.repos.user_ratings.get_by_user_and_recipe(self.user.id, data.recipe_id)
        if not user_rating or not user_rating.rating or user_rating.rating <= 0:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse.respond(message="发表评论前必须先完成星级评分"),
            )

        made_record = (
            self.session.query(UserBakingRecord)
            .filter(UserBakingRecord.recipe_id == data.recipe_id, UserBakingRecord.user_id == self.user.id)
            .first()
        )
        if not made_record:
            raise HTTPException(
                status_code=403,
                detail=ErrorResponse.respond(message="请先提交该配方作品后再进行评论"),
            )

        existing = (
            self.session.query(RecipeComment)
            .filter(RecipeComment.recipe_id == data.recipe_id, RecipeComment.user_id == self.user.id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse.respond(message="您已经评价过该配方，每个用户只能评价一次"),
            )

        save_data = RecipeCommentSave(text=content, user_id=self.user.id, recipe_id=data.recipe_id)
        return self.mixins.create_one(save_data)

    @router.get("/{item_id}", response_model=RecipeCommentOut)
    def get_one(self, item_id: UUID4):
        return self.mixins.get_one(item_id)

    @router.put("/{item_id}", response_model=RecipeCommentOut)
    def update_one(self, item_id: UUID4, data: RecipeCommentUpdate):
        if not self.user.admin:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse.respond(message="评论提交后不可修改"),
            )
        return self.mixins.update_one(data, item_id)

    @router.delete("/{item_id}", response_model=SuccessResponse)
    def delete_one(self, item_id: UUID4):
        if not self.user.admin:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse.respond(message="评论提交后不可删除"),
            )
        self.mixins.delete_one(item_id)
        return SuccessResponse.respond(message="Comment deleted")
