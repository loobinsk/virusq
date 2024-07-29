import datetime
from typing import Literal, Tuple

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Security

from app.database.models import DailyRewardCompletition, User, DailyReward
from app.database.repositories.daily_reward import DailyRewardRepository
from app.database.repositories.user import UserRepository
from app.database.uow.base import BaseUoW
from app.exceptions.daily_reward import DailyRewardAlreadyClaimedError
from app.handlers.user.account import jwt_auth
from app.schemas.base import (
    ErrorResponse,
    UserEntity,
    DailyRewardEntity,
)
from app.schemas.general.auth import JWTValidationData
from app.schemas.user.daily_rewards import (
    GetAllDailyRewardsResponse,
    ClaimDailyRewardResponse,
    GetCurrentDailyRewardResponse,
)

daily_rewards_router = APIRouter(
    prefix="/rewards/daily",
    route_class=DishkaRoute,
)


@daily_rewards_router.get(
    "/getAll",
    responses={
        200: {"model": GetAllDailyRewardsResponse},
        401: {"model": ErrorResponse},
    },
    dependencies=[Security(jwt_auth)],
    tags=["Daily rewards actions"],
)
async def get_daily_rewards(
    daily_reward_repo: FromDishka[DailyRewardRepository],
):
    rewards = await daily_reward_repo.get_all()
    return GetAllDailyRewardsResponse(
        rewards=[DailyRewardEntity.from_daily_reward_model(reward) for reward in rewards]
    )


@daily_rewards_router.get(
    "/getCurrent",
    responses={
        200: {"model": GetCurrentDailyRewardResponse},
        401: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
    },
    dependencies=[Security(jwt_auth)],
    tags=["Daily rewards actions"],
)
async def get_current_daily_reward(
    daily_reward_repo: FromDishka[DailyRewardRepository],
    uow: FromDishka[BaseUoW],
    jwt_data: JWTValidationData = Security(jwt_auth),
):
    user = jwt_data.extra_data.user
    collected_daily_rewards = await daily_reward_repo.get_collected_daily_rewards(model_id=user.id)

    user.collected_daily_rewards = collected_daily_rewards  # type: ignore[assignment]

    reward, is_claimed = await _get_current_reward(
        user=user,
        daily_reward_repo=daily_reward_repo,
        action_type="getCurrent",
    )
    await uow.commit()

    return GetCurrentDailyRewardResponse(
        reward=DailyRewardEntity.from_daily_reward_model(reward),
        is_claimed=is_claimed,
    )


@daily_rewards_router.post(
    "/claim",
    responses={
        200: {"model": ClaimDailyRewardResponse},
        401: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
    },
    tags=["Daily rewards actions"],
)
async def claim_daily_reward(
    user_repo: FromDishka[UserRepository],
    daily_reward_repo: FromDishka[DailyRewardRepository],
    uow: FromDishka[BaseUoW],
    jwt_data: JWTValidationData = Security(jwt_auth),
):
    user = jwt_data.extra_data.user
    collected_daily_rewards = await daily_reward_repo.get_collected_daily_rewards(model_id=user.id)

    user.collected_daily_rewards = collected_daily_rewards  # type: ignore[assignment]

    reward, is_claimed = await _get_current_reward(
        user=user,
        daily_reward_repo=daily_reward_repo,
        action_type="claim",
    )

    if is_claimed:
        raise DailyRewardAlreadyClaimedError

    await daily_reward_repo.claim_daily_reward(
        user_id=user.id,
        daily_reward_id=reward.id,
    )
    await user_repo.claim_reward(
        user_id=user.id,
        reward=reward,
    )

    await uow.commit()
    return ClaimDailyRewardResponse(user=UserEntity.from_user_model(user))


async def _get_current_reward(
    user: User,
    daily_reward_repo: DailyRewardRepository,
    action_type: Literal["getCurrent", "claim"],
) -> Tuple[DailyReward, bool]:
    reward_day = 1
    is_claimed = False

    last_daily_reward = await daily_reward_repo.get_last_daily_reward()

    if len(user.collected_daily_rewards):
        last_collected_daily_reward: DailyRewardCompletition = max(
            user.collected_daily_rewards, key=lambda x: x.collected_at
        )
        current_date = datetime.datetime.utcnow().date()
        collected_at_date = last_collected_daily_reward.collected_at.date()

        if collected_at_date == current_date:
            is_claimed = True
            reward_day = last_collected_daily_reward.daily_reward.day
        elif current_date > collected_at_date + datetime.timedelta(days=1):
            if action_type == "claim":
                await daily_reward_repo.delete_collected_daily_rewards(user_id=user.id)
        elif last_daily_reward.id != last_collected_daily_reward.daily_reward_id:
            reward_day = last_collected_daily_reward.daily_reward.day + 1

    reward = await daily_reward_repo.get_by_reward_day(reward_day)
    return reward, is_claimed
