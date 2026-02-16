"""
Hybrid Search: Combine TF-IDF (keyword) + Semantic (meaning) search results.

Uses Reciprocal Rank Fusion (RRF) algorithm to merge rankings from different
search methods, giving better results than either method alone.

Example:
    >>> from pipeline.hybrid_search import hybrid_search
    >>> results = hybrid_search("enliq login", doc_type="ba", alpha=0.7)
    >>> # alpha=0.7 means 70% keyword, 30% semantic
"""

import logging
from typing import List, Dict, Optional, Any
import os

logger = logging.getLogger(__name__)


def reciprocal_rank_fusion(
    rankings: List[List[Dict]],
    k: int = 60
) -> List[Dict]:
    """
    Reciprocal Rank Fusion algorithm to combine multiple search rankings.

    RRF formula: score(d) = sum(1 / (k + rank(d)))
    where rank(d) is the position of document d in each ranking.

    Args:
        rankings: List of result lists from different search methods
                 Each result should have 'document_id' field
        k: Constant to prevent division by zero (default: 60, from literature)

    Returns:
        Fused ranking sorted by RRF score (highest first)

    Example:
        >>> keyword_results = [{'document_id': 1}, {'document_id': 2}]
        >>> semantic_results = [{'document_id': 2}, {'document_id': 3}]
        >>> fused = reciprocal_rank_fusion([keyword_results, semantic_results])
    """
    if not rankings:
        return []

    # Score accumulator: {document_id: {rrf_score, doc_data}}
    scores = {}

    for ranking in rankings:
        for rank, doc in enumerate(ranking, start=1):
            doc_id = doc.get('document_id')
            if doc_id is None:
                continue

            rrf_score = 1.0 / (k + rank)

            if doc_id not in scores:
                scores[doc_id] = {
                    'rrf_score': 0.0,
                    'doc': doc,
                    'ranks': []
                }

            scores[doc_id]['rrf_score'] += rrf_score
            scores[doc_id]['ranks'].append(rank)

    # Sort by RRF score (descending)
    fused_results = []
    for doc_id, data in sorted(scores.items(), key=lambda x: x[1]['rrf_score'], reverse=True):
        result = data['doc'].copy()
        result['rrf_score'] = data['rrf_score']
        result['ranks'] = data['ranks']  # Show where doc appeared in each ranking
        fused_results.append(result)

    return fused_results


def weighted_fusion(
    keyword_results: List[Dict],
    semantic_results: List[Dict],
    alpha: float = 0.5
) -> List[Dict]:
    """
    Weighted fusion of keyword and semantic results.

    Args:
        keyword_results: Results from TF-IDF search (have 'tfidf_score')
        semantic_results: Results from vector search (have 'similarity')
        alpha: Weight for keyword (0.0 = only semantic, 1.0 = only keyword)

    Returns:
        Fused results sorted by combined score

    Note:
        alpha=0.5 means 50% keyword + 50% semantic (balanced)
        alpha=0.7 means 70% keyword + 30% semantic (prefer exact matches)
        alpha=0.3 means 30% keyword + 70% semantic (prefer meaning)
    """
    if alpha < 0 or alpha > 1:
        raise ValueError("alpha must be between 0 and 1")

    # Normalize scores to 0-1 range
    def normalize_scores(results, score_key):
        if not results:
            return []
        scores = [r.get(score_key, 0) for r in results]
        max_score = max(scores) if scores else 1
        min_score = min(scores) if scores else 0
        score_range = max_score - min_score if max_score != min_score else 1

        normalized = []
        for r in results:
            r_copy = r.copy()
            raw_score = r.get(score_key, 0)
            r_copy['normalized_score'] = (raw_score - min_score) / score_range if score_range > 0 else 0
            normalized.append(r_copy)
        return normalized

    # Normalize both result sets
    keyword_normalized = normalize_scores(keyword_results, 'tfidf_score')
    semantic_normalized = normalize_scores(semantic_results, 'similarity')

    # Combine scores
    combined = {}

    for result in keyword_normalized:
        doc_id = result['document_id']
        combined[doc_id] = {
            'doc': result,
            'keyword_score': result['normalized_score'],
            'semantic_score': 0.0
        }

    for result in semantic_normalized:
        doc_id = result['document_id']
        if doc_id not in combined:
            combined[doc_id] = {
                'doc': result,
                'keyword_score': 0.0,
                'semantic_score': result['normalized_score']
            }
        else:
            # Document exists in both - use semantic result for chunk info
            combined[doc_id]['doc'] = result  # Override with semantic result (has chunk_text)
            combined[doc_id]['semantic_score'] = result['normalized_score']

    # Calculate weighted score
    fused_results = []
    for doc_id, data in combined.items():
        result = data['doc'].copy()
        result['keyword_score'] = data['keyword_score']
        result['semantic_score'] = data['semantic_score']
        result['hybrid_score'] = alpha * data['keyword_score'] + (1 - alpha) * data['semantic_score']
        fused_results.append(result)

    # Sort by hybrid score (descending)
    fused_results.sort(key=lambda x: x['hybrid_score'], reverse=True)

    return fused_results


