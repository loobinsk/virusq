import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import BigInteger, SmallInteger, text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models import Base
from app.typings.consts import (
    DAILY_GAME_ENERGY_AMOUNT,
    FARMING_HOUR_MINING_RATE,
    FARMING_DURATION_HOURS,
    INITIAL_BALANCE,
    INITIAL_REFERRAL_BALANCE,
)
from app.typings.enums import UserFarmingStatus, UserLanguage

if TYPE_CHECKING:
    from app.database.models import BonusTaskCompletition, DailyRewardCompletition


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str | None]
    username: Mapped[str | None] = mapped_column(unique=True)
    language: Mapped[UserLanguage]

    is_banned: Mapped[bool] = mapped_column(server_default="0")
    source: Mapped[str | None] = mapped_column(index=True)
    referral_registration_bonus: Mapped[int] = mapped_column(server_default="0")

    balance: Mapped[int] = mapped_column(BigInteger, default=INITIAL_BALANCE, index=True)
    referral_balance: Mapped[int] = mapped_column(BigInteger, default=INITIAL_REFERRAL_BALANCE)
    daily_overall_profit: Mapped[int] = mapped_column(server_default="0", index=True)

    game_energy: Mapped[int] = mapped_column(SmallInteger, default=DAILY_GAME_ENERGY_AMOUNT)
    game_daily_highscore: Mapped[int] = mapped_column(server_default="0", index=True)
    game_alltime_highscore: Mapped[int] = mapped_column(server_default="0", index=True)

    farming_started_at: Mapped[datetime.datetime | None]
    farming_duration_hours: Mapped[int] = mapped_column(
        SmallInteger, default=FARMING_DURATION_HOURS
    )
    farming_hour_mining_rate: Mapped[int] = mapped_column(default=FARMING_HOUR_MINING_RATE)

    used_webapp: Mapped[bool] = mapped_column(server_default="0")

    last_activity_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())")
    )
    bot_blocked_at: Mapped[datetime.datetime | None]

    completed_bonus_tasks: Mapped[List["BonusTaskCompletition"]] = relationship(
        back_populates="user",
        lazy="noload",
    )

    collected_daily_rewards: Mapped[List["DailyRewardCompletition"]] = relationship(
        back_populates="user",
        lazy="noload",
    )

    @hybrid_property
    def farming_status(self) -> UserFarmingStatus:
        if self.farming_started_at is None:
            return UserFarmingStatus.NOT_STARTED
        elif (
            self.farming_started_at + datetime.timedelta(hours=self.farming_duration_hours)
            > datetime.datetime.utcnow()
        ):
            return UserFarmingStatus.IN_PROGRESS
        else:
            return UserFarmingStatus.FINISHED

    @property
    def farming_second_mining_rate(self) -> float:
        return round(self.farming_hour_mining_rate / 3600, 2)

    @hybrid_property
    def farming_total_profit(self) -> int:
        return self.farming_duration_hours * self.farming_hour_mining_rate
