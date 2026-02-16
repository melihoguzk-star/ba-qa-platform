"""
Smart Matcher Module

Orchestrates hybrid document matching for tasks using semantic search,
keyword search, and metadata filtering.
"""

from typing import List, Dict, Optional
from pipeline.task_analyzer import TaskAnalyzer
from pipeline.hybrid_search import hybrid_search
from pipeline.match_explainer import MatchExplainer
from data.database import get_document_by_id


class SmartMatcher:
    """Orchestrates smart document matching for task descriptions."""

    def __init__(self):
        """Initialize the smart matcher."""
        self.task_analyzer = TaskAnalyzer()
        self.match_explainer = MatchExplainer()
        # Hybrid search weights
        self.alpha = 0.4  # 40% keyword, 60% semantic (alpha is keyword weight)
        self.confidence_threshold = 0.3  # Minimum confidence to return a match

    def find_matches_for_task(
        self,
        task_description: str,
        jira_key: Optional[str] = None,
        doc_type: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Find matching documents for a task description.

        Args:
            task_description: The task description to match
            jira_key: Optional JIRA key for context
            doc_type: Optional document type filter (ba/ta/tc)
            top_k: Number of top matches to return

        Returns:
            List of match dictionaries containing:
                - document_id: Document ID
                - title: Document title
                - doc_type: Document type
                - version: Document version
                - confidence: Overall confidence score (0-1)
                - section_matched: Best matching section/chunk
                - match_breakdown: Detailed score breakdown
                - task_features: Extracted task features
        """
        # Step 1: Analyze the task
        print(f"Analyzing task...")
        task_features = self.task_analyzer.analyze_task(task_description, jira_key)

        # Step 2: Perform hybrid search using the optimized query
        search_query = task_features.get("search_query", task_description)

        # If search_query is empty, use original task_description
        if not search_query or search_query == "...":
            search_query = task_description

        print(f"Searching with query: {search_query[:100]}...")

        # Perform hybrid search
        search_results = hybrid_search(
            query_text=search_query,
            doc_type=doc_type,
            top_k=top_k * 4,  # Get more results for filtering
            alpha=self.alpha
        )

        # Step 3: Calculate confidence scores and build match results
        matches = []
        for result in search_results:
            # Calculate confidence score
            confidence_score, breakdown = self._calculate_confidence(
                result,
                task_features,
                doc_type
            )

            # Filter by confidence threshold
            if confidence_score < self.confidence_threshold:
                continue

            # Build match result
            match = {
                "document_id": result["document_id"],
                "title": result.get("title", "Unknown"),
                "doc_type": result.get("doc_type", "unknown"),
                "version": result.get("version", ""),
                "confidence": confidence_score,
                "section_matched": result.get("chunk_text", "")[:300],  # First 300 chars
                "match_breakdown": breakdown,
                "task_features": task_features,
                "hybrid_score": result.get("combined_score", 0.0),
                "semantic_score": result.get("semantic_score", 0.0),
                "keyword_score": result.get("keyword_score", 0.0)
            }

            # Generate explanation and suggestion using match_explainer
            reasoning = self.match_explainer.explain_match(
                task_description=search_query,
                matched_doc=match,
                scores=breakdown
            )

            suggestion_result = self.match_explainer.suggest_action(
                task_features=task_features,
                matched_doc=match,
                confidence=confidence_score
            )

            # Add reasoning and suggestion to match
            match["reasoning"] = reasoning
            match["suggestion"] = suggestion_result["suggestion"]
            match["suggestion_reasoning"] = suggestion_result["reasoning"]

            matches.append(match)

        # Step 4: Sort by confidence and return top K
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        return matches[:top_k]

    def _calculate_confidence(
        self,
        search_result: Dict,
        task_features: Dict,
        doc_type_filter: Optional[str]
    ) -> tuple[float, Dict]:
        """
        Calculate confidence score for a match.

        Confidence = semantic(50%) + keyword(30%) + metadata(20%)

        Args:
            search_result: Search result from hybrid_search
            task_features: Extracted task features
            doc_type_filter: Document type filter if any

        Returns:
            Tuple of (confidence_score, breakdown_dict)
        """
        # Get base scores from hybrid search
        semantic_score = search_result.get("semantic_score", 0.0)
        keyword_score = search_result.get("keyword_score", 0.0)

        # Calculate metadata score based on doc type relevance
        doc_type = search_result.get("doc_type", "unknown")
        doc_type_relevance = task_features.get("doc_type_relevance", {})
        metadata_score = doc_type_relevance.get(doc_type, 0.5)

        # Boost if matches the doc_type filter
        if doc_type_filter and doc_type == doc_type_filter:
            metadata_score = min(1.0, metadata_score * 1.2)

        # Calculate weighted confidence
        confidence = (
            semantic_score * 0.5 +
            keyword_score * 0.3 +
            metadata_score * 0.2
        )

        # Normalize to [0, 1]
        confidence = max(0.0, min(1.0, confidence))

        # Build breakdown
        breakdown = {
            "semantic_score": semantic_score,
            "keyword_score": keyword_score,
            "metadata_score": metadata_score,
            "weights": {
                "semantic": 0.5,
                "keyword": 0.3,
                "metadata": 0.2
            }
        }

        return confidence, breakdown

    def get_match_with_details(self, match: Dict) -> Dict:
        """
        Enrich a match with full document details.

        Args:
            match: Match dictionary from find_matches_for_task

        Returns:
            Enriched match with full document details
        """
        doc_id = match["document_id"]
        document = get_document_by_id(doc_id)

        if document:
            match["project_name"] = document.get("project_name", "")
            match["created_at"] = document.get("created_at", "")
            match["updated_at"] = document.get("updated_at", "")
            match["file_path"] = document.get("file_path", "")

        return match


# Convenience function for quick matching
def find_matches_for_task(
    task_description: str,
    jira_key: Optional[str] = None,
    doc_type: Optional[str] = None,
    top_k: int = 5
) -> List[Dict]:
    """
    Find matching documents for a task description.

    Args:
        task_description: The task description to match
        jira_key: Optional JIRA key for context
        doc_type: Optional document type filter (ba/ta/tc)
        top_k: Number of top matches to return

    Returns:
        List of match dictionaries with confidence scores and details
    """
    matcher = SmartMatcher()
    return matcher.find_matches_for_task(task_description, jira_key, doc_type, top_k)
