"""
API Gateway — Transaction Service
Business logic for transaction operations.
"""

import logging
import math
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.core.rabbitmq import publish_message
from shared.constants import EXCHANGE_TRANSACTIONS, ROUTING_KEY_TRANSACTION_CREATED
from shared.events import TransactionEvent
from shared.geo_data import get_city_coordinates

logger = logging.getLogger(__name__)


class TransactionService:
    """Handles transaction creation, querying, and publishing to message queue."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_transaction(self, data: TransactionCreate) -> Transaction:
        """Create a new transaction and publish event to RabbitMQ.

        1. Find or create the user
        2. Save transaction to DB
        3. Publish TransactionEvent to RabbitMQ for Worker processing
        4. Broadcast to WebSocket clients for real-time LiveFeed
        """
        # Find or create user
        user = await self._get_or_create_user(data.user_id)

        # Resolve coordinates from city name
        coords = get_city_coordinates(data.location)
        latitude = coords[0] if coords else None
        longitude = coords[1] if coords else None

        # Create transaction record
        transaction = Transaction(
            user_id=user.id,
            amount=float(data.amount),
            currency=data.currency,
            location=data.location,
            latitude=latitude,
            longitude=longitude,
            status="approved",  # Default; Worker may update to suspicious
            metadata_=data.metadata,
        )
        self.db.add(transaction)
        await self.db.flush()  # Get the ID without committing

        # Update user stats
        user.total_transactions += 1

        # Publish event to RabbitMQ
        event = TransactionEvent(
            transaction_id=str(transaction.id),
            user_id=str(user.id),
            user_external_id=data.user_id,
            amount=float(data.amount),
            currency=data.currency,
            location=data.location,
            latitude=latitude,
            longitude=longitude,
            metadata=data.metadata,
        )
        await publish_message(
            exchange_name=EXCHANGE_TRANSACTIONS,
            routing_key=ROUTING_KEY_TRANSACTION_CREATED,
            body=event.model_dump(),
        )

        # Broadcast to WebSocket clients for real-time LiveFeed
        try:
            from app.api.v1.websocket import broadcast_message

            await broadcast_message({
                "type": "new_transaction",
                "data": {
                    "id": str(transaction.id),
                    "user_id": str(user.id),
                    "user_external_id": data.user_id,
                    "amount": float(data.amount),
                    "currency": data.currency,
                    "location": data.location,
                    "status": transaction.status,
                    "created_at": transaction.created_at.isoformat() if transaction.created_at else None,
                },
            })
        except Exception as e:
            logger.warning(f"WebSocket broadcast failed (non-critical): {e}")

        logger.info(
            f"📝 Transaction created: {transaction.id} | "
            f"User: {data.user_id} | Amount: {data.amount} {data.currency} | "
            f"Location: {data.location}"
        )

        return transaction

    async def get_transactions(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        user_external_id: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> tuple[list[Transaction], int]:
        """Get paginated list of transactions with optional filters."""
        query = select(Transaction).join(User)
        count_query = select(func.count(Transaction.id)).join(User)

        # Apply filters
        filters = []
        if status:
            filters.append(Transaction.status == status)
        if user_external_id:
            filters.append(User.external_id == user_external_id)
        if min_amount is not None:
            filters.append(Transaction.amount >= min_amount)
        if max_amount is not None:
            filters.append(Transaction.amount <= max_amount)
        if start_date:
            filters.append(Transaction.created_at >= start_date)
        if end_date:
            filters.append(Transaction.created_at <= end_date)

        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))

        # Get total count
        total = await self.db.scalar(count_query)

        # Get paginated results
        offset = (page - 1) * page_size
        query = query.order_by(Transaction.created_at.desc()).offset(offset).limit(page_size)
        result = await self.db.execute(query)
        transactions = result.scalars().all()

        return transactions, total or 0

    async def get_transaction_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """Get a single transaction by ID."""
        query = select(Transaction).where(Transaction.id == transaction_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_transaction_status(
        self, transaction_id: str, status: str
    ) -> Optional[Transaction]:
        """Update the status of a transaction (called when fraud is detected)."""
        query = select(Transaction).where(Transaction.id == transaction_id)
        result = await self.db.execute(query)
        transaction = result.scalar_one_or_none()

        if transaction:
            transaction.status = status
            await self.db.flush()

        return transaction

    async def _get_or_create_user(self, external_id: str) -> User:
        """Get existing user or create a new one."""
        query = select(User).where(User.external_id == external_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                external_id=external_id,
                risk_level="low",
            )
            self.db.add(user)
            await self.db.flush()
            logger.info(f"👤 New user created: {external_id}")

        return user
