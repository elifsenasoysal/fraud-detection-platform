"""
Shared event schemas for RabbitMQ message passing.
These define the contract between services.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TransactionEvent(BaseModel):
    """Event published when a new transaction is created.
    Published to: fdp.transactions exchange
    Routing key: transaction.created
    """
    transaction_id: str
    user_id: str
    user_external_id: str
    amount: float
    currency: str = "TRY"
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    metadata: dict = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FraudAlertEvent(BaseModel):
    """Event published when fraud is detected.
    Published to: fdp.alerts exchange (fanout)
    """
    alert_id: str
    transaction_id: str
    user_id: str
    user_external_id: str
    amount: float
    location: str
    risk_level: str
    violated_rules: list[str]
    details: dict = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TransactionProcessedEvent(BaseModel):
    """Event published after a transaction has been processed by the worker.
    Used to update the frontend via WebSocket.
    """
    transaction_id: str
    user_id: str
    status: str  # TransactionStatus value
    is_fraud: bool
    risk_level: Optional[str] = None
    violated_rules: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
