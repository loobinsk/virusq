from datetime import datetime, timedelta
from typing import Sequence, Any, Tuple, List

from sqlalchemy import (
    select,
    func,
    Row,
    literal,
    String,
    and_,
    update,
    case,
    cast,
    ColumnElement,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User, DailyReward
from app.database.repositories.base import BaseRepository
from app.exceptions.database import DBActionNotAllowedError
from app.typings.consts import (
    DAILY_GAME_ENERGY_AMOUNT,
    REFERRAL_SYSTEM_MAX_LEVEL,
    REFERRAL_SYSTEM_PROFIT_PERCENT,
    RANKING_PLACE_LIMIT,
    RANKING_CHUNK_SIZE,
    ADMIN_STATS_PLOT_DAYS_AMOUNT,
)
from app.typings.enums import UserFarmingStatus
from app.utils.dt import get_aware_end_of_day


class UserRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self._session = session
        self._repository = BaseRepository(User, session)

    async def get_by_id(self, model_id: int) -> User:
        result = await self._repository.get_one(
            whereclause=User.id == model_id,
        )

        return result

    async def get_all(self) -> Sequence[User]:
        result = await self._repository.get_many()

        return result

    async def get_all_ids(self) -> Sequence[int]:
        statement = select(User.id)
        result = await self._session.scalars(statement)

        return result.all()

    async def create(self, user: User) -> User:
        result = await self._repository.create_one(user)

        return result

    async def update_one_by_id(
        self,
        model_id: int,
        **kwargs,
    ) -> User:
        result = await self._repository.update_one(whereclause=User.id == model_id, **kwargs)

        return result

    async def reward_for_referral(
        self,
        model_id: int,
        amount: int,
    ) -> User:
        result = await self._repository.update_one(
            whereclause=User.id == model_id,
            referral_balance=User.referral_balance + amount,
        )

        return result

    async def delete_one_by_id(self, model_id: int) -> User:
        result = await self._repository.delete_one(whereclause=User.id == model_id)

        return result

    async def start_farming(self, model_id: int) -> User:
        user = await self.get_by_id(model_id)

        if user.farming_status != UserFarmingStatus.NOT_STARTED:
            raise DBActionNotAllowedError(User.__name__)

        result = await self._repository.update_one(
            whereclause=User.id == model_id,
            farming_started_at=datetime.utcnow(),
        )

        return result

    async def claim_farming(self, model_id: int) -> User:
        user = await self.get_by_id(model_id)

        if user.farming_status != UserFarmingStatus.FINISHED:
            raise DBActionNotAllowedError(User.__name__)

        result = await self._repository.update_one(
            whereclause=User.id == model_id,
            farming_started_at=None,
            balance=User.balance + User.farming_total_profit,
            daily_overall_profit=User.daily_overall_profit + User.farming_total_profit,
        )

        return result

    async def reset_game_energy(self) -> None:
        await self._repository.update_many(
            whereclause=User.game_energy < DAILY_GAME_ENERGY_AMOUNT,
            game_energy=DAILY_GAME_ENERGY_AMOUNT,
        )

    async def reset_daily_highscore(self) -> None:
        await self._repository.update_many(
            whereclause=User.game_daily_highscore > 0,
            game_daily_highscore=0,
        )

    async def reset_daily_overall_profit(self) -> None:
        await self._repository.update_many(
            whereclause=User.daily_overall_profit > 0,
            daily_overall_profit=0,
        )

    async def claim_reward(self, user_id: int, reward: DailyReward) -> User:
        user = await self._repository.update_one(
            whereclause=User.id == user_id,
            balance=User.balance + reward.reward_amount,
            daily_overall_profit=User.daily_overall_profit + reward.reward_amount,
        )

        return user

    async def reward_user_referrers(self, user_id: int, initial_profit: int) -> None:
        tree_recursive_cte = (
            select(
                User.id,
                User.source,
                User.balance,
                literal(0).label("level"),
            )
            .where(User.id == user_id)
            .cte(name="tree", recursive=True)
        )

        tree_recursive_cte = tree_recursive_cte.union_all(
            select(
                User.id,
                User.source,
                User.balance,
                (tree_recursive_cte.c.level + 1).label("level"),
            ).where(
                and_(
                    cast(User.id, String) == tree_recursive_cte.c.source,
                    tree_recursive_cte.c.level + 1 <= REFERRAL_SYSTEM_MAX_LEVEL,
                )
            )
        )

        update_statement = (
            update(User)
            .where(
                and_(
                    User.id == tree_recursive_cte.c.id,
                    tree_recursive_cte.c.level > 0,
                ),
            )
            .values(
                referral_balance=case(
                    *[
                        (
                            tree_recursive_cte.c.level == level,
                            User.referral_balance + initial_profit * percent // 100,
                        )
                        for level, percent in list(REFERRAL_SYSTEM_PROFIT_PERCENT.items())
                    ],
                )
            )
        )
        await self._session.execute(update_statement)
        await self._session.commit()

    async def get_referrals_stats(self, model_id: int) -> Sequence[Row[tuple[int, Any, Any]]]:
        tree_cte = (
            select(
                User.id.label("id"),
                User.referral_registration_bonus.label("referral_registration_bonus"),
                User.source.label("source"),
                literal(value=0).label("level"),
            )
            .where(User.id == model_id)
            .cte(name="tree", recursive=True)
        )

        tree_recursive = tree_cte.union_all(
            select(
                User.id,
                User.referral_registration_bonus,
                User.source,
                (tree_cte.c.level + 1).label("level"),
            )
            .join(tree_cte, cast(tree_cte.c.id, String) == User.source)  # type: ignore[name-defined]
            .where((tree_cte.c.level + 1) <= REFERRAL_SYSTEM_MAX_LEVEL)
        )

        result = await self._session.execute(
            select(
                func.count(tree_recursive.c.id).label("referrals_amount"),
                func.sum(tree_recursive.c.referral_registration_bonus).label("referrals_profit"),
                tree_recursive.c.level.label("level"),
            )
            .where(tree_recursive.c.level > 0)
            .group_by(tree_recursive.c.level)
        )

        return result.all()

    async def claim_referrals_profit(
        self,
        model_id: int,
    ) -> User:
        result = await self._repository.update_one(
            whereclause=User.id == model_id,
            balance=User.balance + User.referral_balance,
            daily_overall_profit=User.daily_overall_profit + User.referral_balance,
            referral_balance=0,
        )
        return result

    async def renew_last_activity_at(
        self,
        model_id: int,
    ) -> User:
        result = await self._repository.update_one(
            whereclause=User.id == model_id,
            last_activity_at=datetime.utcnow(),
        )

        return result

    async def get_user_ranking_info(
        self,
        model_id: int,
        ranking_field: str,
    ) -> Tuple[int, int]:
        target_user = await self.get_by_id(model_id)
        ranking_value = getattr(target_user, ranking_field)

        ranking_place_subq = (
            select(User.id)
            .where(
                and_(
                    getattr(User, ranking_field) >= ranking_value,
                    User.id != target_user.id,
                )
            )
            .limit(RANKING_PLACE_LIMIT - 1)
        ).subquery()

        ranking_place_statement = select(func.count("*")).select_from(ranking_place_subq)

        ranking_place = await self._session.scalar(ranking_place_statement)

        if ranking_place is None:
            ranking_place = 1
        else:
            ranking_place += 1

        return ranking_place, ranking_value

    async def get_ranking_chunk(
        self,
        ranking_field: str,
        offset: int,
    ) -> Sequence[User]:
        statement = (
            select(User)
            .order_by(getattr(User, ranking_field).desc(), User.first_name, User.last_name)
            .offset(offset)
            .limit(RANKING_CHUNK_SIZE)
        )

        result = await self._session.scalars(statement)
        return result.all()

    async def decrement_game_energy(
        self,
        model_id: int,
    ) -> User:
        user = await self._repository.update_one(
            whereclause=User.id == model_id,
            game_energy=User.game_energy - 1,
        )
        return user

    async def update_highscores(
        self,
        update_daily_highscore: bool,
        update_alltime_highscore: bool,
        user_id: int,
        score: int,
    ) -> User:
        extra_values = {}

        if update_daily_highscore:
            extra_values["game_daily_highscore"] = score
        if update_alltime_highscore:
            extra_values["game_alltime_highscore"] = score

        user = await self._repository.update_one(
            whereclause=User.id == user_id,
            balance=User.balance + score,
            daily_overall_profit=User.daily_overall_profit + score,
            **extra_values,
        )
        return user

    async def get_users_amount_stats(
        self, referral_source: str | None = None
    ) -> Tuple[int, int, int]:
        statement = select(
            func.count(User.id).label("total_users"),
            func.count(User.id).filter(User.bot_blocked_at.is_(None)).label("active_users"),
            func.count(User.id).filter(User.bot_blocked_at.isnot(None)).label("inactive_users"),
        )

        if referral_source is not None:
            statement = statement.where(User.source == referral_source)

        data = await self._session.execute(statement)

        return tuple(data.one())  # type: ignore[return-value]

    async def get_game_players_stats(self) -> Tuple[int, int, int, int]:
        online_cright = datetime.utcnow()
        online_cleft = online_cright - timedelta(minutes=5)

        statement = select(
            func.count(User.id).label("total_players"),
            func.count(User.id).filter(User.bot_blocked_at.is_(None)).label("active_players"),
            func.count(User.id).filter(User.bot_blocked_at.isnot(None)).label("inactive_players"),
            func.count(User.id)
            .filter(User.last_activity_at.between(online_cleft, online_cright))
            .label("online"),
        ).where(User.used_webapp.is_(True))

        data = await self._session.execute(statement)

        return tuple(data.one())  # type: ignore[return-value]

    async def get_users_dynamic_stats(
        self, referral_source: str | None = None
    ) -> Tuple[int, int, int]:
        today_end = get_aware_end_of_day()
        today_start = today_end - timedelta(days=1)
        week_ago = today_end - timedelta(days=7)
        month_ago = today_end - timedelta(days=30)

        statement = select(
            self._produce_users_dynamic_count_statement(
                today_start,
                today_end,
            ).label("daily_dynamic"),
            self._produce_users_dynamic_count_statement(
                week_ago,
                today_end,
            ).label("weekly_dynamic"),
            self._produce_users_dynamic_count_statement(
                month_ago,
                today_end,
            ).label("monthly_dynamic"),
        )

        if referral_source is not None:
            statement = statement.where(User.source == referral_source)

        data = await self._session.execute(statement)

        return tuple(data.one())  # type: ignore[return-value]

    async def get_data_for_stats_plot(self) -> Tuple[List[int], List[int], List[int]]:
        new_users_data: List[int] = []
        blocked_users_data: List[int] = []
        new_users_without_source_data: List[int] = []

        stats_period_start = get_aware_end_of_day(days_offset=ADMIN_STATS_PLOT_DAYS_AMOUNT - 1)

        for days_offset in range(ADMIN_STATS_PLOT_DAYS_AMOUNT):
            cright = stats_period_start + timedelta(days=days_offset)
            cleft = cright - timedelta(days=1)

            new_users_amount_statement = select(func.count()).where(
                User.created_at.between(cleft, cright)
            )
            new_users_without_source_amount_statement = new_users_amount_statement.where(
                User.source.is_(None)
            )
            blocked_users_amount_statement = select(func.count()).where(
                and_(
                    User.bot_blocked_at.is_not(None),
                    User.bot_blocked_at.between(
                        cleft,
                        cright,
                    ),
                )
            )

            for statement, data_array in zip(
                [
                    new_users_amount_statement,
                    blocked_users_amount_statement,
                    new_users_without_source_amount_statement,
                ],
                [
                    new_users_data,
                    blocked_users_data,
                    new_users_without_source_data,
                ],
            ):
                data = await self._session.scalar(statement)
                data_array.append(data)  # type: ignore[arg-type]

        return new_users_data, blocked_users_data, new_users_without_source_data

    def _produce_users_dynamic_count_statement(
        self,
        period_start: datetime,
        period_end: datetime,
    ) -> ColumnElement[int]:
        return func.count(User.id).filter(
            User.created_at.between(period_start, period_end),
        ) - func.count(User.id).filter(
            and_(
                User.bot_blocked_at.between(period_start, period_end),
                User.bot_blocked_at.isnot(None),
            )
        )
