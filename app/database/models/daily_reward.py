import datetime
from typing import TYPE_CHECKING

from sqlalchemy import SmallInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.mixins import AutoIncrementIdMixin
from app.database.models import Base

if TYPE_CHECKING:
    from app.database.models import User


class DailyReward(Base, AutoIncrementIdMixin):
    __tablename__ = "daily_rewards"

    day: Mapped[int] = mapped_column(SmallInteger, unique=True)
    reward_amount: Mapped[int]


class DailyRewardCompletition(Base, AutoIncrementIdMixin):
    __tablename__ = "daily_rewards_completition"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    daily_reward_id: Mapped[int | None] = mapped_column(
        ForeignKey("daily_rewards.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    collected_at: Mapped[datetime.datetime]

    user: Mapped["User"] = relationship(
        back_populates="collected_daily_rewards",
        lazy="noload",
    )
    daily_reward: Mapped["DailyReward"] = relationship(
        backref="completed_users",
        lazy="joined",
    )
