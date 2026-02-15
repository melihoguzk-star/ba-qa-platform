"""
Tests for Document Matching Engine (Phase 2)
Tests TF-IDF similarity, metadata matching, and hybrid scoring.
"""
import pytest
from pipeline.document_matching import DocumentMatcher, find_similar


class TestTextExtraction:
    """Test text extraction from JSON documents"""

    def test_extract_from_simple_json(self):
        """Should extract text from simple JSON structure"""
        matcher = DocumentMatcher()

        content = {
            "title": "User Login",
            "description": "Authentication system for users"
        }

        text = matcher.extract_text_from_json(content)
        assert "user login" in text.lower()
        assert "authentication system" in text.lower()

    def test_extract_from_nested_json(self):
        """Should extract text from nested JSON"""
        matcher = DocumentMatcher()

        content = {
            "ekranlar": [
                {
                    "ekran_adi": "Login Screen",
                    "fields": [
                        {"name": "email", "type": "text"},
                        {"name": "password", "type": "password"}
                    ]
                }
            ]
        }

        text = matcher.extract_text_from_json(content)
        assert "login screen" in text.lower()
        assert "email" in text.lower()
        assert "password" in text.lower()

    def test_skip_technical_fields(self):
        """Should skip ID and timestamp fields"""
        matcher = DocumentMatcher()

        content = {
            "id": "123",
            "created_at": "2024-01-01",
            "title": "Important Document"
        }

        text = matcher.extract_text_from_json(content)
        assert "123" not in text
        assert "2024" not in text
        assert "important document" in text.lower()

    def test_clean_text(self):
        """Should clean and normalize text"""
        matcher = DocumentMatcher()

        text = matcher._clean_text("  Multiple   Spaces  \n\n  And Lines  ")
        assert text == "multiple spaces and lines"


class TestTokenization:
    """Test tokenization and stopword removal"""

    def test_basic_tokenization(self):
        """Should tokenize text into words"""
        matcher = DocumentMatcher()

        tokens = matcher.tokenize("User authentication system for login")
        assert "user" in tokens
        assert "authentication" in tokens
        assert "system" in tokens
        assert "login" in tokens

    def test_remove_short_tokens(self):
        """Should remove tokens shorter than 3 characters"""
        matcher = DocumentMatcher()

        tokens = matcher.tokenize("I am a BA analyst")
        assert "i" not in tokens
        assert "am" not in tokens
        assert "a" not in tokens
        assert "analyst" in tokens

    def test_remove_stopwords(self):
        """Should remove common stopwords"""
        matcher = DocumentMatcher()

        tokens = matcher.tokenize("This is a user login system and it works")
        # Stopwords should be removed
        assert "bir" not in tokens  # Turkish stopword
        assert "the" not in tokens
        assert "and" not in tokens
        assert "is" not in tokens
        # Content words should remain
        assert "user" in tokens
        assert "login" in tokens
        assert "system" in tokens
        assert "works" in tokens

    def test_case_insensitive(self):
        """Should convert to lowercase"""
        matcher = DocumentMatcher()

        tokens = matcher.tokenize("USER Authentication SYSTEM")
        assert "user" in tokens
        assert "authentication" in tokens
        assert "system" in tokens


class TestTFIDFCalculation:
    """Test TF-IDF vector computation"""

    def test_compute_tf(self):
        """Should compute term frequency correctly"""
        matcher = DocumentMatcher()

        tokens = ["user", "login", "user", "system"]
        tf = matcher.compute_tf(tokens)

        assert tf["user"] == 0.5  # 2/4
        assert tf["login"] == 0.25  # 1/4
        assert tf["system"] == 0.25  # 1/4

    def test_compute_idf(self):
        """Should compute inverse document frequency"""
        matcher = DocumentMatcher()

        docs = [
            ["user", "login"],
            ["user", "system"],
            ["admin", "panel"]
        ]

        idf = matcher.compute_idf(docs)

        # "user" appears in 2 docs: log(3/2) ≈ 0.405
        assert 0.4 < idf["user"] < 0.5

        # "login" appears in 1 doc: log(3/1) ≈ 1.099
        assert 1.0 < idf["login"] < 1.2

    def test_compute_tfidf_vector(self):
        """Should compute TF-IDF vector"""
        matcher = DocumentMatcher()

        tf = {"user": 0.5, "login": 0.25}
        idf = {"user": 0.4, "login": 1.0}

        tfidf = matcher.compute_tfidf_vector(tf, idf)

        assert tfidf["user"] == pytest.approx(0.5 * 0.4)
        assert tfidf["login"] == pytest.approx(0.25 * 1.0)

    def test_empty_tokens(self):
        """Should handle empty token list"""
        matcher = DocumentMatcher()

        tf = matcher.compute_tf([])
        assert tf == {}


