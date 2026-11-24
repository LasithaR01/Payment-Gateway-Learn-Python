from collections.abc import AsyncIterator

import redis.asyncio as _async_redis
from fastapi import Request
from redis import ConnectionError as RedisConnectionError
from redis import RedisError
from redis import TimeoutError as RedisTimeoutError
from redis.asyncio.client import PubSub
from redis.asyncio.retry import Retry
from redis.backoff import default_backoff
from redis.maint_notifications import MaintNotificationsConfig

from api.settings import Settings

Redis = _async_redis.Redis


REDIS_RETRY_ON_ERRROR: list[type[RedisError]] = [RedisConnectionError, RedisTimeoutError]
REDIS_RETRY = Retry(default_backoff(), retries=50)
REDIS_MAINT_NOTIFICATIONS = MaintNotificationsConfig(enabled=False)


async def create_redis(settings: Settings) -> AsyncIterator[Redis]:
    # Keep timeouts finite on Windows so a down/broken Redis fails fast
    # instead of exhausting ephemeral ports with endless reconnects.
    redis = _async_redis.Redis.from_url(
        settings.redis_url,
        decode_responses=True,
        max_connections=50,
        retry_on_error=REDIS_RETRY_ON_ERRROR,
        retry=Retry(default_backoff(), retries=3),
        maint_notifications_config=REDIS_MAINT_NOTIFICATIONS,
        socket_timeout=5,
        socket_connect_timeout=2,
    )
    yield redis
    await redis.close()


async def get_redis(request: Request) -> Redis:
    return request.state.redis


__all__ = [
    "Redis",
    "PubSub",
    "REDIS_RETRY_ON_ERRROR",
    "REDIS_RETRY",
    "REDIS_MAINT_NOTIFICATIONS",
    "create_redis",
    "get_redis",
]