def hybrid_search(
    query_text: str,
    doc_type: str,
    top_k: int = 20,
    alpha: float = 0.5,
    fusion_method: str = 'weighted',
    similarity_threshold: float = 0.0,
    tfidf_search_func: Optional[callable] = None
) -> List[Dict]:
    """
    Hybrid search combining keyword (TF-IDF) and semantic (vector) search.

    Args:
        query_text: Search query
        doc_type: Document type ('ba', 'ta', 'tc', or None for all)
        top_k: Number of results to return
        alpha: Weight for keyword search (0.0-1.0)
               - 0.5 = balanced (default)
               - 0.7 = prefer keyword matches
               - 0.3 = prefer semantic matches
        fusion_method: 'weighted' or 'rrf' (Reciprocal Rank Fusion)
        similarity_threshold: Minimum similarity for semantic results (0.0-1.0)
        tfidf_search_func: Optional custom TF-IDF search function
                          If None, uses default from pipeline.document_matching

    Returns:
        List of document results with hybrid scores

    Example:
        >>> results = hybrid_search("enliq login", "ba", alpha=0.7)
        >>> # Returns documents with "enliq" highly ranked
    """
    from pipeline.vector_store import get_vector_store

    # Get semantic results
    vector_store = get_vector_store()
    logger.info(f"Hybrid search: query='{query_text}', doc_type={doc_type}, alpha={alpha}")

    try:
        semantic_results = vector_store.search(
            query_text=query_text,
            doc_type=doc_type,
            top_k=top_k * 2  # Get more results for fusion
        )

        # Apply similarity threshold
        if similarity_threshold > 0:
            semantic_results = [
                r for r in semantic_results
                if r.get('similarity', 0) >= similarity_threshold
            ]

        logger.info(f"Semantic search found {len(semantic_results)} results")
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        semantic_results = []

    # Get keyword results
    try:
        if tfidf_search_func:
            keyword_results = tfidf_search_func(query_text, doc_type, top_k * 2)
        else:
            # Use default TF-IDF search from document_matching
            from pipeline.document_matching import search_documents_tfidf
            keyword_results = search_documents_tfidf(query_text, doc_type, top_k * 2)

        logger.info(f"Keyword search found {len(keyword_results)} results")
    except Exception as e:
        logger.error(f"Keyword search failed: {e}")
        keyword_results = []

    # If one method failed, return the other
    if not semantic_results and not keyword_results:
        logger.warning("Both search methods failed, returning empty results")
        return []
    elif not semantic_results:
        logger.info("Only keyword results available")
        return keyword_results[:top_k]
    elif not keyword_results:
        logger.info("Only semantic results available")
        return semantic_results[:top_k]

    # Fusion
    if fusion_method == 'rrf':
        logger.info("Using Reciprocal Rank Fusion")
        fused = reciprocal_rank_fusion([keyword_results, semantic_results])
    else:  # weighted (default)
        logger.info(f"Using weighted fusion (alpha={alpha})")
        fused = weighted_fusion(keyword_results, semantic_results, alpha)

    # Return top_k results
    return fused[:top_k]


# Default configuration from environment
DEFAULT_ALPHA = float(os.getenv('HYBRID_SEARCH_ALPHA', '0.5'))
DEFAULT_SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', '0.7'))
DEFAULT_FUSION_METHOD = os.getenv('HYBRID_FUSION_METHOD', 'weighted')


def search_with_defaults(
    query_text: str,
    doc_type: str,
    top_k: int = 20
) -> List[Dict]:
    """
    Hybrid search with default configuration from environment variables.

    Uses:
        - HYBRID_SEARCH_ALPHA (default: 0.5)
        - SIMILARITY_THRESHOLD (default: 0.7)
        - HYBRID_FUSION_METHOD (default: 'weighted')
    """
    return hybrid_search(
        query_text=query_text,
        doc_type=doc_type,
        top_k=top_k,
        alpha=DEFAULT_ALPHA,
        fusion_method=DEFAULT_FUSION_METHOD,
        similarity_threshold=DEFAULT_SIMILARITY_THRESHOLD
    )
