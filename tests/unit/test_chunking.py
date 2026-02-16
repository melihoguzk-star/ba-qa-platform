"""
Unit tests for document chunking strategy.

Tests BA, TA, TC document chunking with size limits and metadata.

Author: BA-QA Platform - Phase 2A
"""
import pytest
from pipeline.chunking_strategy import DocumentChunker, get_chunker


@pytest.mark.unit
class TestDocumentChunker:
    """Test document chunking strategies."""

    def test_singleton_pattern(self):
        """Test that get_chunker returns the same instance."""
        chunker1 = get_chunker()
        chunker2 = get_chunker()
        assert chunker1 is chunker2

    def test_chunk_ba_document_screens(self, sample_ba_document):
        """Test BA document chunking by screens."""
        chunker = DocumentChunker()
        chunks = chunker.chunk_document(
            doc_id=1,
            doc_type='ba',
            content_json=sample_ba_document,
            metadata={'project_id': 1, 'tags': ['test']}
        )

        # Should have 2 screen chunks + 1 backend operation
        assert len(chunks) >= 2

        # Check first screen chunk
        screen_chunks = [c for c in chunks if c['chunk_type'] == 'ekran']
        assert len(screen_chunks) == 2

        first_chunk = screen_chunks[0]
        assert first_chunk['document_id'] == 1
        assert first_chunk['chunk_index'] == 0
        assert 'Login Screen' in first_chunk['chunk_text']
        assert 'Email input' in first_chunk['chunk_text']
        assert first_chunk['metadata']['ekran_adi'] == 'Login Screen'
        assert first_chunk['metadata']['project_id'] == 1

    def test_chunk_ba_document_backend_operations(self, sample_ba_document):
        """Test BA document chunking includes backend operations."""
        chunker = DocumentChunker()
        chunks = chunker.chunk_document(
            doc_id=1,
            doc_type='ba',
            content_json=sample_ba_document
        )

        # Check backend operation chunks
        backend_chunks = [c for c in chunks if c['chunk_type'] == 'backend_operation']
        assert len(backend_chunks) == 1

        backend_chunk = backend_chunks[0]
        assert 'User Authentication' in backend_chunk['chunk_text']
        assert '/api/auth/login' in backend_chunk['chunk_text']
        assert backend_chunk['metadata']['method'] == 'POST'

    def test_chunk_tc_document(self, sample_tc_document):
        """Test TC document chunking by test scenarios."""
        chunker = DocumentChunker()
        chunks = chunker.chunk_document(
            doc_id=2,
            doc_type='tc',
            content_json=sample_tc_document,
            metadata={'project_id': 1}
        )

        assert len(chunks) == 1
        chunk = chunks[0]

        assert chunk['document_id'] == 2
        assert chunk['chunk_type'] == 'test_case'
        assert 'TC001' in chunk['chunk_text']
        assert 'Successful Login' in chunk['chunk_text']
        assert 'Open login page' in chunk['chunk_text']
        assert chunk['metadata']['test_id'] == 'TC001'
        assert chunk['metadata']['step_count'] == 3

    def test_chunk_ta_document_endpoints(self):
        """Test TA document chunking by API endpoints."""
        ta_content = {
            "servisler": [
                {
                    "servis_adi": "Auth Service",
                    "aciklama": "Authentication service",
                    "teknolojiler": ["Node.js", "JWT"],
                    "endpoints": [
                        {
                            "path": "/api/login",
                            "method": "POST",
                            "aciklama": "User login endpoint"
                        },
                        {
                            "path": "/api/logout",
                            "method": "POST",
                            "aciklama": "User logout endpoint"
                        }
                    ]
                }
            ]
        }

        chunker = DocumentChunker()
        chunks = chunker.chunk_document(
            doc_id=3,
            doc_type='ta',
            content_json=ta_content
        )

        # Should have 2 endpoint chunks
        endpoint_chunks = [c for c in chunks if c['chunk_type'] == 'endpoint']
        assert len(endpoint_chunks) == 2

        # Check first endpoint
        first_chunk = endpoint_chunks[0]
        assert 'Auth Service' in first_chunk['chunk_text']
        assert '/api/login' in first_chunk['chunk_text']
        assert 'POST' in first_chunk['chunk_text']
        assert first_chunk['metadata']['servis_adi'] == 'Auth Service'
        assert first_chunk['metadata']['endpoint'] == '/api/login'

    def test_chunk_ta_document_data_entities(self):
        """Test TA document chunking includes data entities."""
        ta_content = {
            "servisler": [],
            "veri_modeli": [
                {
                    "entity": "User",
                    "fields": [
                        {"name": "id", "type": "int", "required": True},
                        {"name": "email", "type": "string", "required": True},
                        {"name": "name", "type": "string", "required": False}
                    ]
                }
            ]
        }

        chunker = DocumentChunker()
        chunks = chunker.chunk_document(
            doc_id=4,
            doc_type='ta',
            content_json=ta_content
        )

        # Should have 1 data entity chunk
        entity_chunks = [c for c in chunks if c['chunk_type'] == 'data_entity']
        assert len(entity_chunks) == 1

        entity_chunk = entity_chunks[0]
        assert 'User' in entity_chunk['chunk_text']
        assert 'id: int' in entity_chunk['chunk_text']
        assert entity_chunk['metadata']['entity_name'] == 'User'
        assert entity_chunk['metadata']['field_count'] == 3

    def test_empty_document(self):
        """Test chunking empty document returns empty list."""
        chunker = DocumentChunker()

        # Empty BA document
        chunks = chunker.chunk_document(
            doc_id=5,
            doc_type='ba',
            content_json={"ekranlar": [], "backend_islemler": []}
        )
        assert chunks == []

        # Empty TC document
        chunks = chunker.chunk_document(
            doc_id=6,
            doc_type='tc',
            content_json={"test_scenarios": []}
        )
        assert chunks == []

    def test_chunk_size_estimation(self):
        """Test token estimation and size limits."""
        chunker = DocumentChunker()

        # Test _estimate_tokens
        text = "This is a test" * 100  # ~1400 chars
        tokens = chunker._estimate_tokens(text)
        assert 300 < tokens < 400  # ~350 tokens

        # Test _truncate_text
        long_text = "x" * 10000
        truncated = chunker._truncate_text(long_text, max_tokens=100)
        assert len(truncated) <= 400 + 3  # 100 tokens * 4 chars + "..."

    def test_invalid_document_type(self):
        """Test that invalid document type raises error."""
        chunker = DocumentChunker()

        with pytest.raises(ValueError, match="Unsupported document type"):
            chunker.chunk_document(
                doc_id=1,
                doc_type='invalid',
                content_json={}
            )

    def test_chunk_metadata_inheritance(self):
        """Test that metadata is inherited by chunks."""
        chunker = DocumentChunker()
        metadata = {
            'project_id': 123,
            'tags': ['important', 'mobile'],
            'jira_keys': ['PROJ-123']
        }

        chunks = chunker.chunk_document(
            doc_id=1,
            doc_type='ba',
            content_json={
                "ekranlar": [
                    {
                        "ekran_adi": "Test Screen",
                        "aciklama": "Test",
                        "ui_elementleri": []
                    }
                ],
                "backend_islemler": []
            },
            metadata=metadata
        )

        assert len(chunks) == 1
        chunk = chunks[0]

        # Check metadata inheritance
        assert chunk['metadata']['project_id'] == 123
        assert chunk['metadata']['tags'] == ['important', 'mobile']
        assert chunk['metadata']['jira_keys'] == ['PROJ-123']

    def test_tc_document_with_test_cases_key(self):
        """Test TC document using 'test_cases' instead of 'test_scenarios'."""
        tc_content = {
            "test_cases": [
                {
                    "test_id": "TC-001",
                    "test_name": "Login Test",
                    "description": "Test login functionality",
                    "priority": "High",
                    "steps": [
                        {"step": 1, "action": "Open app", "expected": "App loads"},
                        {"step": 2, "action": "Enter credentials", "expected": "Form filled"}
                    ],
                    "expected_result": "User logged in"
                }
            ]
        }

        chunker = DocumentChunker()
        chunks = chunker.chunk_document(
            doc_id=7,
            doc_type='tc',
            content_json=tc_content
        )

        assert len(chunks) == 1
        chunk = chunks[0]
        assert 'TC-001' in chunk['chunk_text']
        assert 'Login Test' in chunk['chunk_text']
        assert 'High' in chunk['chunk_text']
        assert 'Open app' in chunk['chunk_text']

    def test_chunk_index_sequence(self, sample_ba_document):
        """Test that chunk indices are sequential."""
        chunker = DocumentChunker()
        chunks = chunker.chunk_document(
            doc_id=1,
            doc_type='ba',
            content_json=sample_ba_document
        )

        # Check indices are sequential
        indices = [c['chunk_index'] for c in chunks]
        assert indices == list(range(len(chunks)))
        assert indices[0] == 0
        assert indices[-1] == len(chunks) - 1
