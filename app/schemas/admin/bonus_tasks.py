from typing import Sequence

from pydantic import BaseModel

from app.schemas.base import AdminBonusTaskEntity
from app.typings.enums import BonusTaskType


class CreateBonusTaskInputData(BaseModel):
    access_id: int | None
    name: str
    task_type: BonusTaskType
    description: str
    photo: bytes
    link: str
    reward_amount: int
    access_data: str | None = None


class CreateBonusTaskResponse(BaseModel):
    bonus_task: AdminBonusTaskEntity


class GetBonusTaskByIdResponse(BaseModel):
    bonus_task: AdminBonusTaskEntity


class GetAllBonusTasksResponse(BaseModel):
    bonus_tasks: Sequence[AdminBonusTaskEntity]


class UpdateBonusTaskInputData(BaseModel):
    id: int
    name: str | None = None
    description: str | None = None
    photo: bytes | None = None
    link: str | None = None
    reward_amount: int | None = None
    access_id: int | None = None
    access_data: str | None = None


class UpdateBonusTaskResponse(BaseModel):
    bonus_task: AdminBonusTaskEntity


class DeleteBonusTaskResponse(BaseModel):
    bonus_task: AdminBonusTaskEntity
