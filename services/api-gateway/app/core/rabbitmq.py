"""
API Gateway — Core RabbitMQ Module
Manages RabbitMQ async connection, declares exchanges/queues, and provides publisher utilities.
"""

import json
import logging
from typing import Optional

import aio_pika

from app.config import settings

logger = logging.getLogger(__name__)

# Module-level connection and channel
connection: Optional[aio_pika.abc.AbstractRobustConnection] = None
channel: Optional[aio_pika.abc.AbstractChannel] = None


async def init_rabbitmq() -> None:
    """Initialize RabbitMQ connection, channel, and declare topology."""
    global connection, channel

    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()

    # Declare exchanges
    await channel.declare_exchange(
        "fdp.transactions", aio_pika.ExchangeType.DIRECT, durable=True
    )
    await channel.declare_exchange(
        "fdp.alerts", aio_pika.ExchangeType.FANOUT, durable=True
    )
    await channel.declare_exchange(
        "fdp.dlx", aio_pika.ExchangeType.DIRECT, durable=True
    )

    # Declare queues
    dlq = await channel.declare_queue("fdp.dlq.transaction", durable=True)

    process_queue = await channel.declare_queue(
        "fdp.transaction.process",
        durable=True,
        arguments={
            "x-dead-letter-exchange": "fdp.dlx",
            "x-dead-letter-routing-key": "dlq.transaction",
        },
    )

    alerts_queue = await channel.declare_queue("fdp.fraud.alerts", durable=True)

    # Bind queues to exchanges
    tx_exchange = await channel.get_exchange("fdp.transactions")
    alerts_exchange = await channel.get_exchange("fdp.alerts")
    dlx_exchange = await channel.get_exchange("fdp.dlx")

    await process_queue.bind(tx_exchange, routing_key="transaction.created")
    await alerts_queue.bind(alerts_exchange, routing_key="")
    await dlq.bind(dlx_exchange, routing_key="dlq.transaction")

    logger.info("✅ RabbitMQ connected & topology declared")


async def close_rabbitmq() -> None:
    """Close RabbitMQ connection."""
    global connection, channel

    if channel:
        await channel.close()
        channel = None
    if connection:
        await connection.close()
        connection = None


async def publish_message(
    exchange_name: str,
    routing_key: str,
    body: dict,
) -> None:
    """Publish a message to a RabbitMQ exchange.

    Args:
        exchange_name: Name of the exchange to publish to
        routing_key: Routing key for the message
        body: Message body (will be JSON serialized)
    """
    if channel is None:
        raise RuntimeError("RabbitMQ is not initialized. Call init_rabbitmq() first.")

    exchange = await channel.get_exchange(exchange_name)

    message = aio_pika.Message(
        body=json.dumps(body, default=str).encode(),
        content_type="application/json",
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
    )

    await exchange.publish(message, routing_key=routing_key)
    logger.debug(f"📤 Published to {exchange_name}/{routing_key}")
