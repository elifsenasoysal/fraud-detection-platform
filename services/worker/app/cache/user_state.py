"""
Worker — User State Cache Management
Manages per-user state in Redis for real-time anomaly detection.
"""

import json
import logging
import time
from typing import Optional

import redis.asyncio as aioredis

from app.cache.keys import RedisKeys
from app.config import settings

logger = logging.getLogger(__name__)


class UserStateCache:
    """Manages user-level state in Redis for anomaly detection rules.

    Stores:
    - Transaction timestamps (Sorted Set) → velocity check
    - Transaction amounts (List) → average amount calculation
    - Last location data (Hash) → impossible travel check
    """

    def __init__(self, redis: aioredis.Redis):
        self.redis = redis

    async def record_transaction(
        self,
        user_id: str,
        amount: float,
        location: str,
        latitude: Optional[float],
        longitude: Optional[float],
        timestamp: float,
    ) -> None:
        """Record a new transaction in the user's cache state.

        This should be called AFTER anomaly checks so that
        the current transaction doesn't affect its own evaluation.
        """
        pipe = self.redis.pipeline()

        # 1. Add to velocity sorted set (score = timestamp)
        tx_key = RedisKeys.user_transactions(user_id)
        pipe.zadd(tx_key, {str(timestamp): timestamp})
        # Clean up old entries (keep last 10 minutes)
        pipe.zremrangebyscore(tx_key, 0, timestamp - 600)
        pipe.expire(tx_key, 3600)  # TTL: 1 hour

        # 2. Add amount to list
        amounts_key = RedisKeys.user_tx_amounts(user_id)
        pipe.lpush(amounts_key, str(amount))
        pipe.ltrim(amounts_key, 0, 99)  # Keep last 100 transactions
        pipe.expire(amounts_key, 86400)  # TTL: 24 hours

        # 3. Update last location
        location_key = RedisKeys.user_last_location(user_id)
        location_data = {
            "location": location,
            "latitude": str(latitude) if latitude else "",
            "longitude": str(longitude) if longitude else "",
            "timestamp": str(timestamp),
        }
        pipe.hset(location_key, mapping=location_data)
        pipe.expire(location_key, 86400)  # TTL: 24 hours

        await pipe.execute()

    async def get_recent_transaction_count(
        self, user_id: str, window_seconds: int
    ) -> int:
        """Get the number of transactions in the recent time window.

        Used by VelocityRule.
        """
        tx_key = RedisKeys.user_transactions(user_id)
        now = time.time()
        count = await self.redis.zcount(tx_key, now - window_seconds, now)
        return count

    async def get_average_amount(self, user_id: str) -> Optional[float]:
        """Get the average transaction amount from cached history.

        Used by AmountRule.
        """
        amounts_key = RedisKeys.user_tx_amounts(user_id)
        amounts = await self.redis.lrange(amounts_key, 0, -1)

        if not amounts:
            return None

        total = sum(float(a) for a in amounts)
        return total / len(amounts)

    async def get_last_location(self, user_id: str) -> Optional[dict]:
        """Get the last known location for the user.

        Used by LocationRule.
        Returns: {"location": str, "latitude": float, "longitude": float, "timestamp": float}
        """
        location_key = RedisKeys.user_last_location(user_id)
        data = await self.redis.hgetall(location_key)

        if not data or not data.get("location"):
            return None

        return {
            "location": data["location"],
            "latitude": float(data["latitude"]) if data.get("latitude") else None,
            "longitude": float(data["longitude"]) if data.get("longitude") else None,
            "timestamp": float(data["timestamp"]) if data.get("timestamp") else None,
        }
