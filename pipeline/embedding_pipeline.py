"""
Embedding Pipeline for Semantic Search

Generates vector embeddings using sentence-transformers (multilingual-e5-base).
Supports lazy loading, session caching, and batch processing.

Author: BA-QA Platform
Date: 2026-02-16
"""
import logging
import os
from typing import List, Optional
import hashlib

logger = logging.getLogger(__name__)


class EmbeddingPipeline:
    """Generate embeddings for semantic search using multilingual model."""

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize embedding pipeline with lazy model loading.

        Args:
            model_name: Hugging Face model ID (default: multilingual-e5-base)
        """
        self.model_name = model_name or os.getenv(
            'EMBEDDING_MODEL',
            'intfloat/multilingual-e5-base'
        )
        self._model = None  # Lazy loaded
        self._cache = {}    # Session cache: hash -> embedding

    @property
    def model(self):
        """Lazy load the embedding model on first use."""
        if self._model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
                logger.info("Embedding model loaded successfully")
            except ImportError:
                raise ImportError(
                    "sentence-transformers not installed. "
                    "Run: pip install sentence-transformers"
                )
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise

        return self._model

    def embed_text(self, text: str, use_cache: bool = True) -> List[float]:
        """
        Generate embedding for a single text string.

        Args:
            text: Input text to embed
            use_cache: Whether to use session cache

        Returns:
            768-dimensional embedding vector
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return [0.0] * 768  # Return zero vector

        # Check cache
        if use_cache:
            text_hash = self._hash_text(text)
            if text_hash in self._cache:
                logger.debug(f"Cache hit for text: {text[:50]}...")
                return self._cache[text_hash]

        # Generate embedding
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            embedding_list = embedding.tolist()

            # Cache result
            if use_cache:
                self._cache[text_hash] = embedding_list

            return embedding_list

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    def embed_batch(self, texts: List[str], batch_size: Optional[int] = None,
                    use_cache: bool = True) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing).

        Args:
            texts: List of input texts
            batch_size: Batch size for processing (default: from env or 32)
            use_cache: Whether to use session cache

        Returns:
            List of 768-dimensional embedding vectors
        """
        if not texts:
            return []

        batch_size = batch_size or int(os.getenv('CHROMA_MAX_BATCH_SIZE', 32))

        # Check cache for all texts - create result list with None placeholders
        embeddings = [None] * len(texts)
        texts_to_embed = []
        text_indices = []

        for i, text in enumerate(texts):
            if not text or not text.strip():
                embeddings[i] = [0.0] * 768
                continue

            if use_cache:
                text_hash = self._hash_text(text)
                if text_hash in self._cache:
                    embeddings[i] = self._cache[text_hash]
                    continue

            # Need to generate embedding
            texts_to_embed.append(text)
            text_indices.append(i)

        # Generate embeddings for cache misses
        if texts_to_embed:
            try:
                logger.info(f"Generating embeddings for {len(texts_to_embed)} texts")
                batch_embeddings = self.model.encode(
                    texts_to_embed,
                    batch_size=batch_size,
                    convert_to_numpy=True,
                    show_progress_bar=len(texts_to_embed) > 10
                )

                # Insert embeddings at correct positions
                for idx, text_idx in enumerate(text_indices):
                    embedding_list = batch_embeddings[idx].tolist()
                    embeddings[text_idx] = embedding_list

                    # Cache results
                    if use_cache:
                        text_hash = self._hash_text(texts_to_embed[idx])
                        self._cache[text_hash] = embedding_list

            except Exception as e:
                logger.error(f"Failed to generate batch embeddings: {e}")
                raise

        return embeddings

    def clear_cache(self):
        """Clear session embedding cache."""
        cache_size = len(self._cache)
        self._cache.clear()
        logger.info(f"Cleared {cache_size} cached embeddings")

    def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        return {
            'cached_embeddings': len(self._cache),
            'model_loaded': self._model is not None,
            'model_name': self.model_name
        }

    @staticmethod
    def _hash_text(text: str) -> str:
        """Generate hash for text caching."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()


# Singleton instance (per session)
_pipeline = None


def get_embedding_pipeline() -> EmbeddingPipeline:
    """Get singleton embedding pipeline instance."""
    global _pipeline
    if _pipeline is None:
        _pipeline = EmbeddingPipeline()
    return _pipeline


def embed_text(text: str) -> List[float]:
    """Convenience function: embed single text."""
    pipeline = get_embedding_pipeline()
    return pipeline.embed_text(text)


def embed_batch(texts: List[str], batch_size: Optional[int] = None) -> List[List[float]]:
    """Convenience function: embed batch of texts."""
    pipeline = get_embedding_pipeline()
    return pipeline.embed_batch(texts, batch_size=batch_size)


# Async indexing helper (for auto-indexing hooks)
def index_document_async(doc_id: int, content_json: dict, doc_type: str, metadata: dict = None):
    """
    Async helper for auto-indexing documents in ChromaDB.
    Called from database.py after document creation.

    Args:
        doc_id: Document ID
        content_json: Document content JSON
        doc_type: Document type ('ba', 'ta', 'tc')
        metadata: Additional metadata (tags, jira_keys, project_id, etc.)
    """
    try:
        # Import here to avoid circular dependencies
        from pipeline.vector_store import get_vector_store

        logger.info(f"Auto-indexing document {doc_id} (type: {doc_type})")
        vector_store = get_vector_store()
        vector_store.index_document(doc_id, doc_type, content_json, metadata)
        logger.info(f"Document {doc_id} indexed successfully")

    except Exception as e:
        logger.error(f"Failed to auto-index document {doc_id}: {e}")
        # Don't raise - auto-indexing failures shouldn't block document creation
