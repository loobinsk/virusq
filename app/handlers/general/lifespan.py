from contextlib import asynccontextmanager

from apscheduler.executors.asyncio import AsyncIOExecutor  # type: ignore[import-untyped]
from dishka import AsyncContainer
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.setup import setup_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    dishka_container: AsyncContainer = app.state.dishka_container
    sessionmaker = await dishka_container.get(async_sessionmaker[AsyncSession])
    redis = await dishka_container.get(Redis)

    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    scheduler = setup_scheduler(sessionmaker)
    scheduler.start()

    yield

    scheduler.shutdown()
    await app.state.dishka_container.close()
