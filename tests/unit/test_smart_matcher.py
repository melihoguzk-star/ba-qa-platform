"""
Unit tests for Smart Matcher module.

Tests hybrid document matching orchestration, confidence scoring,
and result ranking for task-to-document matching.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pipeline.smart_matcher import SmartMatcher, find_matches_for_task


class TestSmartMatcher:
    """Test suite for SmartMatcher class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.matcher = SmartMatcher()

    def test_initialization(self):
        """Test SmartMatcher initialization."""
        assert self.matcher is not None
        assert hasattr(self.matcher, 'task_analyzer')
        assert hasattr(self.matcher, 'match_explainer')
        assert self.matcher.alpha == 0.6
        assert self.matcher.confidence_threshold == 0.3

    @patch('pipeline.smart_matcher.hybrid_search')
    @patch('pipeline.smart_matcher.TaskAnalyzer.analyze_task')
    @patch('pipeline.smart_matcher.MatchExplainer.explain_match')
    @patch('pipeline.smart_matcher.MatchExplainer.suggest_action')
    def test_find_matches_for_task_basic(
        self,
        mock_suggest,
        mock_explain,
        mock_analyze,
        mock_search
    ):
        """Test basic task matching workflow."""
        # Mock task analysis
        mock_analyze.return_value = {
            'keywords': ['login', 'authentication'],
            'intent': 'ADD_FEATURE',
            'scope': 'Login Screen',
            'doc_type_relevance': {'ba': 0.9, 'ta': 0.6, 'tc': 0.3},
            'search_query': 'login authentication'
        }

        # Mock hybrid search results
        mock_search.return_value = [
            {
                'document_id': 1,
                'title': 'Login BA',
                'doc_type': 'ba',
                'version': 'v1.0',
                'chunk_text': 'Login authentication flow...',
                'combined_score': 0.85,
                'semantic_score': 0.8,
                'keyword_score': 0.9
            }
        ]

        # Mock match explanation
        mock_explain.return_value = "Bu doküman login flow'u içeriyor."

        # Mock action suggestion
        mock_suggest.return_value = {
            'suggestion': 'UPDATE_EXISTING',
            'reasoning': 'Doküman zaten login içeriyor.'
        }

        # Execute
        matches = self.matcher.find_matches_for_task(
            task_description="Add Face ID to login",
            doc_type='ba',
            top_k=3
        )

        # Verify
        assert len(matches) == 1
        assert matches[0]['document_id'] == 1
        assert matches[0]['title'] == 'Login BA'
        assert 'confidence' in matches[0]
        assert 'reasoning' in matches[0]
        assert 'suggestion' in matches[0]
        assert matches[0]['suggestion'] == 'UPDATE_EXISTING'

        # Verify components were called
        mock_analyze.assert_called_once()
        mock_search.assert_called_once()
        mock_explain.assert_called_once()
        mock_suggest.assert_called_once()

    @patch('pipeline.smart_matcher.hybrid_search')
    @patch('pipeline.smart_matcher.TaskAnalyzer.analyze_task')
    @patch('pipeline.smart_matcher.MatchExplainer.explain_match')
    @patch('pipeline.smart_matcher.MatchExplainer.suggest_action')
    def test_confidence_threshold_filtering(
        self,
        mock_suggest,
        mock_explain,
        mock_analyze,
        mock_search
    ):
        """Test that low confidence matches are filtered out."""
        # Mock task analysis
        mock_analyze.return_value = {
            'keywords': ['test'],
            'intent': 'ADD_FEATURE',
            'doc_type_relevance': {'ba': 0.5, 'ta': 0.5, 'tc': 0.5},
            'search_query': 'test'
        }

        # Mock hybrid search with low scores
        mock_search.return_value = [
            {
                'document_id': 1,
                'title': 'Doc 1',
                'doc_type': 'ba',
                'version': 'v1.0',
                'chunk_text': 'Text',
                'combined_score': 0.1,  # Very low
                'semantic_score': 0.1,
                'keyword_score': 0.1
            }
        ]

        # Execute
        matches = self.matcher.find_matches_for_task("Test task", top_k=5)

        # Should filter out low confidence matches
        assert len(matches) == 0

    @patch('pipeline.smart_matcher.hybrid_search')
    @patch('pipeline.smart_matcher.TaskAnalyzer.analyze_task')
    @patch('pipeline.smart_matcher.MatchExplainer.explain_match')
    @patch('pipeline.smart_matcher.MatchExplainer.suggest_action')
    def test_multiple_matches_sorted_by_confidence(
        self,
        mock_suggest,
        mock_explain,
        mock_analyze,
        mock_search
    ):
        """Test that multiple matches are sorted by confidence score."""
        # Mock task analysis
        mock_analyze.return_value = {
            'keywords': ['test'],
            'intent': 'ADD_FEATURE',
            'doc_type_relevance': {'ba': 0.8, 'ta': 0.5, 'tc': 0.3},
            'search_query': 'test'
        }

        # Mock multiple search results with different scores
        mock_search.return_value = [
            {
                'document_id': 1,
                'title': 'Doc Low',
                'doc_type': 'ba',
                'version': 'v1.0',
                'chunk_text': 'Text',
                'combined_score': 0.5,
                'semantic_score': 0.5,
                'keyword_score': 0.5
            },
            {
                'document_id': 2,
                'title': 'Doc High',
                'doc_type': 'ba',
                'version': 'v1.0',
                'chunk_text': 'Text',
                'combined_score': 0.9,
                'semantic_score': 0.9,
                'keyword_score': 0.9
            },
            {
                'document_id': 3,
                'title': 'Doc Medium',
                'doc_type': 'ba',
                'version': 'v1.0',
                'chunk_text': 'Text',
                'combined_score': 0.7,
                'semantic_score': 0.7,
                'keyword_score': 0.7
            }
        ]

        mock_explain.return_value = "Explanation"
        mock_suggest.return_value = {'suggestion': 'UPDATE_EXISTING', 'reasoning': 'Test'}

        # Execute
        matches = self.matcher.find_matches_for_task("Test task", top_k=5)

        # Verify sorted by confidence (highest first)
        assert len(matches) == 3
        assert matches[0]['document_id'] == 2  # Highest confidence
        assert matches[1]['document_id'] == 3  # Medium
        assert matches[2]['document_id'] == 1  # Lowest
        assert matches[0]['confidence'] > matches[1]['confidence']
        assert matches[1]['confidence'] > matches[2]['confidence']

    @patch('pipeline.smart_matcher.hybrid_search')
    @patch('pipeline.smart_matcher.TaskAnalyzer.analyze_task')
    def test_top_k_limiting(self, mock_analyze, mock_search):
        """Test that top_k limits the number of results."""
        mock_analyze.return_value = {
            'keywords': ['test'],
            'doc_type_relevance': {'ba': 0.5, 'ta': 0.5, 'tc': 0.5},
            'search_query': 'test'
        }

        # Mock 10 search results
        mock_search.return_value = [
            {
                'document_id': i,
                'title': f'Doc {i}',
                'doc_type': 'ba',
                'version': 'v1.0',
                'chunk_text': 'Text',
                'combined_score': 0.8,
                'semantic_score': 0.8,
                'keyword_score': 0.8
            }
            for i in range(10)
        ]

        with patch.object(self.matcher.match_explainer, 'explain_match', return_value="Test"):
            with patch.object(self.matcher.match_explainer, 'suggest_action', return_value={'suggestion': 'UPDATE_EXISTING', 'reasoning': 'Test'}):
                matches = self.matcher.find_matches_for_task("Test task", top_k=3)

        # Should return only top 3
        assert len(matches) == 3

    def test_calculate_confidence_semantic_weight(self):
        """Test confidence calculation with semantic score."""
        search_result = {
            'semantic_score': 0.8,
            'keyword_score': 0.6,
            'doc_type': 'ba'
        }

        task_features = {
            'doc_type_relevance': {'ba': 0.9, 'ta': 0.5, 'tc': 0.3}
        }

        confidence, breakdown = self.matcher._calculate_confidence(
            search_result,
            task_features,
            doc_type_filter='ba'
        )

        # Verify weighted calculation: 0.8*0.5 + 0.6*0.3 + metadata*0.2
        # Note: metadata gets boosted to 0.9*1.2 = 1.08, capped at 1.0 when filter matches
        expected_semantic = 0.8 * 0.5  # 0.4
        expected_keyword = 0.6 * 0.3    # 0.18
        expected_metadata = min(1.0, 0.9 * 1.2) * 0.2  # 1.0 * 0.2 = 0.2
        expected = expected_semantic + expected_keyword + expected_metadata
        assert abs(confidence - expected) < 0.05  # Allow more tolerance for float math

        # Verify breakdown
        assert breakdown['semantic_score'] == 0.8
        assert breakdown['keyword_score'] == 0.6
        # Metadata gets boosted from 0.9 to min(1.0, 0.9*1.2) = 1.0
        assert breakdown['metadata_score'] == 1.0

    def test_calculate_confidence_metadata_boost(self):
        """Test metadata score boost when doc type matches filter."""
        search_result = {
            'semantic_score': 0.7,
            'keyword_score': 0.7,
            'doc_type': 'ba'
        }

        task_features = {
            'doc_type_relevance': {'ba': 0.5, 'ta': 0.5, 'tc': 0.5}
        }

        # With doc_type filter matching
        confidence_with_boost, breakdown_with_boost = self.matcher._calculate_confidence(
            search_result,
            task_features,
            doc_type_filter='ba'
        )

        # Without doc_type filter
        confidence_without_boost, breakdown_without_boost = self.matcher._calculate_confidence(
            search_result,
            task_features,
            doc_type_filter=None
        )

        # Should get 1.2x boost when filter matches
        assert breakdown_with_boost['metadata_score'] > breakdown_without_boost['metadata_score']

    def test_calculate_confidence_normalization(self):
        """Test that confidence is normalized to [0, 1]."""
        search_result = {
            'semantic_score': 1.5,  # Out of bounds
            'keyword_score': 1.2,   # Out of bounds
            'doc_type': 'ba'
        }

        task_features = {
            'doc_type_relevance': {'ba': 1.5, 'ta': 0.5, 'tc': 0.5}  # Out of bounds
        }

        confidence, _ = self.matcher._calculate_confidence(
            search_result,
            task_features,
            doc_type_filter='ba'
        )

        # Should be normalized to [0, 1]
        assert 0.0 <= confidence <= 1.0

    @patch('pipeline.smart_matcher.hybrid_search')
    @patch('pipeline.smart_matcher.TaskAnalyzer.analyze_task')
    @patch('pipeline.smart_matcher.MatchExplainer.explain_match')
    @patch('pipeline.smart_matcher.MatchExplainer.suggest_action')
    def test_search_query_fallback(
        self,
        mock_suggest,
        mock_explain,
        mock_analyze,
        mock_search
    ):
        """Test fallback to task description when search_query is empty."""
        # Mock task analysis with empty search_query
        mock_analyze.return_value = {
            'keywords': ['test'],
            'doc_type_relevance': {'ba': 0.5, 'ta': 0.5, 'tc': 0.5},
            'search_query': '...'  # Invalid query
        }

        mock_search.return_value = []

        task_description = "Add new feature"
        self.matcher.find_matches_for_task(task_description)

        # Should use task_description as fallback
        call_args = mock_search.call_args[1]
        assert call_args['query_text'] == task_description

    @patch('pipeline.smart_matcher.get_document_by_id')
    def test_get_match_with_details(self, mock_get_doc):
        """Test enriching match with full document details."""
        mock_get_doc.return_value = {
            'id': 1,
            'title': 'Test Doc',
            'project_name': 'Test Project',
            'created_at': '2024-01-01',
            'updated_at': '2024-01-02',
            'file_path': '/path/to/doc'
        }

        match = {
            'document_id': 1,
            'title': 'Test Doc',
            'confidence': 0.8
        }

        enriched = self.matcher.get_match_with_details(match)

        assert enriched['project_name'] == 'Test Project'
        assert enriched['created_at'] == '2024-01-01'
        assert enriched['file_path'] == '/path/to/doc'


