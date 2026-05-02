"""
API Gateway — Fraud Alert Endpoints
"""

import math
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_fraud_service
from app.schemas.common import APIResponse, PaginatedResponse, PaginationMeta
from app.services.fraud_service import FraudService

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedResponse,
    summary="List fraud alerts",
    description="Get paginated list of fraud alerts with filters.",
)
async def list_fraud_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    is_resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    user_id: Optional[str] = Query(None, description="Filter by external user ID"),
    service: FraudService = Depends(get_fraud_service),
):
    """List fraud alerts with optional date range and risk level filters."""
    alerts, total = await service.get_fraud_alerts(
        page=page,
        page_size=page_size,
        start_date=start_date,
        end_date=end_date,
        risk_level=risk_level,
        is_resolved=is_resolved,
        user_external_id=user_id,
    )

    return PaginatedResponse(
        data=alerts,
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=math.ceil(total / page_size) if total > 0 else 0,
        ),
    )


@router.get(
    "/stats",
    response_model=APIResponse,
    summary="Get fraud statistics",
    description="Get overall fraud statistics and analytics.",
)
async def get_fraud_stats(
    service: FraudService = Depends(get_fraud_service),
):
    """Get comprehensive fraud statistics."""
    stats = await service.get_fraud_stats()
    return APIResponse(success=True, data=stats)


@router.get(
    "/stats/trend",
    response_model=APIResponse,
    summary="Get fraud trend over time",
    description="Get daily fraud alert counts and rates for the specified period.",
)
async def get_fraud_trend(
    days: int = Query(7, ge=1, le=90, description="Number of days to look back"),
    service: FraudService = Depends(get_fraud_service),
):
    """Get daily fraud trend data for time-series charts."""
    trend = await service.get_fraud_trend(days=days)
    return APIResponse(success=True, data=trend)

