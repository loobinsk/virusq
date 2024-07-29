import datetime
from typing import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import DailyReward, DailyRewardCompletition
from app.database.repositories.base import BaseRepository


class DailyRewardRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self._session = session
        self._repository = BaseRepository(DailyReward, session)

    async def get_by_reward_day(self, reward_day: int) -> DailyReward:
        result = await self._repository.get_one(whereclause=DailyReward.day == reward_day)

        return result

    async def get_last_daily_reward(self) -> DailyReward:
        statement = select(DailyReward).order_by(DailyReward.day.desc()).limit(1)

        result = await self._session.scalar(statement)

        return result  # type: ignore[return-value]

    async def get_all(self) -> Sequence[DailyReward]:
        result = await self._repository.get_many()

        return result

    async def delete_collected_daily_rewards(self, user_id: int) -> None:
        statement = delete(DailyRewardCompletition).where(
            DailyRewardCompletition.user_id == user_id
        )

        await self._session.execute(statement)

    async def get_collected_daily_rewards(self, model_id: int) -> Sequence[DailyRewardCompletition]:
        statement = select(DailyRewardCompletition).where(
            DailyRewardCompletition.user_id == model_id
        )

        result = await self._session.scalars(statement)

        return result.all()

    async def claim_daily_reward(
        self, user_id: int, daily_reward_id: int
    ) -> DailyRewardCompletition:
        instance = DailyRewardCompletition(
            user_id=user_id,
            daily_reward_id=daily_reward_id,
            collected_at=datetime.datetime.utcnow(),
        )

        self._session.add(instance)
        await self._session.flush([instance])
        return instance
