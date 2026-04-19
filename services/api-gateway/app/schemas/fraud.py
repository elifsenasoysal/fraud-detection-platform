"""
API Gateway — Fraud Alert Pydantic Schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FraudAlertResponse(BaseModel):
    """Fraud alert in API responses."""
    id: str
    transaction_id: str
    user_id: str
    user_external_id: str
    risk_level: str
    violated_rules: list[str]
    details: dict = {}
    amount: float
    location: str
    is_resolved: bool
    resolved_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class FraudListFilter(BaseModel):
    """Query filters for fraud alert list."""
    start_date: Optional[datetime] = Field(None, description="Start date for filtering")
    end_date: Optional[datetime] = Field(None, description="End date for filtering")
    risk_level: Optional[str] = Field(None, description="Filter by risk level")
    is_resolved: Optional[bool] = Field(None, description="Filter by resolved status")
    user_id: Optional[str] = Field(None, description="Filter by external user ID")


class FraudStatsResponse(BaseModel):
    """Fraud statistics summary."""
    total_alerts: int
    active_alerts: int
    resolved_alerts: int
    fraud_rate: float = Field(description="Percentage of suspicious transactions")
    alerts_by_risk: dict[str, int] = Field(
        default_factory=dict,
        description="Alert count by risk level",
    )
    alerts_by_rule: dict[str, int] = Field(
        default_factory=dict,
        description="Alert count by violated rule type",
    )
    top_flagged_users: list[dict] = Field(
        default_factory=list,
        description="Users with most fraud flags",
    )
