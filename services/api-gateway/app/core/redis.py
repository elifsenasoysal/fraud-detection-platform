"""
API Gateway — Core Redis Module
Manages Redis async connection.
"""

import logging
from typing import Optional

import redis.asyncio as aioredis

from app.config import settings

logger = logging.getLogger(__name__)

# Module-level Redis client
redis_client: Optional[aioredis.Redis] = None


async def init_redis() -> None:
    """Initialize Redis connection."""
    global redis_client
    redis_client = aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
    # Test connection
    await redis_client.ping()
    logger.info("✅ Redis connected")


async def close_redis() -> None:
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


def get_redis() -> aioredis.Redis:
    """FastAPI dependency that provides the Redis client.

    Usage:
        @router.get("/data")
        async def get_data(redis: aioredis.Redis = Depends(get_redis)):
            ...
    """
    if redis_client is None:
        raise RuntimeError("Redis is not initialized. Call init_redis() first.")
    return redis_client
