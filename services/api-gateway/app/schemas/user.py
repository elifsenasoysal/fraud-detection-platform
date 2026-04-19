"""
API Gateway — User Pydantic Schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserRiskResponse(BaseModel):
    """User risk status response."""
    user_id: str
    external_id: str
    risk_level: str
    total_transactions: int
    total_fraud_flags: int
    fraud_rate: float = Field(description="Percentage of flagged transactions")
    recent_transactions_count: int = Field(description="Transactions in last 24h")
    average_amount_24h: Optional[float] = Field(None, description="Average transaction amount in last 24h")
    last_transaction_at: Optional[datetime] = None
    last_location: Optional[str] = None

    model_config = {"from_attributes": True}


class UserHistoryResponse(BaseModel):
    """User transaction history response."""
    user_id: str
    external_id: str
    total_transactions: int
    total_amount: float
    average_amount: float
    risk_level: str
    transactions: list = []
    fraud_alerts: list = []

    model_config = {"from_attributes": True}


class UserSummary(BaseModel):
    """Brief user summary for lists."""
    id: str
    external_id: str
    risk_level: str
    total_transactions: int
    total_fraud_flags: int
    created_at: datetime

    model_config = {"from_attributes": True}
