from typing import Sequence

from pydantic import BaseModel

from app.schemas.base import UserEntity, BonusTaskEntity


class GetUncompletedBonusTasksResponse(BaseModel):
    bonus_tasks: Sequence[BonusTaskEntity]


class ClaimBonusTaskInputData(BaseModel):
    bonus_task_id: int


class ClaimBonusTaskResponse(BaseModel):
    user: UserEntity
