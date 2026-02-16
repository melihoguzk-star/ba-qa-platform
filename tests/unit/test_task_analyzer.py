"""
Unit tests for Task Analyzer module.

Tests AI-powered task feature extraction including keywords, intent,
scope, and document type relevance scoring.
"""

import pytest
from unittest.mock import Mock, patch
from pipeline.task_analyzer import TaskAnalyzer, analyze_task


class TestTaskAnalyzer:
    """Test suite for TaskAnalyzer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = TaskAnalyzer()

    def test_initialization(self):
        """Test TaskAnalyzer initialization."""
        assert self.analyzer is not None
        assert hasattr(self.analyzer, 'model')
        assert self.analyzer.model == "claude-sonnet-4-20250514"

    @patch('pipeline.task_analyzer.call_sonnet')
    def test_analyze_task_basic(self, mock_call_sonnet):
        """Test basic task analysis with mocked AI response."""
        # Mock AI response
        mock_call_sonnet.return_value = {
            'content': '''{
                "keywords": ["login", "authentication", "biometric"],
                "intent": "ADD_FEATURE",
                "scope": "Login Screen",
                "entities": ["Face ID", "Touch ID"],
                "doc_type_relevance": {"ba": 0.9, "ta": 0.7, "tc": 0.5},
                "complexity": "medium",
                "search_query": "biometric authentication login Face ID Touch ID"
            }'''
        }

        task = "Add Face ID authentication to login screen"
        result = self.analyzer.analyze_task(task)

        # Verify result structure
        assert isinstance(result, dict)
        assert 'keywords' in result
        assert 'intent' in result
        assert 'scope' in result
        assert 'entities' in result
        assert 'doc_type_relevance' in result
        assert 'complexity' in result
        assert 'search_query' in result

        # Verify content
        assert result['intent'] == 'ADD_FEATURE'
        assert 'login' in result['keywords']
        assert result['doc_type_relevance']['ba'] == 0.9

        # Verify AI was called
        mock_call_sonnet.assert_called_once()

    @patch('pipeline.task_analyzer.call_sonnet')
    def test_analyze_task_with_jira_key(self, mock_call_sonnet):
        """Test task analysis with JIRA key."""
        mock_call_sonnet.return_value = {
            'content': '''{
                "keywords": ["payment", "transfer"],
                "intent": "UPDATE_FEATURE",
                "scope": "Payment Module",
                "entities": ["IBAN", "Bank"],
                "doc_type_relevance": {"ba": 0.8, "ta": 0.6, "tc": 0.4},
                "complexity": "high",
                "search_query": "payment transfer IBAN bank"
            }'''
        }

        task = "Update payment transfer with IBAN validation"
        jira_key = "PROJ-123"
        result = self.analyzer.analyze_task(task, jira_key)

        assert result is not None
        assert result['intent'] == 'UPDATE_FEATURE'

        # Verify JIRA key was included in the call
        call_args = mock_call_sonnet.call_args
        assert jira_key in call_args[1]['user_content']

    @patch('pipeline.task_analyzer.call_sonnet')
    def test_analyze_task_fallback_on_invalid_json(self, mock_call_sonnet):
        """Test fallback when AI returns invalid JSON."""
        # Mock AI response with invalid JSON
        mock_call_sonnet.return_value = {
            'content': 'This is not valid JSON'
        }

        task = "Add new feature"
        result = self.analyzer.analyze_task(task)

        # Should return default structure with search_query
        assert isinstance(result, dict)
        assert 'search_query' in result
        assert result['search_query'] == task  # Fallback to original task

    @patch('pipeline.task_analyzer.call_sonnet')
    def test_analyze_task_handles_ai_error(self, mock_call_sonnet):
        """Test graceful handling of AI call errors."""
        # Mock AI error
        mock_call_sonnet.side_effect = Exception("API Error")

        task = "Add new feature"

        # Should raise exception (no fallback for API errors)
        with pytest.raises(Exception):
            self.analyzer.analyze_task(task)

    @patch('pipeline.task_analyzer.call_sonnet')
    def test_search_query_in_response(self, mock_call_sonnet):
        """Test that search_query is included in AI response."""
        mock_call_sonnet.return_value = {
            'content': '''{
                "keywords": ["login", "authentication"],
                "intent": "ADD_FEATURE",
                "scope": "Login Screen",
                "entities": ["Face ID"],
                "doc_type_relevance": {"ba": 0.9, "ta": 0.6, "tc": 0.3},
                "complexity": "medium",
                "search_query": "login authentication Face ID biometric"
            }'''
        }

        result = self.analyzer.analyze_task("Add Face ID to login")

        assert 'search_query' in result
        assert isinstance(result['search_query'], str)
        assert len(result['search_query']) > 0

    @patch('pipeline.task_analyzer.call_sonnet')
    def test_doc_type_relevance_scoring(self, mock_call_sonnet):
        """Test document type relevance scoring."""
        mock_call_sonnet.return_value = {
            'content': '''{
                "keywords": ["test", "case"],
                "intent": "ADD_FEATURE",
                "scope": "Testing",
                "entities": ["Selenium", "Pytest"],
                "doc_type_relevance": {"ba": 0.3, "ta": 0.4, "tc": 0.9},
                "complexity": "medium",
                "search_query": "test case selenium pytest"
            }'''
        }

        task = "Add automated test cases using Selenium"
        result = self.analyzer.analyze_task(task)

        # TC should have highest relevance for testing tasks
        assert result['doc_type_relevance']['tc'] > result['doc_type_relevance']['ba']
        assert result['doc_type_relevance']['tc'] > result['doc_type_relevance']['ta']

    @patch('pipeline.task_analyzer.call_sonnet')
    def test_intent_detection(self, mock_call_sonnet):
        """Test intent detection for different task types."""
        test_cases = [
            ("Add new login feature", "ADD_FEATURE"),
            ("Fix bug in payment module", "FIX_BUG"),
            ("Update dashboard layout", "UPDATE_FEATURE"),
        ]

        for task, expected_intent in test_cases:
            mock_call_sonnet.return_value = {
                'content': f'''{{
                    "keywords": ["test"],
                    "intent": "{expected_intent}",
                    "scope": "Module",
                    "entities": [],
                    "doc_type_relevance": {{"ba": 0.5, "ta": 0.5, "tc": 0.5}},
                    "complexity": "medium",
                    "search_query": "test"
                }}'''
            }

            result = self.analyzer.analyze_task(task)
            assert result['intent'] == expected_intent

    @patch('pipeline.task_analyzer.call_sonnet')
    def test_complexity_levels(self, mock_call_sonnet):
        """Test complexity level detection."""
        complexities = ["low", "medium", "high"]

        for complexity in complexities:
            mock_call_sonnet.return_value = {
                'content': f'''{{
                    "keywords": ["test"],
                    "intent": "ADD_FEATURE",
                    "scope": "Module",
                    "entities": [],
                    "doc_type_relevance": {{"ba": 0.5, "ta": 0.5, "tc": 0.5}},
                    "complexity": "{complexity}",
                    "search_query": "test"
                }}'''
            }

            result = self.analyzer.analyze_task("Test task")
            assert result['complexity'] == complexity

    @patch('pipeline.task_analyzer.call_sonnet')
    def test_prompt_caching_enabled(self, mock_call_sonnet):
        """Test that prompt caching is enabled for cost optimization."""
        mock_call_sonnet.return_value = {
            'content': '{"keywords": [], "intent": "ADD_FEATURE", "scope": "", "entities": [], "doc_type_relevance": {"ba": 0.5, "ta": 0.5, "tc": 0.5}, "complexity": "medium", "search_query": "test"}'
        }

        self.analyzer.analyze_task("Test task")

        # Verify use_caching parameter was set
        call_kwargs = mock_call_sonnet.call_args[1]
        assert call_kwargs.get('use_caching') is True


class TestAnalyzeTaskConvenienceFunction:
    """Test the convenience function."""

    @patch('pipeline.task_analyzer.TaskAnalyzer.analyze_task')
    def test_analyze_task_convenience_function(self, mock_analyze):
        """Test the module-level analyze_task function."""
        mock_analyze.return_value = {'search_query': 'test'}

        result = analyze_task("Test task", "PROJ-123")

        assert result is not None
        mock_analyze.assert_called_once_with("Test task", "PROJ-123")


class TestTaskAnalyzerEdgeCases:
    """Test edge cases and error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = TaskAnalyzer()

    @patch('pipeline.task_analyzer.call_sonnet')
    def test_empty_task_description(self, mock_call_sonnet):
        """Test handling of empty task description."""
        # Mock fallback response
        mock_call_sonnet.return_value = {
            'content': '''{
                "keywords": [],
                "intent": "UNKNOWN",
                "scope": "",
                "entities": [],
                "doc_type_relevance": {"ba": 0.5, "ta": 0.5, "tc": 0.5},
                "complexity": "low",
                "search_query": ""
            }'''
        }

        result = self.analyzer.analyze_task("")

        assert isinstance(result, dict)
        assert 'search_query' in result

    def test_very_long_task_description(self):
        """Test handling of very long task descriptions."""
        long_task = "Add feature " * 1000  # Very long description

        result = self.analyzer.analyze_task(long_task)

        assert isinstance(result, dict)
        assert 'search_query' in result

    @patch('pipeline.task_analyzer.call_sonnet')
    def test_unicode_in_task(self, mock_call_sonnet):
        """Test handling of Unicode characters in task description."""
        mock_call_sonnet.return_value = {
            'content': '{"keywords": ["kullanıcı", "profil"], "intent": "ADD_FEATURE", "scope": "Profil", "entities": [], "doc_type_relevance": {"ba": 0.8, "ta": 0.5, "tc": 0.3}, "complexity": "medium", "search_query": "kullanıcı profil"}'
        }

        task = "Kullanıcı profil sayfasına fotoğraf yükleme özelliği ekle"
        result = self.analyzer.analyze_task(task)

        assert result is not None
        assert 'kullanıcı' in result.get('keywords', [])

    @patch('pipeline.task_analyzer.call_sonnet')
    def test_special_characters_in_task(self, mock_call_sonnet):
        """Test handling of special characters."""
        mock_call_sonnet.return_value = {
            'content': '{"keywords": ["login"], "intent": "ADD_FEATURE", "scope": "Auth", "entities": [], "doc_type_relevance": {"ba": 0.7, "ta": 0.5, "tc": 0.3}, "complexity": "medium", "search_query": "login authentication"}'
        }

        task = "Add @login #authentication with $special %characters!"
        result = self.analyzer.analyze_task(task)

        assert result is not None
        assert isinstance(result, dict)
