"""
Matching API Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class MatchSearchRequest(BaseModel):
    """Request schema for smart matching search"""
    task_description: str = Field(..., min_length=1, description="Task description to match against")
    jira_key: Optional[str] = Field(None, description="Optional JIRA key for context")
    doc_type: Optional[str] = Field(None, description="Document type filter (ba/ta/tc)")
    top_k: int = Field(5, ge=1, le=20, description="Number of top matches to return")


class TaskFeatures(BaseModel):
    """Task analysis features"""
    keywords: List[str] = Field(default_factory=list)
    intent: str = Field(default="ADD_FEATURE")
    scope: str = Field(default="Unknown")
    entities: List[str] = Field(default_factory=list)
    doc_type_relevance: Dict[str, float] = Field(default_factory=dict)
    complexity: str = Field(default="medium")
    search_query: str = Field(default="")
    analysis_method: Optional[str] = Field(None, description="rule_based or ai")


class MatchBreakdown(BaseModel):
    """Score breakdown for a match"""
    semantic_score: float = Field(..., ge=0, le=1)
    keyword_score: float = Field(..., ge=0, le=1)
    metadata_score: float = Field(..., ge=0, le=1)
    weights: Optional[Dict[str, float]] = None


class MatchResult(BaseModel):
    """Single match result"""
    document_id: int
    title: str
    doc_type: str
    version: str
    confidence: float = Field(..., ge=0, le=1)
    section_matched: str = Field(default="")
    match_breakdown: MatchBreakdown
    task_features: TaskFeatures
    reasoning: str = Field(default="")
    suggestion: str = Field(default="EVALUATE")
    suggestion_reasoning: str = Field(default="")


class MatchSearchResponse(BaseModel):
    """Response schema for smart matching search"""
    matches: List[MatchResult]
    task_features: TaskFeatures
    response_time: float = Field(..., description="Search time in seconds")
    total_found: int = Field(..., description="Total number of matches found")


class MatchAnalyticsResponse(BaseModel):
    """Response schema for match analytics"""
    total_matches: int
    total_accepted: int
    acceptance_rate: float
    avg_confidence: float


class RecordMatchRequest(BaseModel):
    """Request schema for recording a match interaction"""
    task_description: str
    task_features: Dict[str, Any]
    matched_document_id: Optional[int] = None
    confidence_score: float = Field(0.0, ge=0, le=1)
    match_reasoning: str = ""
    suggestion: str = ""
    jira_key: Optional[str] = None
    user_accepted: bool = False
