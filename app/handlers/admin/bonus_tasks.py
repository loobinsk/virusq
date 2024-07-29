from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Security, Body

from app.database.models import BonusTask
from app.database.repositories.bonus_task import BonusTaskRepository
from app.database.uow.base import BaseUoW
from app.handlers.user.account import bot_jwt_auth
from app.schemas.admin.bonus_tasks import (
    CreateBonusTaskResponse,
    CreateBonusTaskInputData,
    UpdateBonusTaskInputData,
    UpdateBonusTaskResponse,
    DeleteBonusTaskResponse,
    GetBonusTaskByIdResponse,
    GetAllBonusTasksResponse,
)
from app.schemas.base import (
    ErrorResponse,
    AdminBonusTaskEntity,
)

admin_bonus_tasks_router = APIRouter(
    prefix="/bonusTasks",
    route_class=DishkaRoute,
)


@admin_bonus_tasks_router.post(
    "/create",
    responses={
        200: {"model": CreateBonusTaskResponse},
        401: {"model": ErrorResponse},
    },
    include_in_schema=False,
    dependencies=[Security(bot_jwt_auth)],
    summary="Create bonus task",
    tags=["Bonus tasks actions"],
)
async def create_bonus_task(
    bonus_task_repo: FromDishka[BonusTaskRepository],
    uow: FromDishka[BaseUoW],
    data: CreateBonusTaskInputData,
):
    bonus_task = await bonus_task_repo.create(
        bonus_task=BonusTask(**data.model_dump(exclude_none=True))
    )

    await uow.commit()
    return CreateBonusTaskResponse(
        bonus_task=AdminBonusTaskEntity.from_bonus_task_model(bonus_task)
    )


@admin_bonus_tasks_router.post(
    "/update",
    dependencies=[Security(bot_jwt_auth)],
    responses={
        200: {"model": UpdateBonusTaskResponse},
        401: {"model": ErrorResponse},
    },
    include_in_schema=False,
    summary="Update bonus task",
    tags=["Bonus tasks actions"],
)
async def update_bonus_task(
    bonus_task_repo: FromDishka[BonusTaskRepository],
    uow: FromDishka[BaseUoW],
    data: UpdateBonusTaskInputData,
):
    bonus_task = await bonus_task_repo.update_by_id(
        model_id=data.id,
        **data.model_dump(exclude_none=True, exclude={"id"}),
    )
    await uow.commit()

    return CreateBonusTaskResponse(
        bonus_task=AdminBonusTaskEntity.from_bonus_task_model(bonus_task),
    )


@admin_bonus_tasks_router.get(
    "/getAll",
    dependencies=[Security(bot_jwt_auth)],
    responses={
        200: {"model": GetAllBonusTasksResponse},
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Get Bonus Task By Id",
    tags=["Bonus Tasks Actions"],
    include_in_schema=False,
)
async def get_all_bonus_tasks(bonus_task_repo: FromDishka[BonusTaskRepository]):
    bonus_tasks = await bonus_task_repo.get_all()

    return GetAllBonusTasksResponse(
        bonus_tasks=[
            AdminBonusTaskEntity.from_bonus_task_model(bonus_task) for bonus_task in bonus_tasks
        ],
    )


@admin_bonus_tasks_router.get(
    "/getById",
    dependencies=[Security(bot_jwt_auth)],
    responses={
        200: {"model": GetBonusTaskByIdResponse},
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Get Bonus Task By Id",
    tags=["Bonus Tasks Actions"],
    include_in_schema=False,
)
async def get_bonus_task_by_id(
    bonus_task_repo: FromDishka[BonusTaskRepository],
    id: int,
):
    bonus_task = await bonus_task_repo.get_by_id(bonus_task_id=id)

    return GetBonusTaskByIdResponse(
        bonus_task=AdminBonusTaskEntity.from_bonus_task_model(bonus_task)
    )


@admin_bonus_tasks_router.delete(
    "/delete",
    dependencies=[Security(bot_jwt_auth)],
    responses={
        200: {"model": DeleteBonusTaskResponse},
    },
    include_in_schema=False,
    summary="Delete bonus task",
    tags=["Bonus tasks actions"],
)
async def delete_bonus_task(
    bonus_task_repo: FromDishka[BonusTaskRepository],
    uow: FromDishka[BaseUoW],
    id: int = Body(embed=True),
):
    bonus_task = await bonus_task_repo.delete_by_id(bonus_task_id=id)
    await uow.commit()

    return DeleteBonusTaskResponse(
        bonus_task=AdminBonusTaskEntity.from_bonus_task_model(bonus_task)
    )
