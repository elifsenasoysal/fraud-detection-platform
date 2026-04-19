"""
API Gateway — User Endpoints
"""

import math

from fastapi import APIRouter, Depends, Query, HTTPException, status

from app.api.deps import get_user_service
from app.schemas.common import APIResponse, PaginatedResponse, PaginationMeta
from app.services.user_service import UserService

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedResponse,
    summary="List all users",
    description="Get paginated list of all users sorted by fraud flags.",
)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: UserService = Depends(get_user_service),
):
    """List all users with pagination."""
    users, total = await service.get_all_users(page=page, page_size=page_size)

    return PaginatedResponse(
        data=[
            {
                "id": str(u.id),
                "external_id": u.external_id,
                "risk_level": u.risk_level,
                "total_transactions": u.total_transactions,
                "total_fraud_flags": u.total_fraud_flags,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=math.ceil(total / page_size) if total > 0 else 0,
        ),
    )


@router.get(
    "/{user_id}/risk",
    response_model=APIResponse,
    summary="Get user risk status",
    description="Get comprehensive risk assessment for a specific user.",
)
async def get_user_risk(
    user_id: str,
    service: UserService = Depends(get_user_service),
):
    """Get user risk status including fraud rate and recent activity."""
    result = await service.get_user_risk(user_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found: {user_id}",
        )

    return APIResponse(success=True, data=result)


@router.get(
    "/{user_id}/history",
    response_model=APIResponse,
    summary="Get user transaction history",
    description="Get detailed transaction history and fraud alerts for a user.",
)
async def get_user_history(
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: UserService = Depends(get_user_service),
):
    """Get user's transaction history with fraud alerts."""
    result = await service.get_user_history(
        user_id, page=page, page_size=page_size
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found: {user_id}",
        )

    return APIResponse(success=True, data=result)
