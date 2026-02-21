"""
Search Router — Hybrid search endpoints
"""
from fastapi import APIRouter, HTTPException
from api.schemas.search import SearchRequest, SearchResponse, SearchResult
from api.services import search_service
import time

router = APIRouter()


@router.post("", response_model=SearchResponse)
def search_documents(request: SearchRequest):
    """
    Perform hybrid semantic + keyword search across documents.

    Uses combination of:
    - Semantic search (vector similarity via ChromaDB)
    - Keyword search (TF-IDF)
    - Metadata filtering

    - **query**: Search query (required)
    - **doc_type_filter**: Filter by document type (ba/ta/tc, optional)
    - **project_filter**: Filter by project ID (optional)
    - **limit**: Maximum number of results (1-100)
    """
    start_time = time.time()

    try:
        results = search_service.hybrid_search(
            query=request.query,
            doc_type_filter=request.doc_type_filter,
            project_filter=request.project_filter,
            limit=request.limit
        )

        execution_time = (time.time() - start_time) * 1000  # Convert to ms

        return SearchResponse(
            query=request.query,
            results=results,
            total_found=len(results),
            execution_time_ms=round(execution_time, 2)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )
