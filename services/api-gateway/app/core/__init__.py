"""
API Gateway — Core Database Module
Manages SQLAlchemy async engine and session factory.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings

# Engine and session factory (initialized in lifespan)
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
    """Close database engine."""
    global engine
    if engine:
        await engine.dispose()


async def get_db() -> AsyncSession:
    """Dependency that provides a database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
