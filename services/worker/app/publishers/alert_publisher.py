"""
Worker — Alert Publisher
Publishes fraud alert events to RabbitMQ and saves them to PostgreSQL.
"""

import json
import logging
import uuid

import aio_pika

from app.core.database import get_session
from app.engine.result import DetectionResult
from shared.constants import EXCHANGE_ALERTS
from shared.events import TransactionEvent, FraudAlertEvent

logger = logging.getLogger(__name__)


class AlertPublisher:
    """Publishes fraud alerts to RabbitMQ and persists them to the database."""

    def __init__(self, channel: aio_pika.abc.AbstractChannel):
        self.channel = channel

    async def publish_fraud_alert(
        self,
        transaction: TransactionEvent,
        detection_result: DetectionResult,
    ) -> None:
        """Create and publish a fraud alert.

        1. Generate FraudAlertEvent
        2. Save to PostgreSQL (fraud_alerts table)
        3. Publish to RabbitMQ (fdp.alerts exchange)
        """
        alert_id = str(uuid.uuid4())

        # Create alert event
        alert = FraudAlertEvent(
            alert_id=alert_id,
            transaction_id=transaction.transaction_id,
            user_id=transaction.user_id,
            user_external_id=transaction.user_external_id,
            amount=transaction.amount,
            location=transaction.location,
            risk_level=detection_result.risk_level,
            violated_rules=detection_result.violated_rule_names,
            details=detection_result.details,
        )

        # Save to database
        await self._save_to_db(alert)

        # Publish to RabbitMQ
        await self._publish_to_queue(alert)

        logger.warning(
            f"🚨 Fraud alert published: alert={alert_id} | "
            f"tx={transaction.transaction_id} | "
            f"user={transaction.user_external_id} | "
            f"risk={detection_result.risk_level}"
        )

    async def _save_to_db(self, alert: FraudAlertEvent) -> None:
        """Persist fraud alert to PostgreSQL."""
        try:
            async with get_session() as session:
                from sqlalchemy import text

                await session.execute(
                    text(
                        "INSERT INTO fraud_alerts "
                        "(id, transaction_id, user_id, risk_level, violated_rules, details) "
                        "VALUES (:id, :tx_id, :user_id, :risk_level, :violated_rules, :details)"
                    ),
                    {
                        "id": alert.alert_id,
                        "tx_id": alert.transaction_id,
                        "user_id": alert.user_id,
                        "risk_level": alert.risk_level,
                        "violated_rules": alert.violated_rules,
                        "details": json.dumps(alert.details, default=str),
                    },
                )
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to save fraud alert to DB: {e}")

    async def _publish_to_queue(self, alert: FraudAlertEvent) -> None:
        """Publish fraud alert event to RabbitMQ."""
        try:
            exchange = await self.channel.get_exchange(EXCHANGE_ALERTS)

            message = aio_pika.Message(
                body=json.dumps(alert.model_dump(), default=str).encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )

            await exchange.publish(message, routing_key="")
        except Exception as e:
            logger.error(f"Failed to publish fraud alert to RabbitMQ: {e}")
