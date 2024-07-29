import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from app.config import config
from app.database.mixins import AutoIncrementIdMixin
from app.database.models import Base
from app.typings.enums import BonusTaskType

if TYPE_CHECKING:
    from app.database.models.user import User


class BonusTask(Base, AutoIncrementIdMixin):
    __tablename__ = "bonus_tasks"

    name: Mapped[str]
    description: Mapped[str]
    photo: Mapped[bytes] = mapped_column(LargeBinary)
    link: Mapped[str]
    reward_amount: Mapped[int]
    task_type: Mapped[BonusTaskType]

    access_id: Mapped[int | None] = mapped_column(BigInteger, unique=True)
    access_data: Mapped[str | None] = mapped_column(
        StringEncryptedType(
            String,
            config.app.db_encryption_secret_key,
            AesEngine,
        )
    )


class BonusTaskCompletition(Base, AutoIncrementIdMixin):
    __tablename__ = "bonus_tasks_completition"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    bonus_task_id: Mapped[int] = mapped_column(
        ForeignKey("bonus_tasks.id", ondelete="CASCADE"),
        index=True,
    )
    user: Mapped["User"] = relationship(
        back_populates="completed_bonus_tasks",
        lazy="noload",
    )
    bonus_task: Mapped["BonusTask"] = relationship(
        backref="completed_users",
        lazy="noload",
    )

    completed_at: Mapped[datetime.datetime]
