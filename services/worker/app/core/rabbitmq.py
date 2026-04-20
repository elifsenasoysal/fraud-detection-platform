"""
Worker — RabbitMQ Connection
Declares required topology and provides channel for consumers.
"""

import aio_pika
from app.config import settings

connection = None
channel = None


async def init_rabbitmq():
    global connection, channel
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)

    # Declare exchanges (idempotent — safe to re-declare)
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
    await channel.declare_queue("fdp.dlq.transaction", durable=True)
    process_queue = await channel.declare_queue(
        "fdp.transaction.process",
        durable=True,
        arguments={
            "x-dead-letter-exchange": "fdp.dlx",
            "x-dead-letter-routing-key": "dlq.transaction",
        },
    )
    alerts_queue = await channel.declare_queue("fdp.fraud.alerts", durable=True)

    # Bind queues
    tx_exchange = await channel.get_exchange("fdp.transactions")
    alerts_exchange = await channel.get_exchange("fdp.alerts")
    dlx_exchange = await channel.get_exchange("fdp.dlx")

    await process_queue.bind(tx_exchange, routing_key="transaction.created")
    await alerts_queue.bind(alerts_exchange, routing_key="")
    dlq = await channel.get_queue("fdp.dlq.transaction")
    await dlq.bind(dlx_exchange, routing_key="dlq.transaction")

    return connection, channel


async def close_rabbitmq():
    global connection, channel
    if channel:
        await channel.close()
        channel = None
    if connection:
        await connection.close()
        connection = None
