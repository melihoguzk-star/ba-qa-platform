"""
Unit tests for ChromaDB vector store.

Tests CRUD operations, search, and collection management.

Author: BA-QA Platform - Phase 2A
"""
import pytest
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from pipeline.vector_store import VectorStore, get_vector_store


@pytest.mark.unit
class TestVectorStore:
    """Test ChromaDB vector store operations."""

    @pytest.fixture
    def temp_chroma_dir(self):
        """Create temporary ChromaDB directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_chroma_client(self):
        """Mock ChromaDB client."""
        with patch('chromadb.PersistentClient') as mock_persistent_client:
            mock_client = Mock()
            mock_persistent_client.return_value = mock_client
            yield mock_client

    def test_singleton_pattern(self):
        """Test that get_vector_store returns the same instance."""
        store1 = get_vector_store()
        store2 = get_vector_store()
        assert store1 is store2

    def test_initialization(self, temp_chroma_dir):
        """Test vector store initialization."""
        store = VectorStore(persist_directory=temp_chroma_dir)
        assert store.persist_directory == temp_chroma_dir
        assert store._client is None  # Lazy loaded
        assert store._collections == {}

    @patch.dict('os.environ', {'CHROMA_DB_PATH': 'test/path'})
    def test_initialization_from_env(self):
        """Test initialization from environment variable."""
        store = VectorStore()
        assert store.persist_directory == 'test/path'

    def test_lazy_client_loading(self, temp_chroma_dir, mock_chroma_client):
        """Test that ChromaDB client is lazy loaded."""
        store = VectorStore(persist_directory=temp_chroma_dir)

        # Client not loaded yet
        assert store._client is None

        # Access client property
        client = store.client

        # Client should be loaded
        assert client is mock_chroma_client

    @patch('chromadb.PersistentClient')
    def test_get_collection(self, mock_persistent_client, temp_chroma_dir):
        """Test getting or creating a collection."""
        mock_client = Mock()
        mock_persistent_client.return_value = mock_client

        store = VectorStore(persist_directory=temp_chroma_dir)

        mock_collection = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection

        # Get BA collection
        collection = store.get_collection('ba')

        assert collection is mock_collection
        mock_client.get_or_create_collection.assert_called_once()

        # Call again - should return cached
        collection2 = store.get_collection('ba')
        assert collection2 is mock_collection
        # Should not call get_or_create_collection again
        assert mock_client.get_or_create_collection.call_count == 1

    def test_get_collection_invalid_type(self, temp_chroma_dir):
        """Test that invalid document type raises error."""
        store = VectorStore(persist_directory=temp_chroma_dir)

        with pytest.raises(ValueError, match="Invalid document type"):
            store.get_collection('invalid')

    def test_collection_names(self):
        """Test collection name mapping."""
        assert VectorStore.COLLECTIONS['ba'] == 'ba_documents'
        assert VectorStore.COLLECTIONS['ta'] == 'ta_documents'
        assert VectorStore.COLLECTIONS['tc'] == 'tc_documents'

    @patch('pipeline.chunking_strategy.get_chunker')
    @patch('pipeline.embedding_pipeline.get_embedding_pipeline')
    def test_index_document(self, mock_get_pipeline, mock_get_chunker,
                           temp_chroma_dir, mock_chroma_client, sample_ba_document):
        """Test document indexing."""
        store = VectorStore(persist_directory=temp_chroma_dir)

        # Mock chunker
        mock_chunker = Mock()
        mock_chunks = [
            {
                'document_id': 1,
                'chunk_index': 0,
                'chunk_type': 'ekran',
                'chunk_text': 'Screen: Login',
                'metadata': {'ekran_adi': 'Login'}
            }
        ]
        mock_chunker.chunk_document.return_value = mock_chunks
        mock_get_chunker.return_value = mock_chunker

        # Mock embedding pipeline
        mock_pipeline = Mock()
        mock_pipeline.embed_batch.return_value = [[0.1] * 768]
        mock_get_pipeline.return_value = mock_pipeline

        # Mock collection
        mock_collection = Mock()
        mock_collection.get.return_value = {'ids': []}
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        # Index document
        store.index_document(
            doc_id=1,
            doc_type='ba',
            content_json=sample_ba_document,
            metadata={'project_id': 1}
        )

        # Verify chunker was called
        mock_chunker.chunk_document.assert_called_once_with(
            1, 'ba', sample_ba_document, {'project_id': 1}
        )

        # Verify embeddings were generated
        mock_pipeline.embed_batch.assert_called_once()

        # Verify chunks were added to collection
        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args[1]
        assert len(call_args['ids']) == 1
        assert call_args['ids'][0] == 'doc1_chunk0'

    @patch('pipeline.chunking_strategy.get_chunker')
    def test_index_document_no_chunks(self, mock_get_chunker,
                                     temp_chroma_dir, mock_chroma_client):
        """Test indexing document with no chunks."""
        store = VectorStore(persist_directory=temp_chroma_dir)

        # Mock chunker returns empty list
        mock_chunker = Mock()
        mock_chunker.chunk_document.return_value = []
        mock_get_chunker.return_value = mock_chunker

        # Index document
        store.index_document(
            doc_id=1,
            doc_type='ba',
            content_json={"ekranlar": []}
        )

        # Should not create collection or add anything
        assert not mock_chroma_client.get_or_create_collection.called

    @patch('pipeline.embedding_pipeline.embed_text')
    def test_search(self, mock_embed_text, temp_chroma_dir, mock_chroma_client):
        """Test semantic search."""
        store = VectorStore(persist_directory=temp_chroma_dir)

        # Mock query embedding
        mock_embed_text.return_value = [0.5] * 768

        # Mock collection
        mock_collection = Mock()
        mock_collection.query.return_value = {
            'ids': [['doc1_chunk0', 'doc2_chunk1']],
            'documents': [['Screen: Login', 'Screen: Dashboard']],
            'distances': [[0.1, 0.2]],
            'metadatas': [[
                {'document_id': 1, 'ekran_adi': 'Login'},
                {'document_id': 2, 'ekran_adi': 'Dashboard'}
            ]]
        }
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        # Search
        results = store.search(
            query_text="login screen",
            doc_type='ba',
            top_k=10
        )

        # Verify results
        assert len(results) == 2

        first_result = results[0]
        assert first_result['id'] == 'doc1_chunk0'
        assert first_result['document_id'] == 1
        assert first_result['chunk_text'] == 'Screen: Login'
        assert 0.8 < first_result['similarity'] < 1.0  # 1 - 0.1 = 0.9

        # Verify query was called correctly
        mock_collection.query.assert_called_once()
        call_args = mock_collection.query.call_args[1]
        assert call_args['n_results'] == 10
        assert len(call_args['query_embeddings']) == 1

    @patch('pipeline.embedding_pipeline.embed_text')
    def test_search_with_filters(self, mock_embed_text, temp_chroma_dir, mock_chroma_client):
        """Test semantic search with metadata filters."""
        store = VectorStore(persist_directory=temp_chroma_dir)

        mock_embed_text.return_value = [0.5] * 768

        # Mock collection
        mock_collection = Mock()
        mock_collection.query.return_value = {
            'ids': [['doc1_chunk0']],
            'documents': [['Screen: Login']],
            'distances': [[0.1]],
            'metadatas': [[{'document_id': 1}]]
        }
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        # Search with filter
        results = store.search(
            query_text="login",
            doc_type='ba',
            top_k=5,
            filter_metadata={'project_id': 1}
        )

        # Verify filter was passed
        call_args = mock_collection.query.call_args[1]
        assert call_args['where'] == {'project_id': 1}

    @patch('pipeline.embedding_pipeline.embed_text')
    def test_search_no_results(self, mock_embed_text, temp_chroma_dir, mock_chroma_client):
        """Test search with no results."""
        store = VectorStore(persist_directory=temp_chroma_dir)

        mock_embed_text.return_value = [0.5] * 768

        # Mock collection with no results
        mock_collection = Mock()
        mock_collection.query.return_value = {
            'ids': [[]],
            'documents': [[]],
            'distances': [[]],
            'metadatas': [[]]
        }
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        # Search
        results = store.search(
            query_text="nonexistent",
            doc_type='ba'
        )

        assert results == []

    def test_delete_document(self, temp_chroma_dir, mock_chroma_client):
        """Test document deletion."""
        store = VectorStore(persist_directory=temp_chroma_dir)

        # Mock collection
        mock_collection = Mock()
        mock_collection.get.return_value = {
            'ids': ['doc1_chunk0', 'doc1_chunk1']
        }
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        # Delete document
        store.delete_document(doc_id=1, doc_type='ba')

        # Verify chunks were queried
        mock_collection.get.assert_called_once_with(
            where={'document_id': 1}
        )

        # Verify chunks were deleted
        mock_collection.delete.assert_called_once_with(
            ids=['doc1_chunk0', 'doc1_chunk1']
        )

    def test_delete_document_no_chunks(self, temp_chroma_dir, mock_chroma_client):
        """Test deleting document with no chunks."""
        store = VectorStore(persist_directory=temp_chroma_dir)

        # Mock collection with no chunks
        mock_collection = Mock()
        mock_collection.get.return_value = {'ids': []}
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        # Delete document
        store.delete_document(doc_id=1, doc_type='ba')

        # Should not call delete
        mock_collection.delete.assert_not_called()

    def test_get_collection_stats(self, temp_chroma_dir, mock_chroma_client):
        """Test collection statistics."""
        store = VectorStore(persist_directory=temp_chroma_dir)

        # Mock collections
        mock_ba_collection = Mock()
        mock_ba_collection.count.return_value = 100

        mock_ta_collection = Mock()
        mock_ta_collection.count.return_value = 50

        mock_tc_collection = Mock()
        mock_tc_collection.count.return_value = 75

        collections = {
            'ba_documents': mock_ba_collection,
            'ta_documents': mock_ta_collection,
            'tc_documents': mock_tc_collection
        }

        def get_or_create_collection(name, **kwargs):
            return collections[name]

        mock_chroma_client.get_or_create_collection.side_effect = get_or_create_collection

        # Get stats
        stats = store.get_collection_stats()

        assert len(stats) == 3
        assert stats['ba']['chunk_count'] == 100
        assert stats['ta']['chunk_count'] == 50
        assert stats['tc']['chunk_count'] == 75
        assert all(s['status'] == 'active' for s in stats.values())

    def test_get_collection_stats_single_type(self, temp_chroma_dir, mock_chroma_client):
        """Test statistics for single collection."""
        store = VectorStore(persist_directory=temp_chroma_dir)

        mock_collection = Mock()
        mock_collection.count.return_value = 42
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        # Get stats for BA only
        stats = store.get_collection_stats(doc_type='ba')

        assert len(stats) == 1
        assert stats['ba']['chunk_count'] == 42

    def test_clear_all_collections(self, temp_chroma_dir, mock_chroma_client):
        """Test clearing all collections."""
        store = VectorStore(persist_directory=temp_chroma_dir)

        # Clear all
        store.clear_all_collections()

        # Verify all collections were deleted
        assert mock_chroma_client.delete_collection.call_count == 3

        call_names = [
            call[1]['name'] for call in mock_chroma_client.delete_collection.call_args_list
        ]
        assert 'ba_documents' in call_names
        assert 'ta_documents' in call_names
        assert 'tc_documents' in call_names

    def test_metadata_json_serialization(self, temp_chroma_dir, mock_chroma_client,
                                        sample_ba_document):
        """Test that list/dict metadata is JSON serialized."""
        store = VectorStore(persist_directory=temp_chroma_dir)

        with patch('pipeline.chunking_strategy.get_chunker') as mock_get_chunker, \
             patch('pipeline.embedding_pipeline.get_embedding_pipeline') as mock_get_pipeline:

            # Mock chunker with list metadata
            mock_chunker = Mock()
            mock_chunks = [
                {
                    'document_id': 1,
                    'chunk_index': 0,
                    'chunk_type': 'ekran',
                    'chunk_text': 'Test',
                    'metadata': {
                        'tags': ['tag1', 'tag2'],  # List - should be serialized
                        'jira_keys': ['KEY-1'],     # List - should be serialized
                        'project_id': 1             # Int - should stay as is
                    }
                }
            ]
            mock_chunker.chunk_document.return_value = mock_chunks
            mock_get_chunker.return_value = mock_chunker

            # Mock embedding
            mock_pipeline = Mock()
            mock_pipeline.embed_batch.return_value = [[0.1] * 768]
            mock_get_pipeline.return_value = mock_pipeline

            # Mock collection
            mock_collection = Mock()
            mock_collection.get.return_value = {'ids': []}
            mock_chroma_client.get_or_create_collection.return_value = mock_collection

            # Index document
            store.index_document(1, 'ba', sample_ba_document)

            # Check that metadata was serialized
            call_args = mock_collection.add.call_args[1]
            metadata = call_args['metadatas'][0]

            import json
            assert metadata['tags'] == json.dumps(['tag1', 'tag2'])
            assert metadata['jira_keys'] == json.dumps(['KEY-1'])
            assert metadata['project_id'] == 1  # Int stays as int
