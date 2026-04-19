"""
API Gateway — Common Pydantic Schemas
Shared response wrappers and pagination.
"""

from typing import Generic, TypeVar, Optional

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Query parameters for pagination."""
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginationMeta(BaseModel):
    """Pagination metadata in response."""
    page: int
    page_size: int
    total_items: int
    total_pages: int


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated API response."""
    success: bool = True
    data: list[T] = []
    pagination: PaginationMeta
    message: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    service: str
    version: str
    dependencies: dict[str, str] = {}
