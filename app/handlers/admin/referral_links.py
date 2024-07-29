from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Security

from app.database.models import ReferralLink
from app.database.repositories.referral_link import ReferralLinkRepository
from app.database.repositories.user import UserRepository
from app.database.uow.base import BaseUoW
from app.handlers.user.account import bot_jwt_auth
from app.schemas.admin.referral_links import (
    GetReferralLinkByIdResponse,
    CreateReferralLinkInputData,
    CreateReferralLinkResponse,
    DeleteReferralLinkResponse,
    GetActiveReferralLinksResponse,
    GetInactiveReferralLinksResponse,
    DeactivateReferralLinkResponse,
    ReferralLinkStats,
    ActivateReferralLinkResponse,
)
from app.schemas.admin.stats import UsersAmountStats, UsersDynamicStats, DetailedStatsEntity
from app.schemas.base import AdminReferralLinkEntity, ErrorResponse

referral_links_router = APIRouter(
    prefix="/referralLinks",
    route_class=DishkaRoute,
)


@referral_links_router.post(
    "/create",
    dependencies=[Security(bot_jwt_auth)],
    summary="Create Referral Link",
    tags=["Referral Links actions"],
    include_in_schema=False,
)
async def create_referral(
    data: CreateReferralLinkInputData,
    uow: FromDishka[BaseUoW],
    referral_link_repo: FromDishka[ReferralLinkRepository],
):
    referral_link = await referral_link_repo.create(
        referral_link=ReferralLink(id=data.id, name=data.name)
    )
    await uow.commit()

    return CreateReferralLinkResponse(
        referral_link=AdminReferralLinkEntity.from_referral_link_model(referral_link)
    )


@referral_links_router.get(
    "/getActive",
    summary="Get Active",
    responses={
        200: {"model": GetActiveReferralLinksResponse},
        401: {"model": ErrorResponse},
    },
    tags=["Referral Links Actions"],
    dependencies=[Security(bot_jwt_auth)],
    include_in_schema=False,
)
async def get_active_referral_links(
    referral_link_repo: FromDishka[ReferralLinkRepository],
):
    referral_links = await referral_link_repo.get_active()
    return GetActiveReferralLinksResponse(
        referral_links=[
            AdminReferralLinkEntity.from_referral_link_model(referral_link)
            for referral_link in referral_links
        ]
    )


@referral_links_router.get(
    "/getInactive",
    summary="Get Inactive",
    responses={
        200: {"model": GetInactiveReferralLinksResponse},
        401: {"model": ErrorResponse},
    },
    tags=["Referral Links Actions"],
    dependencies=[Security(bot_jwt_auth)],
    include_in_schema=False,
)
async def get_inactive_referral_links(
    referral_link_repo: FromDishka[ReferralLinkRepository],
):
    referral_links = await referral_link_repo.get_inactive()
    return GetInactiveReferralLinksResponse(
        referral_links=[
            AdminReferralLinkEntity.from_referral_link_model(referral_link)
            for referral_link in referral_links
        ]
    )


@referral_links_router.get(
    "/getById",
    responses={
        200: {"model": GetReferralLinkByIdResponse},
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Get Referral Link By Id",
    tags=["Referral Links actions"],
    dependencies=[Security(bot_jwt_auth)],
    include_in_schema=False,
)
async def get_referral_link_by_id(
    referral_link_repo: FromDishka[ReferralLinkRepository],
    user_repo: FromDishka[UserRepository],
    id: str,
):
    referral_link = await referral_link_repo.get_by_id(model_id=id)

    total_users, active_users, inactive_users = await user_repo.get_users_amount_stats(
        referral_source=referral_link.id
    )
    daily_dynamic, weekly_dynamic, monthly_dynamic = await user_repo.get_users_dynamic_stats(
        referral_source=referral_link.id
    )

    return GetReferralLinkByIdResponse(
        referral_link=AdminReferralLinkEntity.from_referral_link_model(referral_link),
        stats=ReferralLinkStats(
            users_amount_stats=UsersAmountStats(
                total_users=total_users,
                active_users=DetailedStatsEntity(
                    amount=active_users, percentage_reference_value=total_users
                ),
                inactive_users=DetailedStatsEntity(
                    amount=inactive_users, percentage_reference_value=total_users
                ),
            ),
            dynamic_stats=UsersDynamicStats(
                daily_dynamic=DetailedStatsEntity(
                    amount=daily_dynamic, percentage_reference_value=total_users
                ),
                weekly_dynamic=DetailedStatsEntity(
                    amount=weekly_dynamic, percentage_reference_value=total_users
                ),
                monthly_dynamic=DetailedStatsEntity(
                    amount=monthly_dynamic, percentage_reference_value=total_users
                ),
            ),
        ),
    )


@referral_links_router.post(
    "/activate",
    responses={
        200: {"model": ActivateReferralLinkResponse},
        401: {"model": ErrorResponse},
    },
    summary="Activate Referral Link",
    tags=["Referral Links actions"],
    dependencies=[Security(bot_jwt_auth)],
    include_in_schema=False,
)
async def activate_referral_link(
    referral_link_repo: FromDishka[ReferralLinkRepository],
    uow: FromDishka[BaseUoW],
    id: str,
):
    referral_link = await referral_link_repo.activate_by_id(model_id=id)
    await uow.commit()

    return ActivateReferralLinkResponse(
        referral_link=AdminReferralLinkEntity.from_referral_link_model(referral_link)
    )


@referral_links_router.post(
    "/deactivate",
    responses={
        200: {"model": DeactivateReferralLinkResponse},
        401: {"model": ErrorResponse},
    },
    summary="Deactivate Referral Link",
    tags=["Referral Links actions"],
    dependencies=[Security(bot_jwt_auth)],
    include_in_schema=False,
)
async def deactivate_referral_link(
    referral_link_repo: FromDishka[ReferralLinkRepository],
    uow: FromDishka[BaseUoW],
    id: str,
):
    referral_link = await referral_link_repo.deactivate_by_id(model_id=id)
    await uow.commit()

    return DeactivateReferralLinkResponse(
        referral_link=AdminReferralLinkEntity.from_referral_link_model(referral_link)
    )


@referral_links_router.delete(
    "/delete",
    responses={
        200: {"model": DeleteReferralLinkResponse},
        401: {"model": ErrorResponse},
    },
    summary="Delete Referral Link",
    tags=["Referral Links actions"],
    dependencies=[Security(bot_jwt_auth)],
    include_in_schema=False,
)
async def delete_referral_link(
    referral_link_repo: FromDishka[ReferralLinkRepository],
    uow: FromDishka[BaseUoW],
    id: str,
):
    referral_link = await referral_link_repo.delete_one_by_id(model_id=id)
    await uow.commit()

    return DeleteReferralLinkResponse(
        referral_link=AdminReferralLinkEntity.from_referral_link_model(referral_link)
    )
