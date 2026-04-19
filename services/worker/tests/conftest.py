"""
Worker — Test Fixtures
"""

import pytest
from datetime import datetime, timezone

from shared.events import TransactionEvent


@pytest.fixture
def sample_transaction():
    """Provide a sample transaction event for testing."""
    return TransactionEvent(
        transaction_id="test-tx-001",
        user_id="test-user-uuid",
        user_external_id="test_user_1",
        amount=500.00,
        currency="TRY",
        location="Istanbul",
        latitude=41.0082,
        longitude=28.9784,
        timestamp=datetime.now(timezone.utc),
    )


@pytest.fixture
def high_amount_transaction():
    """Transaction with unusually high amount."""
    return TransactionEvent(
        transaction_id="test-tx-002",
        user_id="test-user-uuid",
        user_external_id="test_user_1",
        amount=50000.00,
        currency="TRY",
        location="Istanbul",
        latitude=41.0082,
        longitude=28.9784,
        timestamp=datetime.now(timezone.utc),
    )
