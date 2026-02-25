"""
Matching Service — Smart document matching business logic
"""
import logging
import time
from typing import List, Dict, Optional, Any
from api.services import database_service

logger = logging.getLogger(__name__)

# BA/TA/TC relevance patterns for Drive file names
_RELEVANCE_PATTERNS = {
    "BA": ["ba", "brd", "business", "requirement", "gereksinim", "analiz"],
    "TA": ["ta", "technical", "teknik", "architecture", "mimari", "api", "endpoint"],
    "TC": ["tc", "test", "senaryo", "scenario", "case"],
}


def _tag_drive_relevance(file_name: str) -> str:
    """Assign a relevance tag to a Drive file based on filename patterns."""
    name_lower = file_name.lower()
    for tag, keywords in _RELEVANCE_PATTERNS.items():
        if any(kw in name_lower for kw in keywords):
            return tag
    return "GENEL"


async def search_matches(
    task_description: str,
    jira_key: Optional[str] = None,
    doc_type: Optional[str] = None,
    top_k: int = 5,
    source: str = "platform",
    mime_type_filter: str = "",
) -> Dict:
    """
    Search for matching documents using smart matcher.

    Args:
        task_description: Task description to match
        jira_key: Optional JIRA key
        doc_type: Optional document type filter (ba/ta/tc)
        top_k: Number of results to return
        source: "platform" | "drive" | "both"

    Returns:
        Dict with matches, task_features, response_time, total_found, drive_matches
    """
    start_time = time.time()
    platform_matches: List[Dict] = []
    task_features: Dict = {}
    drive_matches: List[Dict] = []

    # ── Platform search ──────────────────────────────────────────────
    if source in ("platform", "both"):
        try:
            from pipeline.smart_matcher import SmartMatcher
            matcher = SmartMatcher()
            platform_matches = matcher.find_matches_for_task(
                task_description=task_description,
                jira_key=jira_key,
                doc_type=doc_type,
                top_k=top_k,
            )
            if platform_matches:
                task_features = platform_matches[0].get("task_features", {})
        except Exception as e:
            logger.error(f"Platform smart match failed: {e}")

    # ── Drive search ─────────────────────────────────────────────────
    if source in ("drive", "both"):
        # Build search query — try TaskAnalyzer, fallback to task_description
        search_query = task_description[:200]
        try:
            from pipeline.task_analyzer import TaskAnalyzer
            analyzer = TaskAnalyzer()
            analysis = analyzer.analyze_task(task_description, jira_key)
            if not task_features:
                task_features = analysis
            search_query = analysis.get("search_query", "") or task_description[:200]
        except Exception as e:
            logger.warning(f"TaskAnalyzer failed, using raw query: {e}")

        try:
            from api.services.search_service import drive_search
            from api.services.drive_service import MIME_TYPE_MAP

            resolved_mime = MIME_TYPE_MAP.get(mime_type_filter or "", "")
            drive_results = await drive_search(
                search_query, mime_type=resolved_mime or None
            )
            for item in drive_results:
                drive_matches.append({
                    "name": item.get("name", ""),
                    "file_id": item.get("id", item.get("file_id", "")),
                    "webViewLink": item.get("webViewLink", ""),
                    "mimeType": item.get("mimeType", ""),
                    "modifiedTime": item.get("modifiedTime", ""),
                    "relevance_tag": _tag_drive_relevance(item.get("name", "")),
                    "size": item.get("size"),
                    "lastModifiedBy": item.get("lastModifiedBy", ""),
                    "createdTime": item.get("createdTime", ""),
                    "relevance_score": item.get("_relevance_score", 0),
                })
        except Exception as e:
            logger.error(f"Drive match search failed: {e}")

    response_time = time.time() - start_time

    return {
        "matches": platform_matches,
        "task_features": task_features,
        "response_time": response_time,
        "total_found": len(platform_matches),
        "drive_matches": drive_matches,
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
        from pipeline.smart_matcher import SmartMatcher

        # Get source document
        source_doc = database_service.get_document_by_id(document_id)
        if not source_doc:
            return []

        # Find matches using smart matcher
        matcher = SmartMatcher()
        title = source_doc.get("title", "")
        description = source_doc.get("description", "")
        task_text = f"{title} {description}".strip()
        raw_matches = matcher.find_matches_for_task(
            task_description=task_text,
            doc_type=target_doc_type,
            top_k=limit,
        )
        matches = raw_matches

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
