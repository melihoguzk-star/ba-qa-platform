"""
Unit tests for embedding pipeline.

Tests embedding generation, caching, and batch processing.

Author: BA-QA Platform - Phase 2A
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pipeline.embedding_pipeline import (
    EmbeddingPipeline,
    get_embedding_pipeline,
    embed_text,
    embed_batch
)


@pytest.mark.unit
class TestEmbeddingPipeline:
    """Test embedding generation pipeline."""

    def test_singleton_pattern(self):
        """Test that get_embedding_pipeline returns the same instance."""
        pipeline1 = get_embedding_pipeline()
        pipeline2 = get_embedding_pipeline()
        assert pipeline1 is pipeline2

    def test_initialization(self):
        """Test pipeline initialization with default model."""
        pipeline = EmbeddingPipeline()
        assert pipeline.model_name == 'intfloat/multilingual-e5-base'
        assert pipeline._model is None  # Lazy loaded
        assert pipeline._cache == {}

    def test_initialization_custom_model(self):
        """Test pipeline initialization with custom model."""
        pipeline = EmbeddingPipeline(model_name='custom/model')
        assert pipeline.model_name == 'custom/model'

    @patch.dict('os.environ', {'EMBEDDING_MODEL': 'test/model'})
    def test_initialization_from_env(self):
        """Test pipeline initialization from environment variable."""
        pipeline = EmbeddingPipeline()
        assert pipeline.model_name == 'test/model'

    def test_lazy_model_loading(self):
        """Test that model is loaded only when accessed."""
        pipeline = EmbeddingPipeline()

        # Model not loaded yet
        assert pipeline._model is None

        # Mock sentence_transformers at import location
        with patch('sentence_transformers.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_st.return_value = mock_model

            # Access model property
            model = pipeline.model

            # Model should be loaded
            assert model is mock_model
            mock_st.assert_called_once_with('intfloat/multilingual-e5-base')

    def test_embed_text_basic(self):
        """Test basic text embedding."""
        pipeline = EmbeddingPipeline()

        # Mock the model
        mock_model = Mock()
        mock_embedding = Mock()
        mock_embedding.tolist.return_value = [0.1] * 768
        mock_model.encode.return_value = mock_embedding

        pipeline._model = mock_model

        # Embed text
        embedding = pipeline.embed_text("test text")

        assert len(embedding) == 768
        assert all(isinstance(x, float) for x in embedding)
        mock_model.encode.assert_called_once_with("test text", convert_to_numpy=True)

    def test_embed_text_empty(self):
        """Test embedding empty text returns zero vector."""
        pipeline = EmbeddingPipeline()
        embedding = pipeline.embed_text("")

        assert len(embedding) == 768
        assert all(x == 0.0 for x in embedding)

    def test_embed_text_caching(self):
        """Test that embeddings are cached."""
        pipeline = EmbeddingPipeline()

        # Mock the model
        mock_model = Mock()
        mock_embedding = Mock()
        mock_embedding.tolist.return_value = [0.1] * 768
        mock_model.encode.return_value = mock_embedding

        pipeline._model = mock_model

        # Embed same text twice
        text = "test text"
        embedding1 = pipeline.embed_text(text, use_cache=True)
        embedding2 = pipeline.embed_text(text, use_cache=True)

        # Should be same object (from cache)
        assert embedding1 is embedding2

        # Model should only be called once
        assert mock_model.encode.call_count == 1

    def test_embed_text_no_cache(self):
        """Test embedding without cache."""
        pipeline = EmbeddingPipeline()

        # Mock the model
        mock_model = Mock()
        mock_embedding = Mock()
        mock_embedding.tolist.return_value = [0.1] * 768
        mock_model.encode.return_value = mock_embedding

        pipeline._model = mock_model

        # Embed same text twice without cache
        text = "test text"
        embedding1 = pipeline.embed_text(text, use_cache=False)
        embedding2 = pipeline.embed_text(text, use_cache=False)

        # Model should be called twice
        assert mock_model.encode.call_count == 2

    def test_embed_batch_basic(self):
        """Test batch embedding."""
        pipeline = EmbeddingPipeline()

        # Mock the model
        mock_model = Mock()
        import numpy as np
        mock_embeddings = np.array([[0.1] * 768, [0.2] * 768, [0.3] * 768])
        mock_model.encode.return_value = mock_embeddings

        pipeline._model = mock_model

        # Embed batch
        texts = ["text1", "text2", "text3"]
        embeddings = pipeline.embed_batch(texts, batch_size=32, use_cache=False)

        assert len(embeddings) == 3
        assert all(len(emb) == 768 for emb in embeddings)

        # Check model was called with correct parameters
        mock_model.encode.assert_called_once()
        call_args = mock_model.encode.call_args
        assert call_args[1]['batch_size'] == 32
        assert call_args[1]['convert_to_numpy'] is True

    def test_embed_batch_with_empty_texts(self):
        """Test batch embedding with empty texts."""
        pipeline = EmbeddingPipeline()

        # Mock the model
        mock_model = Mock()
        import numpy as np
        mock_embeddings = np.array([[0.1] * 768, [0.2] * 768])  # Two embeddings (text1, text2)
        mock_model.encode.return_value = mock_embeddings

        pipeline._model = mock_model

        # Embed batch with empty text
        texts = ["text1", "", "text2"]
        embeddings = pipeline.embed_batch(texts, use_cache=False)

        assert len(embeddings) == 3

        # Empty text should have zero vector
        assert all(x == 0.0 for x in embeddings[1])

    def test_embed_batch_caching(self):
        """Test batch embedding uses cache."""
        pipeline = EmbeddingPipeline()

        # Mock the model - return embeddings for ALL texts in batch (including duplicates)
        mock_model = Mock()
        import numpy as np

        # First call: 3 texts (text1, text2, text1)
        mock_embeddings_first = np.array([[0.1] * 768, [0.2] * 768, [0.1] * 768])
        mock_model.encode.return_value = mock_embeddings_first

        pipeline._model = mock_model

        # First batch - no cache yet
        texts = ["text1", "text2", "text1"]  # text1 appears twice
        embeddings = pipeline.embed_batch(texts, use_cache=True)

        assert len(embeddings) == 3
        assert mock_model.encode.call_count == 1

        # Second call - all should come from cache now
        embeddings2 = pipeline.embed_batch(texts, use_cache=True)
        assert mock_model.encode.call_count == 1  # No new calls - used cache

        # Verify results are the same
        assert len(embeddings2) == 3

    def test_embed_batch_empty_list(self):
        """Test batch embedding with empty list."""
        pipeline = EmbeddingPipeline()
        embeddings = pipeline.embed_batch([])
        assert embeddings == []

    def test_clear_cache(self):
        """Test cache clearing."""
        pipeline = EmbeddingPipeline()

        # Add some items to cache
        pipeline._cache = {
            'hash1': [0.1] * 768,
            'hash2': [0.2] * 768
        }

        assert len(pipeline._cache) == 2

        # Clear cache
        pipeline.clear_cache()

        assert len(pipeline._cache) == 0

    def test_get_cache_stats(self):
        """Test cache statistics."""
        pipeline = EmbeddingPipeline()

        # Initially empty
        stats = pipeline.get_cache_stats()
        assert stats['cached_embeddings'] == 0
        assert stats['model_loaded'] is False
        assert stats['model_name'] == 'intfloat/multilingual-e5-base'

        # Add cache item
        pipeline._cache = {'hash1': [0.1] * 768}

        stats = pipeline.get_cache_stats()
        assert stats['cached_embeddings'] == 1

    def test_hash_text(self):
        """Test text hashing for cache keys."""
        from pipeline.embedding_pipeline import EmbeddingPipeline

        # Same text should produce same hash
        hash1 = EmbeddingPipeline._hash_text("test text")
        hash2 = EmbeddingPipeline._hash_text("test text")
        assert hash1 == hash2

        # Different text should produce different hash
        hash3 = EmbeddingPipeline._hash_text("different text")
        assert hash1 != hash3

    def test_convenience_functions(self):
        """Test convenience functions use singleton."""
        with patch('pipeline.embedding_pipeline.get_embedding_pipeline') as mock_get:
            mock_pipeline = Mock()
            mock_pipeline.embed_text.return_value = [0.1] * 768
            mock_pipeline.embed_batch.return_value = [[0.1] * 768]
            mock_get.return_value = mock_pipeline

            # Test embed_text
            result = embed_text("test")
            mock_pipeline.embed_text.assert_called_once_with("test")

            # Test embed_batch
            result = embed_batch(["test1", "test2"], batch_size=16)
            mock_pipeline.embed_batch.assert_called_once_with(
                ["test1", "test2"],
                batch_size=16
            )

    @patch('pipeline.vector_store.get_vector_store')
    def test_index_document_async(self, mock_get_store):
        """Test async indexing helper."""
        from pipeline.embedding_pipeline import index_document_async

        mock_store = Mock()
        mock_get_store.return_value = mock_store

        # Call async indexing
        content = {"ekranlar": []}
        metadata = {"project_id": 1}
        index_document_async(doc_id=1, content_json=content, doc_type='ba', metadata=metadata)

        # Should call vector store
        mock_store.index_document.assert_called_once_with(1, 'ba', content, metadata)

    @patch('pipeline.vector_store.get_vector_store')
    def test_index_document_async_error_handling(self, mock_get_store):
        """Test async indexing handles errors gracefully."""
        from pipeline.embedding_pipeline import index_document_async

        mock_store = Mock()
        mock_store.index_document.side_effect = Exception("Indexing failed")
        mock_get_store.return_value = mock_store

        # Should not raise exception
        try:
            index_document_async(doc_id=1, content_json={}, doc_type='ba')
        except Exception:
            pytest.fail("index_document_async should not raise exceptions")
