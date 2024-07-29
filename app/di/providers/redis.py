from dishka import Provider, Scope, from_context, provide
from redis import asyncio as aioredis
from redis.asyncio import Redis

from app.config import Config


class RedisProvider(Provider):
    scope = Scope.APP

    config = from_context(provides=Config, scope=Scope.APP)

    @provide
    def get_redis_instance(self, config: Config) -> Redis:
        return aioredis.from_url(config.redis.dsn)
