from pydantic import BaseModel, ConfigDict, Field

from mealie.schema._mealie import MealieModel

# TODO: Should these exist?!?!?!?!?


class RecipeSlug(MealieModel):
    slug: str


class SlugResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": "adult-mac-and-cheese"})


class UpdateImageResponse(BaseModel):
    image: str


class UpdateVideoResponse(BaseModel):
    video: str = Field(..., alias="videoUrl")


class RecipeDuplicate(BaseModel):
    name: str | None = None
