"""
API Gateway — User Service
Business logic for user risk assessment and history.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from app.models.user import User
from app.models.transaction import Transaction
from app.models.fraud_alert import FraudAlert

logger = logging.getLogger(__name__)


class UserService:
    """Handles user risk assessment and transaction history."""

    def __init__(self, db: AsyncSession, redis: Optional[aioredis.Redis] = None):
        self.db = db
        self.redis = redis

    async def get_user_risk(self, external_id: str) -> Optional[dict]:
        """Get comprehensive risk status for a user."""
        # Find user
        query = select(User).where(User.external_id == external_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            return None

        # Calculate recent transaction stats (last 24h)
        cutoff_24h = datetime.now(timezone.utc) - timedelta(hours=24)

        recent_count_query = select(func.count(Transaction.id)).where(
            and_(
                Transaction.user_id == user.id,
                Transaction.created_at >= cutoff_24h,
            )
        )
        recent_count = await self.db.scalar(recent_count_query) or 0

        # Average amount in last 24h
        avg_query = select(func.avg(Transaction.amount)).where(
            and_(
                Transaction.user_id == user.id,
                Transaction.created_at >= cutoff_24h,
            )
        )
        avg_amount = await self.db.scalar(avg_query)

        # Last transaction
        last_tx_query = (
            select(Transaction)
            .where(Transaction.user_id == user.id)
            .order_by(Transaction.created_at.desc())
            .limit(1)
        )
        last_tx_result = await self.db.execute(last_tx_query)
        last_tx = last_tx_result.scalar_one_or_none()

        # Calculate fraud rate
        fraud_rate = 0.0
        if user.total_transactions > 0:
            fraud_rate = (user.total_fraud_flags / user.total_transactions) * 100

        return {
            "user_id": str(user.id),
            "external_id": user.external_id,
            "risk_level": user.risk_level,
            "total_transactions": user.total_transactions,
            "total_fraud_flags": user.total_fraud_flags,
            "fraud_rate": round(fraud_rate, 2),
            "recent_transactions_count": recent_count,
            "average_amount_24h": round(float(avg_amount), 2) if avg_amount else None,
            "last_transaction_at": last_tx.created_at if last_tx else None,
            "last_location": last_tx.location if last_tx else None,
        }

    async def get_user_history(
        self, external_id: str, page: int = 1, page_size: int = 20
    ) -> Optional[dict]:
        """Get user's transaction history and fraud alerts."""
        # Find user
        query = select(User).where(User.external_id == external_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            return None

        # Get transactions (paginated)
        offset = (page - 1) * page_size
        tx_query = (
            select(Transaction)
            .where(Transaction.user_id == user.id)
            .order_by(Transaction.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        tx_result = await self.db.execute(tx_query)
        transactions = tx_result.scalars().all()

        # Get fraud alerts
        alert_query = (
            select(FraudAlert)
            .where(FraudAlert.user_id == user.id)
            .order_by(FraudAlert.created_at.desc())
            .limit(50)
        )
        alert_result = await self.db.execute(alert_query)
        alerts = alert_result.scalars().all()

        # Calculate totals
        total_amount_query = select(func.sum(Transaction.amount)).where(
            Transaction.user_id == user.id
        )
        total_amount = await self.db.scalar(total_amount_query) or 0

        avg_amount = float(total_amount) / user.total_transactions if user.total_transactions > 0 else 0

        return {
            "user_id": str(user.id),
            "external_id": user.external_id,
            "total_transactions": user.total_transactions,
            "total_amount": round(float(total_amount), 2),
            "average_amount": round(avg_amount, 2),
            "risk_level": user.risk_level,
            "transactions": [
                {
                    "id": str(tx.id),
                    "amount": float(tx.amount),
                    "currency": tx.currency,
                    "location": tx.location,
                    "status": tx.status,
                    "created_at": tx.created_at.isoformat(),
                }
                for tx in transactions
            ],
            "fraud_alerts": [
                {
                    "id": str(alert.id),
                    "transaction_id": str(alert.transaction_id),
                    "risk_level": alert.risk_level,
                    "violated_rules": alert.violated_rules,
                    "is_resolved": alert.is_resolved,
                    "created_at": alert.created_at.isoformat(),
                }
                for alert in alerts
            ],
        }

    async def get_all_users(
        self, page: int = 1, page_size: int = 20
    ) -> tuple[list[User], int]:
        """Get paginated list of all users."""
        count_query = select(func.count(User.id))
        total = await self.db.scalar(count_query) or 0

        offset = (page - 1) * page_size
        query = (
            select(User)
            .order_by(User.total_fraud_flags.desc(), User.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        result = await self.db.execute(query)
        users = result.scalars().all()

        return users, total
