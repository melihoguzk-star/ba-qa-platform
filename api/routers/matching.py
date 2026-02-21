"""
Matching Router — Smart matching endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from api.services import matching_service, database_service

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
