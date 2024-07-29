import datetime
from typing import Sequence

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import BonusTask, BonusTaskCompletition
from app.database.repositories.base import BaseRepository
from app.exceptions.database import RecordNotFoundError


class BonusTaskRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self._session = session
        self._repository = BaseRepository(BonusTask, session)

    async def create(self, bonus_task: BonusTask) -> BonusTask:
        result = await self._repository.create_one(bonus_task)

        return result

    async def get_all(self) -> Sequence[BonusTask]:
        result = await self._repository.get_many()

        return result

    async def get_by_id(self, bonus_task_id: int) -> BonusTask:
        result = await self._repository.get_one(whereclause=BonusTask.id == bonus_task_id)

        return result

    async def update_by_id(self, bonus_task_id: int, **kwargs) -> BonusTask:
        result = await self._repository.update_one(
            whereclause=BonusTask.id == bonus_task_id, **kwargs
        )

        return result

    async def delete_by_id(self, bonus_task_id: int) -> BonusTask:
        result = await self._repository.delete_one(whereclause=BonusTask.id == bonus_task_id)

        return result

    async def get_uncompleted_task_by_id(self, user_id: int, bonus_task_id: int) -> BonusTask:
        statement = (
            select(BonusTask)
            .outerjoin(
                target=BonusTaskCompletition,
                onclause=and_(
                    BonusTaskCompletition.bonus_task_id == BonusTask.id,
                    BonusTaskCompletition.user_id == user_id,
                ),
            )
            .where(
                and_(
                    BonusTaskCompletition.bonus_task_id.is_(None),
                    BonusTask.id == bonus_task_id,
                )
            )
        )
        result = await self._session.scalar(statement)

        if result is None:
            raise RecordNotFoundError(BonusTask.__name__)

        return result

    async def get_uncompleted_tasks(self, user_id: int) -> Sequence[BonusTask]:
        statement = (
            select(BonusTask)
            .outerjoin(
                target=BonusTaskCompletition,
                onclause=and_(
                    BonusTaskCompletition.bonus_task_id == BonusTask.id,
                    BonusTaskCompletition.user_id == user_id,
                ),
            )
            .where(BonusTaskCompletition.bonus_task_id.is_(None))
        )

        result = await self._session.scalars(statement)
        return result.all()

    async def set_bonus_task_completed(self, user_id: int, bonus_task_id: int) -> None:
        instance = BonusTaskCompletition(
            user_id=user_id,
            bonus_task_id=bonus_task_id,
            completed_at=datetime.datetime.utcnow(),
        )

        self._session.add(instance)
        await self._session.flush([instance])
