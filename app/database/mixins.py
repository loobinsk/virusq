import datetime

from sqlalchemy import BigInteger, DateTime, text
from sqlalchemy.orm import (
    Mapped,
    declarative_mixin,
    mapped_column,
)


@declarative_mixin
class CreatedAtMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=text("TIMEZONE('utc', now())"),
    )


@declarative_mixin
class UpdatedAtMixin:
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        onupdate=datetime.datetime.utcnow,
        server_default=text("TIMEZONE('utc', now())"),
    )


@declarative_mixin
class AutoIncrementIdMixin:
    id: Mapped[int] = mapped_column(
        BigInteger,
        autoincrement=True,
        primary_key=True,
        sort_order=999,
    )
