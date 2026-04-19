"""
API Gateway — Transaction Endpoints
"""

import math
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_transaction_service
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.schemas.common import APIResponse, PaginatedResponse, PaginationMeta
from app.services.transaction_service import TransactionService

router = APIRouter()


@router.post(
    "",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new transaction",
    description="Submit a new e-commerce transaction for processing and fraud analysis.",
)
async def create_transaction(
    data: TransactionCreate,
    service: TransactionService = Depends(get_transaction_service),
):
    """Create a new transaction.

    The transaction will be:
    1. Saved to the database
    2. Published to RabbitMQ for anomaly detection
    3. Processed by the Worker service
    """
    transaction = await service.create_transaction(data)

    return APIResponse(
        success=True,
        data={
            "id": str(transaction.id),
            "user_id": data.user_id,
            "amount": float(transaction.amount),
            "currency": transaction.currency,
            "location": transaction.location,
            "status": transaction.status,
            "created_at": transaction.created_at.isoformat() if transaction.created_at else None,
        },
        message="Transaction created and queued for processing",
    )


@router.get(
    "",
    response_model=PaginatedResponse,
    summary="List transactions",
    description="Get paginated list of transactions with optional filters.",
)
async def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by status"),
    user_id: Optional[str] = Query(None, description="Filter by external user ID"),
    min_amount: Optional[float] = Query(None, ge=0),
    max_amount: Optional[float] = Query(None, ge=0),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    service: TransactionService = Depends(get_transaction_service),
):
    """List transactions with filtering and pagination."""
    transactions, total = await service.get_transactions(
        page=page,
        page_size=page_size,
        status=status,
        user_external_id=user_id,
        min_amount=min_amount,
        max_amount=max_amount,
        start_date=start_date,
        end_date=end_date,
    )

    return PaginatedResponse(
        data=[
            {
                "id": str(tx.id),
                "user_id": str(tx.user_id),
                "amount": float(tx.amount),
                "currency": tx.currency,
                "location": tx.location,
                "status": tx.status,
                "created_at": tx.created_at.isoformat() if tx.created_at else None,
            }
            for tx in transactions
        ],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=math.ceil(total / page_size) if total > 0 else 0,
        ),
    )
