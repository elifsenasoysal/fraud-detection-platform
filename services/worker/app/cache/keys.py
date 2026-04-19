"""
Worker — Redis Key Templates
Centralizes all Redis key patterns for consistency.
"""


class RedisKeys:
    """Redis key templates for user state management."""

    @staticmethod
    def user_transactions(user_id: str) -> str:
        """Sorted set of recent transaction timestamps (for velocity check)."""
        return f"user:{user_id}:transactions"

    @staticmethod
    def user_tx_amounts(user_id: str) -> str:
        """List of recent transaction amounts (for average calculation)."""
        return f"user:{user_id}:tx_amounts"

    @staticmethod
    def user_last_location(user_id: str) -> str:
        """Hash with last transaction's location data."""
        return f"user:{user_id}:last_location"

    @staticmethod
    def user_avg_amount(user_id: str) -> str:
        """Cached average amount for a user (24h window)."""
        return f"user:{user_id}:avg_amount"
