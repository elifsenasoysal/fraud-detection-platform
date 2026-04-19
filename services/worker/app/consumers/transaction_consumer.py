"""
Worker — Transaction Consumer
Consumes transaction events from RabbitMQ, runs anomaly detection,
and publishes fraud alerts when detected.
"""

import json
import logging
import time
import uuid

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from app.cache.user_state import UserStateCache
from app.core.database import get_session
from app.core.redis import get_redis
from app.engine.detector import FraudDetector
from app.publishers.alert_publisher import AlertPublisher
from shared.constants import QUEUE_TRANSACTION_PROCESS
from shared.events import TransactionEvent

logger = logging.getLogger(__name__)


class TransactionConsumer:
    """Consumes transaction events from RabbitMQ and runs fraud detection.

    Flow:
    1. Consume message from fdp.transaction.process queue
    2. Deserialize into TransactionEvent
    3. Run FraudDetector.analyze()
    4. If fraud detected → publish FraudAlertEvent + update DB
    5. Update user cache state
    6. ACK/NACK the message
    """

    def __init__(self, channel: aio_pika.abc.AbstractChannel):
        self.channel = channel
        self.redis = get_redis()
        self.cache = UserStateCache(self.redis)
        self.detector = FraudDetector(cache=self.cache)
        self.publisher = AlertPublisher(channel)

    async def start(self) -> None:
        """Start consuming from the transaction queue."""
        queue = await self.channel.get_queue(QUEUE_TRANSACTION_PROCESS)
        await queue.consume(self._process_message)
        logger.info(f"📥 Consuming from queue: {QUEUE_TRANSACTION_PROCESS}")

    async def _process_message(self, message: AbstractIncomingMessage) -> None:
        """Process a single transaction message."""
        async with message.process():
            try:
                # Parse message
                body = json.loads(message.body.decode())
                transaction = TransactionEvent(**body)

                logger.info(
                    f"📦 Processing: tx={transaction.transaction_id} | "
                    f"user={transaction.user_external_id} | "
                    f"amount={transaction.amount} | location={transaction.location}"
                )

                # Run anomaly detection
                result = await self.detector.analyze(transaction)

                if result.is_fraud:
                    # Publish fraud alert
                    await self.publisher.publish_fraud_alert(
                        transaction=transaction,
                        detection_result=result,
                    )

                    # Update transaction status in DB
                    await self._update_transaction_status(
                        transaction.transaction_id, "suspicious"
                    )

                    # Update user fraud count and risk level
                    await self._update_user_fraud_stats(
                        transaction.user_id, result.risk_level
                    )

                # Update user cache state (record this transaction)
                await self.cache.record_transaction(
                    user_id=transaction.user_id,
                    amount=transaction.amount,
                    location=transaction.location,
                    latitude=transaction.latitude,
                    longitude=transaction.longitude,
                    timestamp=time.time(),
                )

                logger.info(
                    f"✅ Processed: tx={transaction.transaction_id} | "
                    f"fraud={result.is_fraud} | risk={result.risk_level}"
                )

            except Exception as e:
                logger.error(f"❌ Error processing message: {e}", exc_info=True)

    async def _update_transaction_status(
        self, transaction_id: str, status: str
    ) -> None:
        """Update transaction status in PostgreSQL."""
        try:
            async with get_session() as session:
                from sqlalchemy import text

                await session.execute(
                    text(
                        "UPDATE transactions SET status = :status WHERE id = :id"
                    ),
                    {"status": status, "id": transaction_id},
                )
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to update transaction status: {e}")

    async def _update_user_fraud_stats(
        self, user_id: str, risk_level: str
    ) -> None:
        """Update user's fraud flag count and risk level in PostgreSQL."""
        try:
            async with get_session() as session:
                from sqlalchemy import text

                await session.execute(
                    text(
                        "UPDATE users SET total_fraud_flags = total_fraud_flags + 1, "
                        "risk_level = :risk_level, updated_at = NOW() "
                        "WHERE id = :id"
                    ),
                    {"risk_level": risk_level, "id": user_id},
                )
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to update user fraud stats: {e}")
