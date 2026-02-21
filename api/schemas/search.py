"""
Search Schemas — Pydantic models for hybrid search
"""
from pydantic import BaseModel, Field
from typing import Optional


class SearchRequest(BaseModel):
    """Search request schema"""
    query: str = Field(..., min_length=1)
    doc_type_filter: Optional[str] = Field(None, pattern="^(BRD|BA|TA|TC)$")
    project_filter: Optional[int] = None
    limit: int = Field(default=10, ge=1, le=100)


class SearchResult(BaseModel):
    """Individual search result"""
    document_id: int
    title: str
    doc_type: str
    score: float
    snippet: str
    metadata: Optional[dict] = None


class SearchResponse(BaseModel):
    """Search response schema"""
    query: str
    results: list[SearchResult]
    total_found: int
    execution_time_ms: float
