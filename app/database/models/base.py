from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from app.database.mixins import (
    CreatedAtMixin,
    UpdatedAtMixin,
)

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase, CreatedAtMixin, UpdatedAtMixin):
    __abstract__ = True

    metadata = metadata
