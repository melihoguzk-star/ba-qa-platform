"""
Matching Service — Smart document matching business logic
"""
import time
from typing import List, Dict, Optional, Any
from api.services import database_service


def search_matches(
    task_description: str,
    jira_key: Optional[str] = None,
    doc_type: Optional[str] = None,
    top_k: int = 5
) -> Dict:
    """
    Search for matching documents using smart matcher.

    Args:
        task_description: Task description to match
        jira_key: Optional JIRA key
        doc_type: Optional document type filter (ba/ta/tc)
        top_k: Number of results to return

    Returns:
        Dict with matches, task_features, response_time, total_found
    """
    from pipeline.smart_matcher import SmartMatcher

    matcher = SmartMatcher()

    # Perform search with timing
    start_time = time.time()
    matches = matcher.find_matches_for_task(
        task_description=task_description,
        jira_key=jira_key,
        doc_type=doc_type,
        top_k=top_k
    )
    response_time = time.time() - start_time

    # Extract task features from first match (or empty if no matches)
    task_features = {}
    if matches:
        task_features = matches[0].get("task_features", {})

    return {
        "matches": matches,
        "task_features": task_features,
        "response_time": response_time,
        "total_found": len(matches)
    }


def get_analytics(time_range: str = "all") -> Dict:
    """
    Get smart matching analytics.

    Args:
        time_range: Time range filter (7days, 30days, 90days, all)

    Returns:
        Dict with analytics metrics
    """
    from data.database import get_task_match_analytics
    return get_task_match_analytics(time_range)


def record_match_interaction(
    task_description: str,
    task_features: Dict,
    matched_document_id: Optional[int] = None,
    confidence_score: float = 0.0,
    match_reasoning: str = "",
    suggestion: str = "",
    jira_key: Optional[str] = None,
    user_accepted: bool = False
) -> int:
    """
    Record a match interaction for analytics.

    Args:
        task_description: Task description
        task_features: Extracted task features
        matched_document_id: ID of matched document (None if no match)
        confidence_score: Match confidence score
        match_reasoning: Explanation of the match
        suggestion: Suggested action
        jira_key: Optional JIRA key
        user_accepted: Whether user accepted the match

    Returns:
        ID of created task_match record
    """
    from data.database import record_task_match
    return record_task_match(
        task_description=task_description,
        task_features=task_features,
        matched_document_id=matched_document_id,
        confidence_score=confidence_score,
        match_reasoning=match_reasoning,
        suggestion=suggestion,
        jira_key=jira_key,
        user_accepted=user_accepted
    )


def smart_match_document(
    document_id: int,
    target_doc_type: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Find matching documents using smart matcher (document-to-document).

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
