"""
API Gateway — Transaction Pydantic Schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    """Schema for creating a new transaction via API."""
    user_id: str = Field(..., description="External user ID", examples=["user_42"])
    amount: float = Field(..., gt=0, description="Transaction amount", examples=[1500.00])
    currency: str = Field(default="TRY", max_length=3, description="Currency code")
    location: str = Field(..., description="Transaction location (city name)", examples=["Istanbul"])
    metadata: dict = Field(default_factory=dict, description="Additional transaction metadata")


class TransactionResponse(BaseModel):
    """Schema for transaction in API responses."""
    id: str
    user_id: str
    user_external_id: str
    amount: float
    currency: str
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str
    metadata: dict = {}
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionListFilter(BaseModel):
    """Query filters for transaction list."""
    status: Optional[str] = Field(None, description="Filter by status")
    user_id: Optional[str] = Field(None, description="Filter by external user ID")
    min_amount: Optional[float] = Field(None, ge=0, description="Minimum amount")
    max_amount: Optional[float] = Field(None, ge=0, description="Maximum amount")
    location: Optional[str] = Field(None, description="Filter by location")
    start_date: Optional[datetime] = Field(None, description="Start date filter")
    end_date: Optional[datetime] = Field(None, description="End date filter")
