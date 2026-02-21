"""
Matching Service — Smart matching logic
"""
from typing import Dict, Any, List, Optional
from api.services import database_service


def smart_match_document(
    document_id: int,
    target_doc_type: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Find matching documents using smart matcher.

    Args:
        document_id: Source document ID
        target_doc_type: Optional target document type filter
        limit: Maximum number of matches

    Returns:
        List of matched documents with scores and explanations
    """
    try:
        from pipeline.smart_matcher import find_matches

        # Get source document
        source_doc = database_service.get_document_by_id(document_id)
        if not source_doc:
            return []

        # Find matches using existing smart matcher
        matches = find_matches(
            source_document=source_doc,
            target_type=target_doc_type,
            top_k=limit
        )

        # Format results
        results = []
        for match in matches:
            results.append({
                "document_id": match.get("document_id"),
                "title": match.get("title", ""),
                "doc_type": match.get("doc_type", ""),
                "confidence_score": match.get("score", 0.0),
                "match_reasoning": match.get("reasoning", ""),
                "suggestion": match.get("suggestion", ""),
                "metadata": match.get("metadata", {})
            })

        return results

    except Exception as e:
        # Fallback: return empty if smart matcher not available
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Smart matching failed: {e}")
        return []
