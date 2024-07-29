import datetime

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Body
from fastapi import Security

from app.config import config
from app.database.models import User
from app.database.repositories.referral_link import ReferralLinkRepository
from app.database.repositories.user import UserRepository
from app.database.uow.base import BaseUoW
from app.exceptions.auth import InitDataAuthError
from app.exceptions.database import RecordNotFoundError
from app.schemas.base import ErrorResponse
from app.schemas.base import UserEntity
from app.schemas.general.auth import (
    TelegramWebappAuthData,
    RenewJWTResponse,
    RenewJWTInputData,
    JWTValidationData,
)
from app.schemas.user.account import SetUserInactiveResponse, GetUserByIdResponse, UserBotEntity
from app.schemas.user.account import (
    UserRegistrationInputData,
    UserRegistrationResponse,
    GetUserResponse,
)
from app.typings.consts import DEFAULT_REFERRAL_BONUS, DEFAULT_PREMIUM_REFERRAL_BONUS
from app.typings.enums import UserLanguage
from app.utils.auth import InitDataAuthManager, JWTAuth

account_router = APIRouter(prefix="/account", route_class=DishkaRoute)

jwt_auth = JWTAuth(
    secret_key=config.app.jwt_secret,
    auto_error=True,
    algorithm="HS256",
    access_expires_delta=datetime.timedelta(hours=1.5),
)
bot_jwt_auth = JWTAuth(
    secret_key=config.app.bot_jwt_secret,
    auto_error=True,
    algorithm="HS256",
    skip_serialization=True,
)


@account_router.post(
    "/registration",
    summary="Create new user",
    include_in_schema=False,
    dependencies=[Security(bot_jwt_auth)],
    responses={
        201: {"model": UserRegistrationResponse},
        401: {"model": ErrorResponse},
    },
)
async def registration_handler(
    data: UserRegistrationInputData,
    user_repo: FromDishka[UserRepository],
    referral_link_repo: FromDishka[ReferralLinkRepository],
    uow: FromDishka[BaseUoW],
) -> UserRegistrationResponse:
    reward = 0

    if data.source is not None:
        if data.source.isdigit():
            referrer = await user_repo.get_by_id(model_id=int(data.source))
            if referrer is None:
                data.source = None
            else:
                reward = (
                    DEFAULT_PREMIUM_REFERRAL_BONUS if data.is_premium else DEFAULT_REFERRAL_BONUS
                )
                await user_repo.reward_for_referral(
                    model_id=referrer.id,
                    amount=reward,
                )
        else:
            try:
                await referral_link_repo.get_by_id(model_id=data.source)
            except RecordNotFoundError:
                data.source = None

    user_model = User(
        **data.model_dump(exclude_none=True, exclude={"is_premium"}),
        balance=reward,
        referral_registration_bonus=reward,
    )

    user = await user_repo.create(user_model)
    await uow.commit()

    return UserRegistrationResponse(user=UserBotEntity.from_user_model(user))


@account_router.post(
    "/login",
    summary="Login",
    responses={
        200: {"model": RenewJWTResponse},
        401: {"model": ErrorResponse},
    },
    tags=["Account actions"],
)
async def login_handler(
    data: RenewJWTInputData,
    user_repo: FromDishka[UserRepository],
    referral_link_repo: FromDishka[ReferralLinkRepository],
    uow: FromDishka[BaseUoW],
    jwt_manager: FromDishka[JWTAuth],
    auth_manager: FromDishka[InitDataAuthManager],
) -> RenewJWTResponse:
    try:
        parsed_init_data = TelegramWebappAuthData.from_webapp_init_data(data.init_data)
        if not auth_manager.check_hash(init_data=parsed_init_data.raw_data):
            raise ValueError("Invalid hash")
    except ValueError as e:
        raise InitDataAuthError(message=f"Could not validate credentials. Details: {e.__repr__()}")

    jwt_data = {
        "user_id": parsed_init_data.user.id,
    }

    jwt_token = jwt_manager.create_access_token(
        subject=jwt_data,
        expires_delta=datetime.timedelta(hours=1.5),
    )
    try:
        await user_repo.get_by_id(model_id=parsed_init_data.user.id)
    except RecordNotFoundError:
        await registration_handler(
            data=UserRegistrationInputData(
                id=parsed_init_data.user.id,
                language=UserLanguage.RU
                if parsed_init_data.user.language_code == "ru"
                else UserLanguage.EN,
                source=parsed_init_data.start_param,
                username=parsed_init_data.user.username,
                first_name=parsed_init_data.user.first_name,
                last_name=parsed_init_data.user.last_name,
                is_premium=bool(parsed_init_data.user.is_premium),
            ),
            user_repo=user_repo,
            referral_link_repo=referral_link_repo,
            uow=uow,
        )

    await user_repo.update_one_by_id(
        model_id=parsed_init_data.user.id,
        used_webapp=True,
    )
    await uow.commit()

    return RenewJWTResponse(
        jwt_token=jwt_token,
        webapp_auth_data=parsed_init_data,
    )


@account_router.get(
    "/getMe",
    summary="Get Me",
    responses={
        200: {"model": GetUserResponse},
        401: {"model": ErrorResponse},
    },
    dependencies=[Security(jwt_auth)],
    tags=["Account actions"],
)
async def get_me_handler(
    user_repo: FromDishka[UserRepository],
    jwt_data: JWTValidationData = Security(jwt_auth),
):
    user = await user_repo.get_by_id(model_id=jwt_data.parsed_data.user_id)

    return GetUserResponse(user=UserEntity.from_user_model(user))


@account_router.get(
    "/getById",
    responses={
        200: {"model": GetUserByIdResponse},
        401: {"model": ErrorResponse},
    },
    dependencies=[Security(bot_jwt_auth)],
    include_in_schema=False,
    summary="Get user by ID",
)
async def get_by_id_handler(
    user_repo: FromDishka[UserRepository],
    user_id: int,
):
    user = await user_repo.get_by_id(model_id=user_id)

    return GetUserByIdResponse(user=UserBotEntity.from_user_model(user))


@account_router.post(
    "/setInactive",
    responses={
        200: {"model": SetUserInactiveResponse},
        401: {"model": ErrorResponse},
    },
    include_in_schema=False,
    dependencies=[Security(bot_jwt_auth)],
    summary="Set User Inactive by ID",
)
async def set_inactive_handler(
    user_repo: FromDishka[UserRepository],
    uow: FromDishka[BaseUoW],
    user_id: int = Body(embed=True),
):
    user = await user_repo.update_one_by_id(
        model_id=user_id, bot_blocked_at=datetime.datetime.utcnow()
    )

    await uow.commit()
    return SetUserInactiveResponse(user=UserBotEntity.from_user_model(user))


@account_router.post(
    "/setActive",
    responses={
        200: {"model": SetUserInactiveResponse},
        401: {"model": ErrorResponse},
    },
    include_in_schema=False,
    dependencies=[Security(bot_jwt_auth)],
    summary="Set User Active by ID",
)
async def set_active_handler(
    user_repo: FromDishka[UserRepository],
    uow: FromDishka[BaseUoW],
    user_id: int = Body(embed=True),
):
    user = await user_repo.update_one_by_id(model_id=user_id, bot_blocked_at=None)

    await uow.commit()
    return SetUserInactiveResponse(user=UserBotEntity.from_user_model(user))
