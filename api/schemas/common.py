"""
Common Schemas — Shared Pydantic models
"""
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str
    error_code: Optional[str] = None


class SuccessResponse(BaseModel):
    """Standard success response"""
    message: str
    data: Optional[dict] = None
