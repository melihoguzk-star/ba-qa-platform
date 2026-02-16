"""
Unit tests for Match Explainer module.

Tests explanation generation and action suggestion logic for
document matches.
"""

import pytest
from unittest.mock import Mock, patch
from pipeline.match_explainer import (
    MatchExplainer,
    explain_match,
    suggest_action
)


class TestMatchExplainer:
    """Test suite for MatchExplainer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.explainer = MatchExplainer()

    def test_initialization(self):
        """Test MatchExplainer initialization."""
        assert self.explainer is not None
        assert hasattr(self.explainer, 'model')
        assert self.explainer.model == "claude-sonnet-4-20250514"

    def test_explain_match_uses_template(self):
        """Test that explain_match uses template explanation."""
        matched_doc = {
            'title': 'Login BA',
            'doc_type': 'ba',
            'confidence': 0.75
        }

        scores = {
            'semantic_score': 0.8,
            'keyword_score': 0.7,
            'metadata_score': 0.6
        }

        explanation = self.explainer.explain_match(
            task_description="Add Face ID to login",
            matched_doc=matched_doc,
            scores=scores
        )

        # Should return Turkish template explanation
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert 'Login BA' in explanation or 'BA' in explanation

    def test_generate_template_explanation_high_confidence(self):
        """Test template explanation for high confidence match."""
        matched_doc = {
            'title': 'Payment Module',
            'doc_type': 'ba',
            'confidence': 0.85
        }

        scores = {
            'semantic_score': 0.9,
            'keyword_score': 0.8,
            'metadata_score': 0.7
        }

        explanation = self.explainer._generate_template_explanation(
            matched_doc,
            scores
        )

        # Should mention high match score
        assert 'Yüksek eşleşme' in explanation or 'yüksek' in explanation.lower()

    def test_generate_template_explanation_medium_confidence(self):
        """Test template explanation for medium confidence match."""
        matched_doc = {
            'title': 'Dashboard',
            'doc_type': 'ba',
            'confidence': 0.65
        }

        scores = {
            'semantic_score': 0.7,
            'keyword_score': 0.6,
            'metadata_score': 0.6
        }

        explanation = self.explainer._generate_template_explanation(
            matched_doc,
            scores
        )

        # Should mention medium/orta level match
        assert 'Orta' in explanation or 'orta' in explanation

    def test_generate_template_explanation_low_confidence(self):
        """Test template explanation for low confidence match."""
        matched_doc = {
            'title': 'Test Cases',
            'doc_type': 'tc',
            'confidence': 0.35
        }

        scores = {
            'semantic_score': 0.4,
            'keyword_score': 0.3,
            'metadata_score': 0.3
        }

        explanation = self.explainer._generate_template_explanation(
            matched_doc,
            scores
        )

        # Should mention low score or evaluation needed
        assert 'Düşük' in explanation or 'düşük' in explanation or 'değerlendirme' in explanation

    def test_generate_template_explanation_semantic_dominant(self):
        """Test template explanation when semantic score is dominant."""
        matched_doc = {
            'title': 'Login Flow',
            'doc_type': 'ba',
            'confidence': 0.70
        }

        scores = {
            'semantic_score': 0.9,  # High semantic
            'keyword_score': 0.3,   # Low keyword
            'metadata_score': 0.5
        }

        explanation = self.explainer._generate_template_explanation(
            matched_doc,
            scores
        )

        # Should mention semantic similarity
        assert 'anlamsal' in explanation.lower()

    def test_generate_template_explanation_keyword_dominant(self):
        """Test template explanation when keyword score is dominant."""
        matched_doc = {
            'title': 'Payment',
            'doc_type': 'ba',
            'confidence': 0.70
        }

        scores = {
            'semantic_score': 0.3,  # Low semantic
            'keyword_score': 0.9,   # High keyword
            'metadata_score': 0.5
        }

        explanation = self.explainer._generate_template_explanation(
            matched_doc,
            scores
        )

        # Should mention keyword matching
        assert 'anahtar kelime' in explanation.lower()

    def test_suggest_action_high_confidence(self):
        """Test action suggestion for high confidence match."""
        task_features = {
            'intent': 'ADD_FEATURE',
            'keywords': ['login', 'authentication']
        }

        matched_doc = {
            'title': 'Login BA',
            'doc_type': 'ba'
        }

        result = self.explainer.suggest_action(
            task_features=task_features,
            matched_doc=matched_doc,
            confidence=0.80
        )

        # High confidence should suggest UPDATE_EXISTING
        assert result['suggestion'] == 'UPDATE_EXISTING'
        assert 'reasoning' in result
        assert isinstance(result['reasoning'], str)

    def test_suggest_action_low_confidence(self):
        """Test action suggestion for low confidence match."""
        task_features = {
            'intent': 'ADD_FEATURE',
            'keywords': ['quantum', 'blockchain']
        }

        matched_doc = {
            'title': 'Login BA',
            'doc_type': 'ba'
        }

        result = self.explainer.suggest_action(
            task_features=task_features,
            matched_doc=matched_doc,
            confidence=0.25
        )

        # Low confidence should suggest CREATE_NEW
        assert result['suggestion'] == 'CREATE_NEW'
        assert 'reasoning' in result

    def test_suggest_action_medium_confidence_high_side(self):
        """Test action suggestion for medium-high confidence."""
        task_features = {
            'intent': 'UPDATE_FEATURE',
            'keywords': ['payment']
        }

        matched_doc = {
            'title': 'Payment Module',
            'doc_type': 'ba'
        }

        result = self.explainer.suggest_action(
            task_features=task_features,
            matched_doc=matched_doc,
            confidence=0.65
        )

        # Medium-high should suggest UPDATE_EXISTING
        assert result['suggestion'] == 'UPDATE_EXISTING'

    def test_suggest_action_medium_confidence_low_side(self):
        """Test action suggestion for medium-low confidence."""
        task_features = {
            'intent': 'ADD_FEATURE',
            'keywords': ['new']
        }

        matched_doc = {
            'title': 'Old Doc',
            'doc_type': 'ba'
        }

        result = self.explainer.suggest_action(
            task_features=task_features,
            matched_doc=matched_doc,
            confidence=0.45
        )

        # Medium-low should suggest CREATE_NEW
        assert result['suggestion'] == 'CREATE_NEW'

    def test_suggest_action_includes_confidence(self):
        """Test that suggestion includes confidence score."""
        task_features = {'intent': 'ADD_FEATURE', 'keywords': []}
        matched_doc = {'title': 'Test', 'doc_type': 'ba'}

        result = self.explainer.suggest_action(
            task_features=task_features,
            matched_doc=matched_doc,
            confidence=0.77
        )

        assert 'confidence' in result
        assert result['confidence'] == 0.77

    def test_suggest_action_update_sections_field(self):
        """Test that suggestion includes update_sections field."""
        task_features = {'intent': 'ADD_FEATURE', 'keywords': []}
        matched_doc = {'title': 'Test', 'doc_type': 'ba'}

        result = self.explainer.suggest_action(
            task_features=task_features,
            matched_doc=matched_doc,
            confidence=0.80
        )

        assert 'update_sections' in result
        assert isinstance(result['update_sections'], list)

    def test_ai_explanation_disabled(self):
        """Test that AI explanation is disabled (uses template)."""
        matched_doc = {
            'title': 'Test Doc',
            'doc_type': 'ba',
            'confidence': 0.50
        }

        scores = {
            'semantic_score': 0.5,
            'keyword_score': 0.5,
            'metadata_score': 0.5
        }

        # Call explain_match (should NOT use AI)
        explanation = self.explainer.explain_match(
            task_description="Test task",
            matched_doc=matched_doc,
            scores=scores,
            use_ai=True  # Even if requested, should use template
        )

        # Should return template explanation (not AI)
        assert isinstance(explanation, str)
        assert len(explanation) > 0


class TestExplainMatchConvenienceFunction:
    """Test the convenience function."""

    @patch('pipeline.match_explainer.MatchExplainer.explain_match')
    def test_explain_match_convenience_function(self, mock_explain):
        """Test the module-level explain_match function."""
        mock_explain.return_value = "Test explanation"

        matched_doc = {'title': 'Test', 'doc_type': 'ba', 'confidence': 0.7}
        scores = {'semantic_score': 0.7, 'keyword_score': 0.6, 'metadata_score': 0.5}

        result = explain_match(
            task_description="Test task",
            matched_doc=matched_doc,
            scores=scores,
            use_ai=False
        )

        assert result == "Test explanation"
        mock_explain.assert_called_once()


class TestSuggestActionConvenienceFunction:
    """Test the convenience function."""

    @patch('pipeline.match_explainer.MatchExplainer.suggest_action')
    def test_suggest_action_convenience_function(self, mock_suggest):
        """Test the module-level suggest_action function."""
        mock_suggest.return_value = {
            'suggestion': 'UPDATE_EXISTING',
            'reasoning': 'Test',
            'update_sections': [],
            'confidence': 0.8
        }

        task_features = {'intent': 'ADD_FEATURE', 'keywords': []}
        matched_doc = {'title': 'Test', 'doc_type': 'ba'}

        result = suggest_action(
            task_features=task_features,
            matched_doc=matched_doc,
            confidence=0.8
        )

        assert result['suggestion'] == 'UPDATE_EXISTING'
        mock_suggest.assert_called_once()


class TestMatchExplainerEdgeCases:
    """Test edge cases and error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.explainer = MatchExplainer()

    def test_explain_match_missing_fields(self):
        """Test explanation with missing document fields."""
        matched_doc = {}  # Empty doc
        scores = {
            'semantic_score': 0.5,
            'keyword_score': 0.5,
            'metadata_score': 0.5
        }

        explanation = self.explainer.explain_match(
            task_description="Test",
            matched_doc=matched_doc,
            scores=scores
        )

        # Should handle missing fields gracefully
        assert isinstance(explanation, str)
        assert len(explanation) > 0

    def test_explain_match_missing_scores(self):
        """Test explanation with missing scores."""
        matched_doc = {
            'title': 'Test',
            'doc_type': 'ba',
            'confidence': 0.7
        }

        scores = {}  # Empty scores

        explanation = self.explainer.explain_match(
            task_description="Test",
            matched_doc=matched_doc,
            scores=scores
        )

        # Should handle missing scores gracefully
        assert isinstance(explanation, str)

    def test_suggest_action_empty_task_features(self):
        """Test suggestion with empty task features."""
        task_features = {}  # Empty features
        matched_doc = {'title': 'Test', 'doc_type': 'ba'}

        result = self.explainer.suggest_action(
            task_features=task_features,
            matched_doc=matched_doc,
            confidence=0.6
        )

        # Should still return valid suggestion
        assert 'suggestion' in result
        assert result['suggestion'] in ['UPDATE_EXISTING', 'CREATE_NEW', 'EXTEND_DOCUMENT']

    def test_suggest_action_edge_confidence_values(self):
        """Test suggestion with edge confidence values."""
        task_features = {'intent': 'ADD_FEATURE', 'keywords': []}
        matched_doc = {'title': 'Test', 'doc_type': 'ba'}

        # Test boundary values
        # Logic: >0.75 → UPDATE, <0.4 → CREATE, else: >0.5 → UPDATE, <=0.5 → CREATE
        test_cases = [
            (0.0, 'CREATE_NEW'),   # Very low
            (0.39, 'CREATE_NEW'),   # Just below 0.4 threshold
            (0.4, 'CREATE_NEW'),   # At 0.4, not > 0.5
            (0.5, 'CREATE_NEW'),   # Mid point (NOT > 0.5)
            (0.51, 'UPDATE_EXISTING'), # Just above 0.5
            (0.75, 'UPDATE_EXISTING'), # At 0.75, still > 0.5
            (0.76, 'UPDATE_EXISTING'), # Just above 0.75
            (1.0, 'UPDATE_EXISTING'),  # Perfect match
        ]

        for confidence, expected_suggestion in test_cases:
            result = self.explainer.suggest_action(
                task_features=task_features,
                matched_doc=matched_doc,
                confidence=confidence
            )

            assert result['suggestion'] == expected_suggestion, \
                f"Confidence {confidence} should suggest {expected_suggestion}"

    def test_template_explanation_with_unicode(self):
        """Test template explanation with Turkish characters."""
        matched_doc = {
            'title': 'Kullanıcı Profili',
            'doc_type': 'ba',
            'confidence': 0.70
        }

        scores = {
            'semantic_score': 0.7,
            'keyword_score': 0.7,
            'metadata_score': 0.7
        }

        explanation = self.explainer._generate_template_explanation(
            matched_doc,
            scores
        )

        # Should handle Turkish characters properly
        assert isinstance(explanation, str)
        assert 'Kullanıcı Profili' in explanation or 'BA' in explanation

    def test_reasoning_is_in_turkish(self):
        """Test that reasoning is in Turkish."""
        task_features = {'intent': 'ADD_FEATURE', 'keywords': []}
        matched_doc = {'title': 'Test', 'doc_type': 'ba'}

        result = self.explainer.suggest_action(
            task_features=task_features,
            matched_doc=matched_doc,
            confidence=0.80
        )

        # Check for Turkish characters/words
        reasoning = result['reasoning']
        turkish_indicators = ['doküman', 'Doküman', 'ü', 'ı', 'ş', 'ğ', 'ç', 'Yeni', 'yeni']

        has_turkish = any(indicator in reasoning for indicator in turkish_indicators)
        assert has_turkish, "Reasoning should be in Turkish"

    def test_explanation_length_reasonable(self):
        """Test that explanations are not too long or too short."""
        matched_doc = {
            'title': 'Test Document',
            'doc_type': 'ba',
            'confidence': 0.70
        }

        scores = {
            'semantic_score': 0.7,
            'keyword_score': 0.7,
            'metadata_score': 0.7
        }

        explanation = self.explainer.explain_match(
            task_description="Test task",
            matched_doc=matched_doc,
            scores=scores
        )

        # Should be reasonable length (not empty, not too long)
        assert 10 < len(explanation) < 500
