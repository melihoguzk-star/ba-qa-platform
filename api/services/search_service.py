"""
Search Service — Hybrid search logic
"""
from typing import Optional
from api.schemas.search import SearchResult


def hybrid_search(
    query: str,
    doc_type_filter: Optional[str] = None,
    project_filter: Optional[int] = None,
    limit: int = 10
) -> list[SearchResult]:
    """
    Perform hybrid semantic + keyword search.

    Uses pipeline/hybrid_search.py for the actual search logic.
    """
    try:
        from pipeline.hybrid_search import hybrid_search_documents

        # Call existing hybrid search function
        raw_results = hybrid_search_documents(
            query=query,
            doc_type_filter=doc_type_filter,
            limit=limit,
            project_id_filter=project_filter
        )

        # Convert to SearchResult schema
        results = []
        for r in raw_results:
            results.append(SearchResult(
                document_id=r['document_id'],
                title=r.get('title', 'Untitled'),
                doc_type=r.get('doc_type', 'unknown'),
                score=r.get('score', 0.0),
                snippet=r.get('snippet', ''),
                metadata=r.get('metadata', {})
            ))

        return results

    except Exception as e:
        # Fallback: if hybrid search not available, return empty results
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Hybrid search failed: {e}")
        return []
