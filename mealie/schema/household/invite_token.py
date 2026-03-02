from uuid import UUID

from pydantic import ConfigDict
from typing import Literal

from mealie.schema._mealie import MealieModel


class CreateInviteToken(MealieModel):
    uses: int
    group_id: UUID | None = None
    household_id: UUID | None = None


class SaveInviteToken(MealieModel):
    uses_left: int
    group_id: UUID
    household_id: UUID
    token: str


class ReadInviteToken(MealieModel):
    token: str
    uses_left: int
    group_id: UUID
    household_id: UUID
    model_config = ConfigDict(from_attributes=True)


class EmailInvitation(MealieModel):
    email: str
    token: str
    invite_role: Literal["student"] | None = None


class EmailInitationResponse(MealieModel):
    success: bool
    error: str | None = None
