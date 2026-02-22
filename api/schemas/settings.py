"""
Settings API Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


# ============================================================================
# API Key Schemas
# ============================================================================

class GeminiKeyResponse(BaseModel):
    """Gemini API key (masked)"""
    index: int
    key_preview: str
    key_hash: str
    status: str = "unknown"  # active, quota_exceeded, invalid, unknown
    requests: int = 0
    errors: int = 0
    last_used: Optional[datetime] = None
    last_error: Optional[str] = None


class GeminiKeysListResponse(BaseModel):
    """List of Gemini keys"""
    keys: List[GeminiKeyResponse]
    total: int


class KeyTestRequest(BaseModel):
    """Test API key request"""
    key_index: int


class KeyTestResponse(BaseModel):
    """Test API key response"""
    is_valid: bool
    message: str


class AnthropicKeyResponse(BaseModel):
    """Anthropic API key (masked, read-only from environment)"""
    key_preview: str
    configured: bool


# ============================================================================
# Rotation Settings Schemas
# ============================================================================

class RotationSettingsResponse(BaseModel):
    """Key rotation settings"""
    strategy: str = "least_used"  # least_used, round_robin, random
    auto_reset_enabled: bool = True
    total_keys: int
    rotation_enabled: bool


class RotationSettingsRequest(BaseModel):
    """Update rotation settings"""
    strategy: Optional[str] = None
    auto_reset_enabled: Optional[bool] = None


class ResetKeysResponse(BaseModel):
    """Reset all keys response"""
    success: bool
    message: str
    keys_reset: int


# ============================================================================
# Statistics Schemas
# ============================================================================

class KeyStatistics(BaseModel):
    """Individual key statistics"""
    key_preview: str
    status: str
    requests: int
    errors: int
    last_used: Optional[str] = None
    last_error: Optional[str] = None


class UsageStatisticsResponse(BaseModel):
    """Overall usage statistics"""
    total_keys: int
    active_keys: int
    failed_keys: int
    total_requests: int
    total_errors: int
    keys: List[KeyStatistics]


# ============================================================================
# Vector Store Schemas
# ============================================================================

class VectorStoreConfigResponse(BaseModel):
    """Vector store configuration"""
    semantic_search_enabled: bool
    auto_indexing_enabled: bool
    embedding_model: str
    persist_directory: str


class CollectionStats(BaseModel):
    """Single collection statistics"""
    chunk_count: int
    status: str  # active, inactive, unknown


class VectorStoreStatsResponse(BaseModel):
    """Vector store statistics"""
    ba: CollectionStats
    ta: CollectionStats
    tc: CollectionStats
    total_chunks: int


class VectorSearchRequest(BaseModel):
    """Test semantic search request"""
    query: str = Field(..., min_length=1)
    doc_type: str = Field(..., pattern="^(ba|ta|tc)$")
    top_k: int = Field(default=5, ge=1, le=20)


class VectorSearchResult(BaseModel):
    """Single search result"""
    document_id: int
    similarity: float
    chunk_text: str
    metadata: Dict[str, Any]


class VectorSearchResponse(BaseModel):
    """Search results"""
    results: List[VectorSearchResult]
    total: int


# ============================================================================
# Smart Matching Analytics Schemas
# ============================================================================

class SuggestionBreakdown(BaseModel):
    """Suggestion breakdown item"""
    suggestion: Optional[str]
    count: int
    accepted: int


class DocTypeBreakdown(BaseModel):
    """Document type breakdown item"""
    doc_type: str
    count: int
    avg_confidence: float


class SmartMatchingAnalyticsResponse(BaseModel):
    """Smart matching analytics"""
    total_matches: int
    total_accepted: int
    acceptance_rate: float
    avg_confidence: float
    suggestion_breakdown: List[SuggestionBreakdown]
    doc_type_breakdown: List[DocTypeBreakdown]
