"""
API Gateway — Dependency Injection
Provides shared dependencies for route handlers.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from app.core.database import get_db
from app.core.redis import get_redis
from app.services.transaction_service import TransactionService
from app.services.user_service import UserService
from app.services.fraud_service import FraudService


async def get_transaction_service(
    db: AsyncSession = Depends(get_db),
) -> TransactionService:
    """Provide TransactionService instance."""
    return TransactionService(db)


async def get_user_service(
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
) -> UserService:
    """Provide UserService instance."""
    return UserService(db, redis)


async def get_fraud_service(
    db: AsyncSession = Depends(get_db),
) -> FraudService:
    """Provide FraudService instance."""
    return FraudService(db)
