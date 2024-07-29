from collections import defaultdict

from authlib.common.errors import AuthlibBaseError  # type: ignore[import-untyped]
from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions.auth import InitDataAuthError
from app.exceptions.bonus_tasks import BonusTaskUncompletedError
from app.exceptions.daily_reward import DailyRewardAlreadyClaimedError
from app.exceptions.database import (
    IntegrityViolationError,
    RecordNotFoundError,
    DBActionNotAllowedError,
)
from app.exceptions.game import GameStartImpossibleError
from app.schemas.base import ErrorResponse


async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    reformatted_message = defaultdict(list)

    for pydantic_error in exc.errors():
        loc, msg = pydantic_error["loc"], pydantic_error["msg"]
        filtered_loc = loc[1:] if loc[0] in ("body", "query", "path") else loc

        field_string = ".".join(list(map(str, filtered_loc)))  # nested fields with dot-notation
        reformatted_message[field_string].append(msg)

    return ErrorResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message=jsonable_encoder({"errors": reformatted_message}),
    ).json_response


async def record_already_exists_exception_handler(
    _: Request, exc: IntegrityViolationError
) -> JSONResponse:
    return ErrorResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        message=exc.message,
    ).json_response


async def record_not_found_exception_handler(_: Request, exc: RecordNotFoundError) -> JSONResponse:
    return ErrorResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        message=exc.message,
    ).json_response


async def db_action_not_allowed_exception_handler(
    _: Request, exc: DBActionNotAllowedError
) -> JSONResponse:
    return ErrorResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        message=exc.message,
    ).json_response


async def init_data_auth_exception_handler(_: Request, exc: InitDataAuthError) -> JSONResponse:
    return ErrorResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        message=exc.message,
    ).json_response


async def authlib_error_exception_handler(_: Request, __: AuthlibBaseError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"message": "Unauthorized"},
    )


async def bonus_task_uncompleted_exception_handler(
    _: Request, exc: BonusTaskUncompletedError
) -> JSONResponse:
    return ErrorResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        message=exc.message,
    ).json_response


async def game_start_impossible_exception_handler(
    _: Request, exc: GameStartImpossibleError
) -> JSONResponse:
    return ErrorResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        message=exc.message,
    ).json_response


async def daily_reward_already_claimed_exception_handler(
    _: Request, exc: DailyRewardAlreadyClaimedError
) -> JSONResponse:
    return ErrorResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        message=exc.message,
    ).json_response
