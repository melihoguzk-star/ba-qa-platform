"""
Matching Router — Smart matching endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from api.services import matching_service, database_service
from api.schemas.matching import (
    MatchSearchRequest,
    MatchSearchResponse,
    MatchAnalyticsResponse,
    RecordMatchRequest,
    MatchResult as TaskMatchResult,
    TaskFeatures,
    MatchBreakdown
)

router = APIRouter()


class MatchRequest(BaseModel):
    """Match request schema"""
    document_id: int = Field(..., description="Source document ID")
    target_doc_type: Optional[str] = Field(None, description="Target document type filter (ba/ta/tc)")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum number of matches")


class MatchResult(BaseModel):
    """Match result schema"""
    document_id: int
    title: str
    doc_type: str
    confidence_score: float
    match_reasoning: str
    suggestion: str
    metadata: Dict[str, Any] = {}


class MatchResponse(BaseModel):
    """Match response schema"""
    source_document_id: int
    source_title: str
    matches: List[MatchResult]
    total_found: int


@router.post("", response_model=MatchResponse)
async def match_documents(request: MatchRequest):
    """
    Find matching documents using AI-powered smart matcher.

    Uses combination of:
    - Semantic similarity (embeddings)
    - Structural analysis
    - Business rule matching
    - AI reasoning

    Useful for:
    - Finding related BA documents for a new task
    - Matching TC documents to BA requirements
    - Discovering similar technical implementations

    - **document_id**: Source document ID to match against
    - **target_doc_type**: Optional filter for target document type (ba/ta/tc)
    - **limit**: Maximum number of matches to return (1-50)

    Returns:
    - Ranked list of matching documents
    - Confidence scores (0-1)
    - AI-generated reasoning for each match
    - Suggested actions
    """
    # Validate source document exists
    source_doc = database_service.get_document_by_id(request.document_id)
    if not source_doc:
        raise HTTPException(
            status_code=404,
            detail=f"Source document with ID {request.document_id} not found"
        )

    try:
        # Find matches using smart matcher
        matches = matching_service.smart_match_document(
            document_id=request.document_id,
            target_doc_type=request.target_doc_type,
            limit=request.limit
        )

        # Format response
        return MatchResponse(
            source_document_id=request.document_id,
            source_title=source_doc.get('title', 'Untitled'),
            matches=matches,
            total_found=len(matches)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Matching failed: {str(e)}"
        )


# ═══════════════════════════════════════════════════════════════
# TASK-TO-DOCUMENT MATCHING (Smart Matching Page)
# ═══════════════════════════════════════════════════════════════

@router.post("/search", response_model=MatchSearchResponse)
async def search_task_matches(request: MatchSearchRequest):
    """
    Search for matching documents based on task description.

    Uses AI-powered task analysis and hybrid search to find relevant documents.

    This endpoint is used by the Smart Matching page where users describe
    a task and get suggestions for existing documents that might be relevant.
    """
    try:
        result = matching_service.search_matches(
            task_description=request.task_description,
            jira_key=request.jira_key,
            doc_type=request.doc_type,
            top_k=request.top_k
        )

        # Convert matches to Pydantic models
        match_results = []
        for match in result["matches"]:
            match_result = TaskMatchResult(
                document_id=match["document_id"],
                title=match["title"],
                doc_type=match["doc_type"],
                version=match.get("version", ""),
                confidence=match["confidence"],
                section_matched=match.get("section_matched", ""),
                match_breakdown=MatchBreakdown(**match["match_breakdown"]),
                task_features=TaskFeatures(**match["task_features"]),
                reasoning=match.get("reasoning", ""),
                suggestion=match.get("suggestion", "EVALUATE"),
                suggestion_reasoning=match.get("suggestion_reasoning", "")
            )
            match_results.append(match_result)

        return MatchSearchResponse(
            matches=match_results,
            task_features=TaskFeatures(**result["task_features"]) if result["task_features"] else TaskFeatures(),
            response_time=result["response_time"],
            total_found=result["total_found"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Match search failed: {str(e)}"
        )


@router.get("/analytics", response_model=MatchAnalyticsResponse)
async def get_match_analytics(time_range: str = "all"):
    """
    Get smart matching analytics.

    Query params:
        time_range: 7days, 30days, 90days, or all
    """
    valid_ranges = ["7days", "30days", "90days", "all"]
    if time_range not in valid_ranges:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid time_range. Must be one of: {', '.join(valid_ranges)}"
        )

    try:
        analytics = matching_service.get_analytics(time_range)
        return MatchAnalyticsResponse(**analytics)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch analytics: {str(e)}"
        )


@router.post("/record")
async def record_task_match(request: RecordMatchRequest):
    """
    Record a match interaction for analytics tracking.

    Used when user accepts or rejects a match suggestion.
    """
    try:
        match_id = matching_service.record_match_interaction(
            task_description=request.task_description,
            task_features=request.task_features,
            matched_document_id=request.matched_document_id,
            confidence_score=request.confidence_score,
            match_reasoning=request.match_reasoning,
            suggestion=request.suggestion,
            jira_key=request.jira_key,
            user_accepted=request.user_accepted
        )

        return {
            "match_id": match_id,
            "message": "Match interaction recorded successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record match: {str(e)}"
        )
