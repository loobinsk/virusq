from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database.repositories.user import UserRepository
from app.database.uow.sqlalchemy import SQLAlchemyUoW


async def reset_game_energy(sessionmaker: async_sessionmaker[AsyncSession]):
    async with sessionmaker() as session:
        uow = SQLAlchemyUoW(session)

        user_repo = UserRepository(session)
        await user_repo.reset_game_energy()
        await uow.commit()


async def reset_game_highscore(
    sessionmaker: async_sessionmaker[AsyncSession],
):
    async with sessionmaker() as session:
        uow = SQLAlchemyUoW(session)
        user_repo = UserRepository(session)

        await user_repo.reset_daily_highscore()
        await uow.commit()