class TestCosineSimilarity:
    """Test cosine similarity calculation"""

    def test_identical_vectors(self):
        """Should return 1.0 for identical vectors"""
        matcher = DocumentMatcher()

        vec = {"user": 0.5, "login": 0.3}
        similarity = matcher.cosine_similarity(vec, vec)

        assert similarity == pytest.approx(1.0)

    def test_orthogonal_vectors(self):
        """Should return 0.0 for completely different vectors"""
        matcher = DocumentMatcher()

        vec1 = {"user": 0.5, "login": 0.3}
        vec2 = {"admin": 0.4, "panel": 0.6}

        similarity = matcher.cosine_similarity(vec1, vec2)
        assert similarity == 0.0

    def test_partial_overlap(self):
        """Should compute partial similarity"""
        matcher = DocumentMatcher()

        vec1 = {"user": 0.5, "login": 0.3, "system": 0.2}
        vec2 = {"user": 0.4, "login": 0.4, "admin": 0.2}

        similarity = matcher.cosine_similarity(vec1, vec2)
        assert 0 < similarity < 1

    def test_empty_vectors(self):
        """Should handle empty vectors"""
        matcher = DocumentMatcher()

        vec1 = {"user": 0.5}
        vec2 = {}

        similarity = matcher.cosine_similarity(vec1, vec2)
        assert similarity == 0.0


class TestMetadataScore:
    """Test metadata-based similarity scoring"""

    def test_matching_tags(self):
        """Should score high for matching tags"""
        matcher = DocumentMatcher()

        doc1 = {"tags": ["authentication", "security", "login"]}
        doc2 = {"tags": ["authentication", "security"]}

        score = matcher.compute_metadata_score(doc1, doc2)
        assert score > 0.3  # Tags have 0.5 weight

    def test_matching_jira_keys(self):
        """Should score for matching JIRA keys"""
        matcher = DocumentMatcher()

        doc1 = {"jira_keys": ["PROJ-123", "PROJ-456"]}
        doc2 = {"jira_keys": ["PROJ-123"]}

        score = matcher.compute_metadata_score(doc1, doc2)
        assert score > 0.1  # JIRA keys have 0.3 weight

    def test_same_project(self):
        """Should score for same project"""
        matcher = DocumentMatcher()

        doc1 = {"project_id": 1}
        doc2 = {"project_id": 1}

        score = matcher.compute_metadata_score(doc1, doc2)
        assert score == 0.2  # Project has 0.2 weight

    def test_combined_metadata(self):
        """Should combine all metadata scores"""
        matcher = DocumentMatcher()

        doc1 = {
            "tags": ["auth", "login"],
            "jira_keys": ["PROJ-123"],
            "project_id": 1
        }
        doc2 = {
            "tags": ["auth", "login"],
            "jira_keys": ["PROJ-123"],
            "project_id": 1
        }

        score = matcher.compute_metadata_score(doc1, doc2)
        assert score == 1.0  # Perfect metadata match

    def test_no_metadata(self):
        """Should return 0 for no metadata"""
        matcher = DocumentMatcher()

        doc1 = {}
        doc2 = {}

        score = matcher.compute_metadata_score(doc1, doc2)
        assert score == 0.0


