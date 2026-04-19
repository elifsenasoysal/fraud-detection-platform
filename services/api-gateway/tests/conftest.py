"""
API Gateway — Test Configuration
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest_asyncio.fixture
async def client():
    """Provide an async HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_transaction():
    """Provide a sample transaction payload."""
    return {
        "user_id": "test_user_1",
        "amount": 250.00,
        "currency": "TRY",
        "location": "Istanbul",
        "metadata": {"test": True},
    }
