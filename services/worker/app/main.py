"""
Worker — Main Entry Point
Starts the RabbitMQ consumer loop for transaction processing.
"""

import asyncio
import logging
import signal
import sys

from app.config import settings
from app.core.database import init_db, close_db
from app.core.redis import init_redis, close_redis
from app.core.rabbitmq import init_rabbitmq, close_rabbitmq
from app.consumers.transaction_consumer import TransactionConsumer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


async def main():
    """Main worker entry point."""
    logger.info("🔧 Starting Worker Service...")

    # Initialize connections
    await init_db()
    await init_redis()
    connection, channel = await init_rabbitmq()

    logger.info("✅ Worker is ready — listening for transactions...")

    # Start consumer
    consumer = TransactionConsumer(channel)
    await consumer.start()

    # Keep running until interrupted
    try:
        await asyncio.Future()  # Run forever
    except asyncio.CancelledError:
        pass
    finally:
        logger.info("🛑 Shutting down Worker...")
        await close_rabbitmq()
        await close_redis()
        await close_db()
        logger.info("👋 Worker stopped")


def handle_signal(sig, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {sig}, shutting down...")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    asyncio.run(main())
