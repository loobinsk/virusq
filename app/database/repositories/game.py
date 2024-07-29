import datetime
from typing import Tuple

from sqlalchemy import and_, select, func, distinct, FunctionFilter
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Game
from app.database.repositories.base import BaseRepository
from app.utils.dt import get_aware_end_of_day


class GameRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self._session = session
        self._repository = BaseRepository(Game, session)

    async def create(self, game: Game) -> Game:
        result = await self._repository.create_one(game)

        return result

    async def get_by_id(self, model_id: str) -> Game:
        result = await self._repository.get_one(
            Game.id == model_id,
        )

        return result

    async def get_active_game(self, model_id: str, user_id: int) -> Game:
        result = await self._repository.get_one(
            whereclause=and_(
                Game.id == model_id,
                Game.user_id == user_id,
                Game.finished_at.is_(None),
            )
        )

        return result

    async def finish_game(self, game_id: str, score: int, marked_as_suspicious: bool) -> Game:
        result = await self._repository.update_one(
            whereclause=Game.id == game_id,
            score=score,
            marked_as_suspicious=marked_as_suspicious,
            on_fraud_check=marked_as_suspicious,
            finished_at=datetime.datetime.utcnow(),
        )

        return result

    async def get_games_in_progress_amount(self) -> int:
        statement = select(func.count(Game.id))
        games_in_progress_amount = await self._session.scalar(statement)

        return games_in_progress_amount  # type: ignore[return-value]

    async def get_game_engagement_stats(self) -> Tuple[int, int, int, int]:
        today_end = get_aware_end_of_day()
        today_start = today_end - datetime.timedelta(days=1)
        week_ago = today_end - datetime.timedelta(days=7)

        statement = select(
            func.count(Game.id).label("total_games"),
            self._produce_period_count_statement(
                today_start,
                today_end,
                count_unique_games=True,
            ).label("daily_unique_players"),
            self._produce_period_count_statement(
                today_start,
                today_end,
            ).label("daily_games_played"),
            self._produce_period_count_statement(
                week_ago,
                today_end,
            ).label("weekly_games_played"),
        )

        data = await self._session.execute(statement)
        return tuple(data.one())  # type: ignore[return-value]

    def _produce_period_count_statement(
        self,
        period_start: datetime.datetime,
        period_end: datetime.datetime,
        count_unique_games: bool = False,
    ) -> FunctionFilter[int]:
        field = Game.id

        if count_unique_games:
            field = distinct(Game.user_id)  # type: ignore[assignment]

        return func.count(field).filter(Game.created_at.between(period_start, period_end))
