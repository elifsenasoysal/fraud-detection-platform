"""
Worker — RabbitMQ Connection
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
    return connection, channel


async def close_rabbitmq():
    global connection, channel
    if channel:
        await channel.close()
        channel = None
    if connection:
        await connection.close()
        connection = None
