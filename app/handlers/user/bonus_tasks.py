from contextlib import suppress

from aiohttp import ClientSession, ClientResponseError
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Security

from app.config import config
from app.database.models import BonusTask, User
from app.database.repositories.bonus_task import BonusTaskRepository
from app.database.repositories.user import UserRepository
from app.database.uow.base import BaseUoW
from app.exceptions.bonus_tasks import BonusTaskUncompletedError
from app.handlers.user.account import jwt_auth
from app.schemas.base import (
    ErrorResponse,
    BonusTaskEntity,
    UserEntity,
)
from app.schemas.general.auth import JWTValidationData
from app.schemas.user.bonus_tasks import (
    GetUncompletedBonusTasksResponse,
    ClaimBonusTaskResponse,
    ClaimBonusTaskInputData,
)
from app.typings.enums import BonusTaskType

bonus_tasks_router = APIRouter(
    prefix="/bonusTasks",
    route_class=DishkaRoute,
)


@bonus_tasks_router.get(
    "/getUncompleted",
    responses={
        200: {"model": GetUncompletedBonusTasksResponse},
        401: {"model": ErrorResponse},
    },
    summary="Get uncompleted bonus tasks",
    tags=["Bonus tasks actions"],
)
async def get_uncompleted_bonus_tasks(
    bonus_task_repo: FromDishka[BonusTaskRepository],
    jwt_data: JWTValidationData = Security(jwt_auth),
):
    uncompleted_bonus_tasks = await bonus_task_repo.get_uncompleted_tasks(
        user_id=jwt_data.parsed_data.user_id
    )
    return GetUncompletedBonusTasksResponse(
        bonus_tasks=[
            BonusTaskEntity.from_bonus_task_model(bonus_task)
            for bonus_task in uncompleted_bonus_tasks
        ]
    )


@bonus_tasks_router.post(
    "/claim",
    responses={
        200: {"model": ClaimBonusTaskResponse},
        401: {"model": ErrorResponse},
    },
    summary="Claim bonus task completition",
    tags=["Bonus tasks actions"],
)
async def claim_bonus_task(
    bonus_task_repo: FromDishka[BonusTaskRepository],
    user_repo: FromDishka[UserRepository],
    uow: FromDishka[BaseUoW],
    data: ClaimBonusTaskInputData,
    jwt_data: JWTValidationData = Security(jwt_auth),
):
    user_id = jwt_data.parsed_data.user_id

    bonus_task = await bonus_task_repo.get_uncompleted_task_by_id(
        user_id=user_id,
        bonus_task_id=data.bonus_task_id,
    )
    is_completed = await check_bonus_task_completition(bonus_task=bonus_task, user_id=user_id)

    if not is_completed:
        raise BonusTaskUncompletedError

    await bonus_task_repo.set_bonus_task_completed(
        user_id=user_id,
        bonus_task_id=bonus_task.id,
    )

    user = await user_repo.update_one_by_id(
        model_id=user_id,
        balance=User.balance + bonus_task.reward_amount,
        daily_overall_profit=User.daily_overall_profit + bonus_task.reward_amount,
    )

    await uow.commit()
    return ClaimBonusTaskResponse(user=UserEntity.from_user_model(user))


async def check_bonus_task_completition(bonus_task: BonusTask, user_id: int) -> bool:
    BASE_URL = "https://api.telegram.org/bot"

    session = ClientSession(
        raise_for_status=True,
    )
    result = False

    match bonus_task.task_type:
        case BonusTaskType.TG_CHANNEL:
            with suppress(ClientResponseError):
                response = await session.post(
                    f"{BASE_URL}{config.app.telegram_bot_token}/getChatMember",
                    data={"chat_id": bonus_task.access_id, "user_id": user_id},
                )
                json_data = await response.json()
                result = bool(json_data["result"]["status"] not in {"left", "kicked", "restricted"})
        case BonusTaskType.TG_BOT:
            with suppress(ClientResponseError):
                await session.post(
                    f"{BASE_URL}{bonus_task.access_data}/sendChatAction",
                    data={"chat_id": bonus_task.access_id, "action": "typing"},
                )
                result = True
        case BonusTaskType.UNSPECIFIED:
            result = True

    await session.close()
    return result
