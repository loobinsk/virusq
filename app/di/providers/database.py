from typing import AsyncIterable

from dishka import Provider, Scope, from_context, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import Config
from app.database.repositories.bonus_task import BonusTaskRepository
from app.database.repositories.daily_reward import DailyRewardRepository
from app.database.repositories.game import GameRepository
from app.database.repositories.referral_link import ReferralLinkRepository
from app.database.repositories.user import UserRepository
from app.database.uow.base import BaseUoW
from app.database.uow.sqlalchemy import SQLAlchemyUoW


class ConnectionProvider(Provider):
    scope = Scope.APP

    config = from_context(provides=Config, scope=Scope.APP)

    @provide
    async def get_async_engine(self, config: Config) -> AsyncIterable[AsyncEngine]:
        engine = create_async_engine(
            url=config.postgres.dsn,
            echo=config.is_dev_mode,
            future=True,
            pool_size=5000,
            max_overflow=5000,
            pool_pre_ping=True,
        )

        yield engine

        await engine.dispose(close=True)

    @provide
    def get_async_sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            engine,
            autoflush=False,
            expire_on_commit=False,
        )

    @provide(scope=Scope.REQUEST)
    async def async_session(
        self, sessionmaker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with sessionmaker() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def uow(self, session: AsyncSession) -> BaseUoW:
        return SQLAlchemyUoW(session)


class RepositoriesProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def user_repo(self, session: AsyncSession) -> UserRepository:
        return UserRepository(session=session)

    @provide
    def referral_link_repo(self, session: AsyncSession) -> ReferralLinkRepository:
        return ReferralLinkRepository(session=session)

    @provide
    def bonus_task_repo(self, session: AsyncSession) -> BonusTaskRepository:
        return BonusTaskRepository(session=session)

    @provide
    def daily_reward_repo(self, session: AsyncSession) -> DailyRewardRepository:
        return DailyRewardRepository(session=session)

    @provide
    def game_repo(self, session: AsyncSession) -> GameRepository:
        return GameRepository(session=session)
