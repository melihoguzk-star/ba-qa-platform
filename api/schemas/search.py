"""
Search Schemas — Pydantic models for hybrid search
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class SearchRequest(BaseModel):
    """Search request schema"""
    query: str = Field(..., min_length=1)
    doc_type_filter: Optional[str] = Field(None, pattern="^(BRD|BA|TA|TC)$")
    project_filter: Optional[int] = None
    limit: int = Field(default=10, ge=1, le=100)
    source: str = Field(default="platform", pattern="^(platform|drive|both)$")


class SearchResult(BaseModel):
    """Individual search result"""
    document_id: int
    title: str
    doc_type: str
    score: float
    snippet: str
    metadata: Optional[dict] = None


class DriveResult(BaseModel):
    """Google Drive search result"""
    name: str
    file_id: str = ""
    webViewLink: str = ""
    mimeType: str = ""
    modifiedTime: str = ""
    size: Optional[str] = None


class SearchResponse(BaseModel):
    """Search response schema"""
    query: str
    platform_results: List[SearchResult] = Field(default_factory=list)
    drive_results: List[DriveResult] = Field(default_factory=list)
    total_found: int
    execution_time_ms: float


class DriveSearchRequest(BaseModel):
    """Dedicated Drive search request"""
    query: str = Field(..., min_length=1)
    folder_id: Optional[str] = None
    mime_type: Optional[str] = None


class ReindexStatusResponse(BaseModel):
    """Reindex status response"""
    status: str  # idle | running | completed | failed
    total: int = 0
    processed: int = 0
    errors: int = 0
    error_message: str = ""


class SearchStatsResponse(BaseModel):
    """Search/vector store stats"""
    ba: Optional[Dict[str, Any]] = None
    ta: Optional[Dict[str, Any]] = None
    tc: Optional[Dict[str, Any]] = None
    total_chunks: int = 0
