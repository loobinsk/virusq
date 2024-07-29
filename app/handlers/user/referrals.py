from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Security

from app.database.repositories.user import UserRepository
from app.database.uow.base import BaseUoW
from app.handlers.user.account import jwt_auth
from app.schemas.base import ErrorResponse, UserEntity
from app.schemas.general.auth import JWTValidationData
from app.schemas.user.referrals import (
    ReferralsStatsResponse,
    ReferralsStatsLevel,
    ReferralsClaimProfitResponse,
)

referrals_router = APIRouter(prefix="/referrals", route_class=DishkaRoute)


@referrals_router.get(
    "/stats",
    responses={
        200: {"model": ReferralsStatsResponse},
        401: {"model": ErrorResponse},
    },
    summary="Referrals stats",
    tags=["Referrals actions"],
)
async def get_referrals_stats_handler(
    user_repo: FromDishka[UserRepository],
    jwt_data: JWTValidationData = Security(jwt_auth),
):
    referrals_stats = await user_repo.get_referrals_stats(model_id=jwt_data.parsed_data.user_id)

    return ReferralsStatsResponse(
        levels=[
            ReferralsStatsLevel(
                referrals_amount=referrals_amount,
                referrals_profit=referrals_profit,
                level=level,
            )
            for referrals_amount, referrals_profit, level in referrals_stats
        ]
    )


@referrals_router.post(
    "/claimProfit",
    responses={
        200: {"model": ReferralsClaimProfitResponse},
        401: {"model": ErrorResponse},
    },
    summary="Claim referral profit",
    tags=["Referrals actions"],
)
async def referrals_claim_profit_handler(
    user_repo: FromDishka[UserRepository],
    uow: FromDishka[BaseUoW],
    jwt_data: JWTValidationData = Security(jwt_auth),
):
    user = await user_repo.claim_referrals_profit(model_id=jwt_data.parsed_data.user_id)

    await uow.commit()
    return ReferralsClaimProfitResponse(user=UserEntity.from_user_model(user))
