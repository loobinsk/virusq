from typing import List

import sentry_sdk
from apscheduler.executors.asyncio import AsyncIOExecutor  # type: ignore[import-untyped]
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore[import-untyped]
from apscheduler.triggers.cron import CronTrigger  # type: ignore[import-untyped]
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore[import-untyped]
from authlib.common.errors import AuthlibBaseError  # type: ignore[import-untyped]
from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from dishka.provider import BaseProvider
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.config import Config, config
from app.cron.account import reset_overall_profit
from app.cron.game import reset_game_energy, reset_game_highscore
from app.di.providers.auth import JWTManagerProvider
from app.di.providers.database import RepositoriesProvider, ConnectionProvider
from app.di.providers.redis import RedisProvider
from app.di.providers.webapp import WebAppProvider
from app.exceptions.auth import InitDataAuthError
from app.exceptions.bonus_tasks import BonusTaskUncompletedError
from app.exceptions.daily_reward import DailyRewardAlreadyClaimedError
from app.exceptions.database import (
    IntegrityViolationError,
    RecordNotFoundError,
    DBActionNotAllowedError,
)
from app.exceptions.game import GameStartImpossibleError
from app.handlers.general.exceptions import (
    record_already_exists_exception_handler,
    record_not_found_exception_handler,
    validation_exception_handler,
    init_data_auth_exception_handler,
    db_action_not_allowed_exception_handler,
    daily_reward_already_claimed_exception_handler,
    authlib_error_exception_handler,
    bonus_task_uncompleted_exception_handler,
    game_start_impossible_exception_handler,
)
from app.handlers.routes import user_router, admin_router
from app.handlers.user.account import jwt_auth
from app.utils.auth import JWTAuth
from app.utils.logs import SetupLogger, LoggerReg


def setup_handlers(app: FastAPI):
    for router in (user_router, admin_router):
        app.include_router(router)

    setup_exception_handlers(app)


def setup_middlewares(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def setup_exception_handlers(app: FastAPI):
    error_handlers = {
        validation_exception_handler: RequestValidationError,
        record_already_exists_exception_handler: IntegrityViolationError,
        record_not_found_exception_handler: RecordNotFoundError,
        authlib_error_exception_handler: AuthlibBaseError,
        bonus_task_uncompleted_exception_handler: BonusTaskUncompletedError,
        init_data_auth_exception_handler: InitDataAuthError,
        db_action_not_allowed_exception_handler: DBActionNotAllowedError,
        daily_reward_already_claimed_exception_handler: DailyRewardAlreadyClaimedError,
        game_start_impossible_exception_handler: GameStartImpossibleError,
    }
    for handler, error in error_handlers.items():
        app.add_exception_handler(error, handler)  # type: ignore[arg-type]


def setup_dependencies(
    app: FastAPI,
):
    providers: List[BaseProvider] = [
        ConnectionProvider(),
        RepositoriesProvider(),
        JWTManagerProvider(),
        WebAppProvider(),
        RedisProvider(),
    ]

    container = make_async_container(
        *providers,
        context={Config: config, JWTAuth: jwt_auth},
    )
    setup_dishka(container, app)


def setup_logging():
    SetupLogger(
        name_registration=[LoggerReg(name="", level=LoggerReg.Level(config.logging.level))],
        default_development=True,  # forcibly enable console formatting (development mode)
    )

    sentry_sdk.init(
        dsn=str(config.logging.sentry_dsn),
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        debug=config.is_dev_mode,
    )


def setup_scheduler(
    sessionmaker: async_sessionmaker[AsyncSession],
):
    scheduler = AsyncIOScheduler(
        executors={"default": AsyncIOExecutor()},
    )
    scheduler.add_job(
        reset_game_energy,
        kwargs={"sessionmaker": sessionmaker},
        trigger=CronTrigger(hour=0, minute=0, timezone="UTC"),
        id="reset_game_energy",
    )

    scheduler.add_job(
        reset_game_highscore,
        kwargs={"sessionmaker": sessionmaker},
        trigger=CronTrigger(hour=0, minute=0, timezone="UTC"),
        id="reset_daily_highscore",
    )

    scheduler.add_job(
        reset_overall_profit,
        kwargs={"sessionmaker": sessionmaker},
        trigger=CronTrigger(hour=0, minute=0, timezone="UTC"),
        id="reset_daily_overall_profit",
    )

    return scheduler
