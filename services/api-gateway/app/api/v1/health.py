"""
API Gateway — Health Check Endpoint
"""

import logging

from fastapi import APIRouter
import redis.asyncio as aioredis

from app.config import settings
from app.core.redis import redis_client
from app.schemas.common import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check the health status of the API Gateway and its dependencies.",
)
async def health_check():
    """Check service health and dependency connectivity."""
    dependencies = {}

    # Check Redis
    try:
        if redis_client:
            await redis_client.ping()
            dependencies["redis"] = "healthy"
        else:
            dependencies["redis"] = "not initialized"
    except Exception as e:
        dependencies["redis"] = f"unhealthy: {str(e)}"

    # Check RabbitMQ
    from app.core.rabbitmq import connection
    try:
        if connection and not connection.is_closed:
            dependencies["rabbitmq"] = "healthy"
        else:
            dependencies["rabbitmq"] = "not connected"
    except Exception as e:
        dependencies["rabbitmq"] = f"unhealthy: {str(e)}"

    # Overall status
    all_healthy = all(v == "healthy" for v in dependencies.values())

    return HealthResponse(
        status="healthy" if all_healthy else "degraded",
        service="api-gateway",
        version="1.0.0",
        dependencies=dependencies,
    )
