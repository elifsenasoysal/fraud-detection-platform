"""
Worker — Database Connection
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.config import settings

engine = None
async_session_factory = None


async def init_db():
    global engine, async_session_factory
    engine = create_async_engine(settings.database_url, pool_size=10, pool_pre_ping=True)
    async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def close_db():
    global engine
    if engine:
        await engine.dispose()


def get_session() -> AsyncSession:
    return async_session_factory()
