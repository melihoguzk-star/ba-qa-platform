"""
📊 Document Matching Engine — Phase 2: Smart Matching & Recommendations

Hybrid approach combining:
1. TF-IDF keyword-based similarity (content matching)
2. Metadata matching (tags, JIRA keys, project)

No external APIs required - fully local implementation.
"""
import json
import re
from typing import List, Dict, Tuple, Optional
from collections import Counter
import math


class DocumentMatcher:
    """
    Hybrid document matching using TF-IDF + Metadata scoring.

    Similarity Score = (TF-IDF Score × 0.6) + (Metadata Score × 0.4)
    """

    def __init__(self):
        self.idf_cache = {}

    # ═══════════════════════════════════════════════════════════════
    # TEXT EXTRACTION
    # ═══════════════════════════════════════════════════════════════

    def extract_text_from_json(self, content_json: dict) -> str:
        """
        Extract all text content from BA/TA/TC JSON structure.

        Args:
            content_json: Document content in JSON format

        Returns:
            Concatenated text string
        """
        text_parts = []

        def recursive_extract(obj):
            """Recursively extract text from nested JSON"""
            if isinstance(obj, dict):
                for key, value in obj.items():
                    # Skip IDs and technical fields
                    if key in ['id', 'version', 'created_at', 'updated_at']:
                        continue
                    recursive_extract(value)
            elif isinstance(obj, list):
                for item in obj:
                    recursive_extract(item)
            elif isinstance(obj, str):
                # Clean and add text
                cleaned = self._clean_text(obj)
                if cleaned:
                    text_parts.append(cleaned)

        recursive_extract(content_json)
        return " ".join(text_parts)

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Convert to lowercase
        text = text.lower().strip()
        return text

    # ═══════════════════════════════════════════════════════════════
    # TF-IDF SIMILARITY
    # ═══════════════════════════════════════════════════════════════

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.

        Args:
            text: Input text string

        Returns:
            List of tokens (words)
        """
        # Split on non-alphanumeric characters
        tokens = re.findall(r'\b\w+\b', text.lower())

        # Remove very short tokens (< 3 chars) - likely noise
        tokens = [t for t in tokens if len(t) >= 3]

        # Remove common Turkish stopwords (basic set)
        stopwords = {
            'bir', 'bu', 've', 've', 'için', 'ile', 'olarak', 'ise', 'gibi',
            'the', 'is', 'at', 'which', 'on', 'and', 'or', 'not', 'are', 'was'
        }
        tokens = [t for t in tokens if t not in stopwords]

        return tokens

    def compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        """
        Compute Term Frequency (TF).

        TF(t) = (Number of times term t appears in document) / (Total number of terms)
        """
        total_terms = len(tokens)
        if total_terms == 0:
            return {}

        term_counts = Counter(tokens)
        return {term: count / total_terms for term, count in term_counts.items()}

    def compute_idf(self, documents_tokens: List[List[str]]) -> Dict[str, float]:
        """
        Compute Inverse Document Frequency (IDF).

        IDF(t) = log(Total documents / Documents containing term t)
        """
        total_docs = len(documents_tokens)
        if total_docs == 0:
            return {}

        # Count documents containing each term
        doc_freq = Counter()
        for tokens in documents_tokens:
            unique_terms = set(tokens)
            for term in unique_terms:
                doc_freq[term] += 1

        # Compute IDF
        idf = {}
        for term, freq in doc_freq.items():
            idf[term] = math.log(total_docs / freq)

        return idf

    def compute_tfidf_vector(self, tf: Dict[str, float], idf: Dict[str, float]) -> Dict[str, float]:
        """
        Compute TF-IDF vector.

        TF-IDF(t) = TF(t) × IDF(t)
        """
        return {term: tf_val * idf.get(term, 0) for term, tf_val in tf.items()}

    def cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """
        Compute cosine similarity between two TF-IDF vectors.

        cosine_similarity = (A · B) / (||A|| × ||B||)

        Returns:
            Similarity score between 0 and 1
        """
        # Get common terms
        common_terms = set(vec1.keys()) & set(vec2.keys())

        if not common_terms:
            return 0.0

        # Dot product
        dot_product = sum(vec1[term] * vec2[term] for term in common_terms)

        # Magnitudes
        magnitude1 = math.sqrt(sum(val ** 2 for val in vec1.values()))
        magnitude2 = math.sqrt(sum(val ** 2 for val in vec2.values()))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    # ═══════════════════════════════════════════════════════════════
    # METADATA SIMILARITY
    # ═══════════════════════════════════════════════════════════════

    def compute_metadata_score(
        self,
        doc1: Dict,
        doc2: Dict
    ) -> float:
        """
        Compute metadata-based similarity score.

        Scoring:
        - Tags match: 0.5 (high weight)
        - JIRA keys match: 0.3 (medium weight)
        - Same project: 0.2 (low weight - might be too similar)

        Returns:
            Metadata similarity score between 0 and 1
        """
        score = 0.0

        # Tags similarity (Jaccard index)
        tags1 = set(doc1.get('tags', []))
        tags2 = set(doc2.get('tags', []))

        if tags1 or tags2:
            intersection = len(tags1 & tags2)
            union = len(tags1 | tags2)
            tags_similarity = intersection / union if union > 0 else 0
            score += tags_similarity * 0.5

        # JIRA keys similarity (Jaccard index)
        jira1 = set(doc1.get('jira_keys', []))
        jira2 = set(doc2.get('jira_keys', []))

        if jira1 or jira2:
            intersection = len(jira1 & jira2)
            union = len(jira1 | jira2)
            jira_similarity = intersection / union if union > 0 else 0
            score += jira_similarity * 0.3

        # Same project (exact match, but not None)
        proj1 = doc1.get('project_id')
        proj2 = doc2.get('project_id')
        if proj1 is not None and proj2 is not None and proj1 == proj2:
            score += 0.2

        return min(score, 1.0)  # Cap at 1.0

    # ═══════════════════════════════════════════════════════════════
    # HYBRID MATCHING
    # ═══════════════════════════════════════════════════════════════

    def find_similar_documents(
        self,
        target_doc: Dict,
        candidate_docs: List[Dict],
        top_n: int = 5,
        min_score: float = 0.1
    ) -> List[Tuple[Dict, float, Dict]]:
        """
        Find similar documents using hybrid approach.

        Args:
            target_doc: Document to find matches for (with 'content_json' field)
            candidate_docs: List of candidate documents to compare against
            top_n: Number of top matches to return
            min_score: Minimum similarity score threshold

        Returns:
            List of tuples: (document, similarity_score, score_breakdown)
            Sorted by similarity score (descending)
        """
        if not candidate_docs:
            return []

        # Extract target document text
        target_text = self.extract_text_from_json(target_doc.get('content_json', {}))
        target_tokens = self.tokenize(target_text)

        # Extract all candidate texts and tokenize
        candidate_texts = []
        candidate_tokens_list = []

        for doc in candidate_docs:
            text = self.extract_text_from_json(doc.get('content_json', {}))
            tokens = self.tokenize(text)
            candidate_texts.append(text)
            candidate_tokens_list.append(tokens)

        # Compute IDF across all documents (target + candidates)
        all_tokens = [target_tokens] + candidate_tokens_list
        idf = self.compute_idf(all_tokens)

        # Compute target TF-IDF
        target_tf = self.compute_tf(target_tokens)
        target_tfidf = self.compute_tfidf_vector(target_tf, idf)

        # Compute similarities
        results = []

        for i, doc in enumerate(candidate_docs):
            # Skip same document (by ID)
            if doc.get('id') == target_doc.get('id'):
                continue

            # Skip different document types (BA should match BA, etc.)
            if doc.get('doc_type') != target_doc.get('doc_type'):
                continue

            # TF-IDF similarity
            candidate_tf = self.compute_tf(candidate_tokens_list[i])
            candidate_tfidf = self.compute_tfidf_vector(candidate_tf, idf)
            tfidf_score = self.cosine_similarity(target_tfidf, candidate_tfidf)

            # Metadata similarity
            metadata_score = self.compute_metadata_score(target_doc, doc)

            # Hybrid score: TF-IDF (60%) + Metadata (40%)
            hybrid_score = (tfidf_score * 0.6) + (metadata_score * 0.4)

            # Score breakdown
            breakdown = {
                'tfidf_score': round(tfidf_score, 3),
                'metadata_score': round(metadata_score, 3),
                'hybrid_score': round(hybrid_score, 3)
            }

            # Add to results if above threshold
            if hybrid_score >= min_score:
                results.append((doc, hybrid_score, breakdown))

        # Sort by hybrid score (descending)
        results.sort(key=lambda x: x[1], reverse=True)

        # Return top N
        return results[:top_n]

    def get_match_explanation(self, breakdown: Dict) -> str:
        """
        Generate human-readable explanation of match score.

        Args:
            breakdown: Score breakdown dict

        Returns:
            Explanation string
        """
        tfidf = breakdown['tfidf_score']
        metadata = breakdown['metadata_score']

        explanations = []

        if tfidf > 0.5:
            explanations.append("Strong content similarity")
        elif tfidf > 0.2:
            explanations.append("Moderate content similarity")
        else:
            explanations.append("Weak content similarity")

        if metadata > 0.5:
            explanations.append("matching tags/project")
        elif metadata > 0.2:
            explanations.append("some shared metadata")

        return " - " + ", ".join(explanations) if explanations else "Low similarity"


# ═══════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def find_similar(target_doc: Dict, candidate_docs: List[Dict], top_n: int = 5) -> List[Tuple[Dict, float, Dict]]:
    """
    Convenience function to find similar documents.

    Args:
        target_doc: Document to find matches for
        candidate_docs: List of candidate documents
        top_n: Number of results to return

    Returns:
        List of (document, score, breakdown) tuples
    """
    matcher = DocumentMatcher()
    return matcher.find_similar_documents(target_doc, candidate_docs, top_n=top_n)


def search_documents_tfidf(
    query_text: str,
    doc_type: Optional[str] = None,
    top_k: int = 20,
    min_score: float = 0.0
) -> List[Dict]:
    """
    Search documents using TF-IDF keyword matching.

    Args:
        query_text: Search query string
        doc_type: Document type filter ('ba', 'ta', 'tc', or None for all)
        top_k: Number of results to return
        min_score: Minimum TF-IDF score threshold

    Returns:
        List of documents with tfidf_score field, sorted by relevance

    Example:
        >>> results = search_documents_tfidf("enliq login", "ba", top_k=10)
        >>> for r in results:
        ...     print(f"Doc {r['document_id']}: {r['tfidf_score']:.2f}")
    """
    from data.database import get_documents_with_content

    # Fetch all documents of the specified type WITH content
    try:
        if doc_type:
            documents = get_documents_with_content(doc_type=doc_type, limit=1000)
        else:
            # Get all document types
            all_docs = []
            for dt in ['ba', 'ta', 'tc']:
                all_docs.extend(get_documents_with_content(doc_type=dt, limit=1000))
            documents = all_docs
    except Exception as e:
        print(f"Error fetching documents: {e}")
        return []

    if not documents:
        return []

    # Initialize matcher
    matcher = DocumentMatcher()

    # Tokenize query
    query_tokens = matcher.tokenize(query_text)
    if not query_tokens:
        return []

    # Extract all document texts and tokenize
    # IMPORTANT: Include title, tags, and content for better keyword matching
    doc_tokens_list = []
    for doc in documents:
        content_json = doc.get('content_json', {})
        if isinstance(content_json, str):
            import json
            content_json = json.loads(content_json)

        # Combine title + tags + content for comprehensive search
        text_parts = []

        # Add title (repeat 3x for higher weight)
        title = doc.get('title', '')
        if title:
            text_parts.extend([title, title, title])

        # Add tags (repeat 2x for medium weight)
        tags = doc.get('tags', [])
        if tags:
            tag_text = ' '.join(tags)
            text_parts.extend([tag_text, tag_text])

        # Add content (normal weight)
        content_text = matcher.extract_text_from_json(content_json)
        text_parts.append(content_text)

        # Combine all parts
        full_text = ' '.join(text_parts)
        tokens = matcher.tokenize(full_text)
        doc_tokens_list.append(tokens)

    # Compute IDF across query + all documents
    all_tokens = [query_tokens] + doc_tokens_list
    idf = matcher.compute_idf(all_tokens)

    # Compute query TF-IDF vector
    query_tf = matcher.compute_tf(query_tokens)
    query_tfidf = matcher.compute_tfidf_vector(query_tf, idf)

    # Score each document
    results = []
    for i, doc in enumerate(documents):
        # Compute document TF-IDF vector
        doc_tf = matcher.compute_tf(doc_tokens_list[i])
        doc_tfidf = matcher.compute_tfidf_vector(doc_tf, idf)

        # Compute cosine similarity
        tfidf_score = matcher.cosine_similarity(query_tfidf, doc_tfidf)

        # Filter by minimum score
        if tfidf_score < min_score:
            continue

        # Add result with standardized format
        result = {
            'document_id': doc.get('id'),
            'title': doc.get('title', 'Untitled'),
            'doc_type': doc.get('doc_type'),
            'project_id': doc.get('project_id'),
            'tfidf_score': round(tfidf_score, 4),
            'content_json': doc.get('content_json'),
            'metadata': {
                'tags': doc.get('tags', []),
                'jira_keys': doc.get('jira_keys', [])
            }
        }
        results.append(result)

    # Sort by TF-IDF score (descending)
    results.sort(key=lambda x: x['tfidf_score'], reverse=True)

    # Return top_k results
    return results[:top_k]