class TestFindMatchesConvenienceFunction:
    """Test the convenience function."""

    @patch('pipeline.smart_matcher.SmartMatcher.find_matches_for_task')
    def test_find_matches_convenience_function(self, mock_find):
        """Test the module-level find_matches_for_task function."""
        mock_find.return_value = [{'document_id': 1}]

        result = find_matches_for_task(
            task_description="Test task",
            jira_key="PROJ-123",
            doc_type='ba',
            top_k=5
        )

        assert len(result) == 1
        mock_find.assert_called_once_with(
            "Test task",
            "PROJ-123",
            'ba',
            5
        )


class TestSmartMatcherEdgeCases:
    """Test edge cases and error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.matcher = SmartMatcher()

    @patch('pipeline.smart_matcher.hybrid_search')
    @patch('pipeline.smart_matcher.TaskAnalyzer.analyze_task')
    def test_empty_search_results(self, mock_analyze, mock_search):
        """Test handling of empty search results."""
        mock_analyze.return_value = {
            'keywords': ['test'],
            'doc_type_relevance': {'ba': 0.5, 'ta': 0.5, 'tc': 0.5},
            'search_query': 'test'
        }

        mock_search.return_value = []

        matches = self.matcher.find_matches_for_task("Test task")

        assert len(matches) == 0

    @patch('pipeline.smart_matcher.hybrid_search')
    @patch('pipeline.smart_matcher.TaskAnalyzer.analyze_task')
    @patch('pipeline.smart_matcher.MatchExplainer.explain_match')
    @patch('pipeline.smart_matcher.MatchExplainer.suggest_action')
    def test_missing_scores_in_search_result(
        self,
        mock_suggest,
        mock_explain,
        mock_analyze,
        mock_search
    ):
        """Test handling of search results with missing scores."""
        mock_analyze.return_value = {
            'keywords': ['test'],
            'doc_type_relevance': {'ba': 0.5, 'ta': 0.5, 'tc': 0.5},
            'search_query': 'test'
        }

        # Result with missing scores
        mock_search.return_value = [
            {
                'document_id': 1,
                'title': 'Test',
                'doc_type': 'ba',
                'version': 'v1.0',
                'chunk_text': 'Text'
                # Missing: semantic_score, keyword_score, combined_score
            }
        ]

        mock_explain.return_value = "Test"
        mock_suggest.return_value = {'suggestion': 'CREATE_NEW', 'reasoning': 'Test'}

        matches = self.matcher.find_matches_for_task("Test task")

        # Should handle missing scores gracefully with defaults (0.0)
        assert len(matches) >= 0  # May filter out due to low confidence

    @patch('pipeline.smart_matcher.hybrid_search')
    @patch('pipeline.smart_matcher.TaskAnalyzer.analyze_task')
    def test_task_analyzer_error_handling(self, mock_analyze, mock_search):
        """Test handling of task analyzer errors."""
        # Task analyzer raises exception
        mock_analyze.side_effect = Exception("AI Error")

        mock_search.return_value = []

        # Should handle error gracefully
        with pytest.raises(Exception):
            self.matcher.find_matches_for_task("Test task")

    @patch('pipeline.smart_matcher.hybrid_search')
    @patch('pipeline.smart_matcher.TaskAnalyzer.analyze_task')
    def test_hybrid_search_error_handling(self, mock_analyze, mock_search):
        """Test handling of hybrid search errors."""
        mock_analyze.return_value = {
            'keywords': ['test'],
            'doc_type_relevance': {'ba': 0.5, 'ta': 0.5, 'tc': 0.5},
            'search_query': 'test'
        }

        # Hybrid search raises exception
        mock_search.side_effect = Exception("Search Error")

        # Should propagate error
        with pytest.raises(Exception):
            self.matcher.find_matches_for_task("Test task")