class TestHybridMatching:
    """Test hybrid matching with real-world scenarios"""

    def test_find_similar_basic(self):
        """Should find similar documents"""
        target = {
            "id": 1,
            "doc_type": "ba",
            "content_json": {"title": "User Login System", "description": "Authentication flow"},
            "tags": ["auth", "login"],
            "project_id": 1
        }

        candidates = [
            {
                "id": 2,
                "doc_type": "ba",
                "content_json": {"title": "User Authentication", "description": "Login process"},
                "tags": ["auth"],
                "project_id": 1
            },
            {
                "id": 3,
                "doc_type": "ba",
                "content_json": {"title": "Admin Panel", "description": "Dashboard management"},
                "tags": ["admin"],
                "project_id": 2
            }
        ]

        matcher = DocumentMatcher()
        results = matcher.find_similar_documents(target, candidates, top_n=2)

        assert len(results) > 0
        # First result should be more similar (auth-related)
        assert results[0][0]["id"] == 2
        assert results[0][1] > 0.3  # Reasonable similarity score

    def test_skip_same_document(self):
        """Should skip the same document by ID"""
        target = {
            "id": 1,
            "doc_type": "ba",
            "content_json": {"title": "User authentication login system for users"},
            "tags": []
        }

        candidates = [
            {"id": 1, "doc_type": "ba", "content_json": {"title": "User authentication login system for users"}, "tags": []},
            {"id": 2, "doc_type": "ba", "content_json": {"title": "User authentication login process workflow"}, "tags": []}
        ]

        matcher = DocumentMatcher()
        results = matcher.find_similar_documents(target, candidates, min_score=0.0)

        # Should only return doc ID 2 (skip ID 1 which is same document)
        assert len(results) == 1
        assert results[0][0]["id"] == 2

    def test_skip_different_doc_type(self):
        """Should only match same document type"""
        target = {
            "id": 1,
            "doc_type": "ba",
            "content_json": {"title": "User login authentication system for secure access"},
            "tags": []
        }

        candidates = [
            {"id": 2, "doc_type": "tc", "content_json": {"title": "User login authentication system for secure access"}, "tags": []},
            {"id": 3, "doc_type": "ba", "content_json": {"title": "User login authentication process workflow"}, "tags": []}
        ]

        matcher = DocumentMatcher()
        results = matcher.find_similar_documents(target, candidates, min_score=0.0)

        # Should only return BA document (skip TC even if content matches)
        assert len(results) == 1
        assert results[0][0]["id"] == 3

    def test_min_score_threshold(self):
        """Should filter by minimum score"""
        target = {
            "id": 1,
            "doc_type": "ba",
            "content_json": {"title": "Very specific unique content"},
            "tags": []
        }

        candidates = [
            {"id": 2, "doc_type": "ba", "content_json": {"title": "Completely different"}, "tags": []}
        ]

        matcher = DocumentMatcher()
        results = matcher.find_similar_documents(target, candidates, min_score=0.5)

        # Should return nothing (low similarity)
        assert len(results) == 0

    def test_top_n_limit(self):
        """Should respect top_n limit"""
        target = {
            "id": 1,
            "doc_type": "ba",
            "content_json": {"title": "Test"},
            "tags": ["test"]
        }

        candidates = [
            {"id": i, "doc_type": "ba", "content_json": {"title": "Test"}, "tags": ["test"]}
            for i in range(2, 12)  # 10 candidates
        ]

        matcher = DocumentMatcher()
        results = matcher.find_similar_documents(target, candidates, top_n=3)

        assert len(results) == 3

    def test_hybrid_score_breakdown(self):
        """Should provide score breakdown"""
        target = {
            "id": 1,
            "doc_type": "ba",
            "content_json": {"title": "User Login"},
            "tags": ["auth"]
        }

        candidates = [
            {
                "id": 2,
                "doc_type": "ba",
                "content_json": {"title": "User Login System"},
                "tags": ["auth"]
            }
        ]

        matcher = DocumentMatcher()
        results = matcher.find_similar_documents(target, candidates)

        assert len(results) > 0
        doc, score, breakdown = results[0]

        # Check breakdown structure
        assert "tfidf_score" in breakdown
        assert "metadata_score" in breakdown
        assert "hybrid_score" in breakdown

        # Verify hybrid calculation (60% TF-IDF + 40% metadata)
        expected = (breakdown["tfidf_score"] * 0.6) + (breakdown["metadata_score"] * 0.4)
        assert breakdown["hybrid_score"] == pytest.approx(expected, abs=0.01)


class TestConvenienceFunction:
    """Test the convenience wrapper function"""

    def test_find_similar_wrapper(self):
        """Should work as a simple wrapper"""
        target = {
            "id": 1,
            "doc_type": "ba",
            "content_json": {"title": "User authentication system for login process"},
            "tags": ["auth"],
            "project_id": 1
        }

        candidates = [
            {
                "id": 2,
                "doc_type": "ba",
                "content_json": {"title": "User authentication workflow and login process"},
                "tags": ["auth"],
                "project_id": 1
            }
        ]

        results = find_similar(target, candidates, top_n=5)
        assert len(results) > 0
        assert isinstance(results[0], tuple)
        assert len(results[0]) == 3  # (doc, score, breakdown)
