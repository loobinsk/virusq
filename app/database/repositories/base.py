from typing import Generic, Sequence, Type, TypeVar

from asyncpg import UniqueViolationError
from sqlalchemy import ColumnExpressionArgument, delete, select, update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from app.database.models import Base
from app.exceptions.database import IntegrityViolationError, RecordNotFoundError

AbstractModel = TypeVar("AbstractModel", bound=Base)


class BaseRepository(Generic[AbstractModel]):
    def __init__(
        self,
        type_model: Type[AbstractModel],
        _session: AsyncSession,
    ):
        self.type_model = type_model
        self._session = _session

    async def get_one(
        self,
        whereclause: ColumnExpressionArgument[bool] | None = None,
        options: Sequence[ExecutableOption] | None = None,
    ) -> AbstractModel:
        statement = select(self.type_model)

        if options is not None:
            statement = statement.options(*options)
        if whereclause is not None:
            statement = statement.where(whereclause)

        result = await self._session.scalar(statement)
        if result is None:
            raise RecordNotFoundError(self.type_model.__name__)

        return result

    async def get_many(
        self,
        whereclause: ColumnExpressionArgument[bool] | None = None,
        options: Sequence[ExecutableOption] | None = None,
        limit: int | None = None,
    ) -> Sequence[AbstractModel]:
        statement = select(self.type_model)

        if options is not None:
            statement = statement.options(*options)
        if whereclause is not None:
            statement = statement.where(whereclause)
        if limit is not None:
            statement = statement.limit(limit)

        result = await self._session.scalars(statement)

        return result.all()

    async def create_one(
        self,
        instance: AbstractModel,
    ) -> AbstractModel:
        try:
            self._session.add(instance)
            await self._session.flush([instance])
            return instance
        except IntegrityError as exc:
            orig = exc.orig
            # Error from asyncpg
            if (
                orig is not None
                and hasattr(orig, "sqlstate")
                and orig.sqlstate == UniqueViolationError.sqlstate
            ):
                raise IntegrityViolationError(self.type_model.__name__) from exc
            raise

    async def create_many(
        self,
        instances: Sequence[AbstractModel],
    ) -> Sequence[AbstractModel]:
        try:
            self._session.add_all(instances)
            await self._session.flush(instances)
            return instances
        except IntegrityError as exc:
            orig = exc.orig
            # Error from asyncpg
            if (
                orig is not None
                and hasattr(orig, "sqlstate")
                and orig.sqlstate == UniqueViolationError.sqlstate
            ):
                raise IntegrityViolationError(self.type_model.__name__) from exc
            raise

    async def update_one(
        self,
        whereclause: ColumnExpressionArgument[bool] | None = None,
        **kwargs,
    ) -> AbstractModel:
        statement = update(self.type_model).values(**kwargs).returning(self.type_model)

        if whereclause is not None:
            statement = statement.where(whereclause)

        try:
            result = (await self._session.execute(statement)).scalar_one()
        except NoResultFound:
            raise RecordNotFoundError(self.type_model.__name__)

        return result

    async def update_many(
        self,
        whereclause: ColumnExpressionArgument[bool] | None = None,
        **kwargs,
    ) -> Sequence[AbstractModel]:
        statement = update(self.type_model).values(**kwargs).returning(self.type_model)

        if whereclause is not None:
            statement = statement.where(whereclause)

        result = await self._session.scalars(statement)

        return result.all()

    async def delete_one(
        self,
        whereclause: ColumnExpressionArgument[bool] | None = None,
    ) -> AbstractModel:
        statement = delete(self.type_model).returning(self.type_model)

        if whereclause is not None:
            statement = statement.where(whereclause)

        try:
            result = (await self._session.execute(statement)).scalar_one()
        except NoResultFound:
            raise RecordNotFoundError(self.type_model.__name__)

        return result

    async def delete_many(
        self,
        whereclause: ColumnExpressionArgument[bool] | None = None,
    ) -> Sequence[AbstractModel]:
        statement = delete(self.type_model).returning(self.type_model)

        if whereclause is not None:
            statement = statement.where(whereclause)

        result = await self._session.scalars(statement)

        return result.all()
