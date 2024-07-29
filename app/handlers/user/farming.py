from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Security

from app.database.repositories.user import UserRepository
from app.database.uow.base import BaseUoW
from app.handlers.user.account import jwt_auth
from app.schemas.base import UserEntity, ErrorResponse
from app.schemas.general.auth import JWTValidationData
from app.schemas.user.farming import (
    FarmingClaimResponse,
    FarmingStartResponse,
)

farming_router = APIRouter(prefix="/farming", route_class=DishkaRoute)


@farming_router.post(
    "/start",
    responses={
        200: {"model": FarmingStartResponse},
        401: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
    },
    summary="Start Farming",
    tags=["Farming actions"],
)
async def start_farming_handler(
    user_repo: FromDishka[UserRepository],
    uow: FromDishka[BaseUoW],
    jwt_data: JWTValidationData = Security(jwt_auth),
):
    user = await user_repo.start_farming(model_id=jwt_data.parsed_data.user_id)
    await uow.commit()

    return FarmingStartResponse(user=UserEntity.from_user_model(user))


@farming_router.post(
    "/collect",
    responses={
        200: {"model": FarmingClaimResponse},
        401: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
    },
    summary="Claim Farming",
    tags=["Farming actions"],
)
async def claim_farming_handler(
    user_repo: FromDishka[UserRepository],
    uow: FromDishka[BaseUoW],
    jwt_data: JWTValidationData = Security(jwt_auth),
):
    user = await user_repo.claim_farming(model_id=jwt_data.parsed_data.user_id)
    await user_repo.reward_user_referrers(
        user_id=jwt_data.parsed_data.user_id,
        initial_profit=user.farming_total_profit,
    )

    await uow.commit()

    return FarmingClaimResponse(user=UserEntity.from_user_model(user))
