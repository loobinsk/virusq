from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.database.repositories.user import UserRepository
from app.database.uow.sqlalchemy import SQLAlchemyUoW


async def reset_overall_profit(
    sessionmaker: async_sessionmaker[AsyncSession],
):
    async with sessionmaker() as session:
        uow = SQLAlchemyUoW(session)
        user_repo = UserRepository(session)

        await user_repo.reset_daily_overall_profit()
        await uow.commit()
