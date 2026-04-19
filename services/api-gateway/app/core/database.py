"""
API Gateway — Core Database Module
Manages SQLAlchemy async engine and session factory.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings

# Module-level state
engine = None
async_session_factory = None


async def init_db() -> None:
    """Initialize database engine and session factory."""
    global engine, async_session_factory

    engine = create_async_engine(
        settings.database_url,
        echo=settings.api_debug,
        pool_size=20,
        max_overflow=10,
        pool_pre_ping=True,
    )

    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def close_db() -> None:
    """Close database engine and release connections."""
    global engine
    if engine:
        await engine.dispose()
        engine = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides a database session.

    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
