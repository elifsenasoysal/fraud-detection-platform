"""
API Gateway — FastAPI Application Factory
Sets up the FastAPI app with lifespan events, middleware, and routes.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.database import init_db, close_db
from app.core.redis import init_redis, close_redis
from app.core.rabbitmq import init_rabbitmq, close_rabbitmq, start_alert_consumer
from app.api.v1.router import api_v1_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown events."""
    # ── Startup ──
    logger.info("🚀 Starting API Gateway...")
    await init_db()
    await init_redis()
    await init_rabbitmq()

    # Start consuming fraud alerts for WebSocket broadcast
    await start_alert_consumer()

    logger.info("✅ API Gateway is ready")

    yield

    # ── Shutdown ──
    logger.info("🛑 Shutting down API Gateway...")
    await close_rabbitmq()
    await close_redis()
    await close_db()
    logger.info("👋 API Gateway stopped")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title=settings.app_name,
        description=(
            "Real-time e-commerce fraud detection platform. "
            "Collects transaction data, detects anomalies, "
            "and provides alerts via WebSocket."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS Middleware ──
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict to specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Register Routers ──
    application.include_router(api_v1_router, prefix="/api/v1")

    return application


# Application instance
app = create_app()

