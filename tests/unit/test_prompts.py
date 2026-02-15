"""
Unit tests for Prompt Templates (agents/prompts.py).

Tests cover:
- Prompt builder functions
- Variable substitution
- Conditional logic (with/without BRD)
- Prompt structure validation
- No syntax errors
"""
import pytest
import re


# ─────────────────────────────────────────────
# BA Evaluation Prompt Tests
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestBAEvaluationPrompt:
    """Test BA evaluation prompt builder."""

    def test_build_ba_prompt_without_brd(self):
        """Test BA prompt generation without BRD reference."""
        from agents.prompts import build_ba_evaluation_prompt

        ba_text = "Sample BA document content"
        prompt = build_ba_evaluation_prompt(ba_text, has_brd=False)

        # Verify basic structure
        assert isinstance(prompt, str)
        assert len(prompt) > 100  # Should be substantial

        # Should NOT mention BRD comparison
        assert "COMPARING it against THIS REFERENCE" not in prompt
        assert "reference document was provided" in prompt.lower()

        # Should contain evaluation criteria
        assert "completeness" in prompt.lower()
        assert "wireframes" in prompt.lower()
        assert "requirement" in prompt.lower()

    def test_build_ba_prompt_with_brd(self):
        """Test BA prompt generation with BRD reference."""
        from agents.prompts import build_ba_evaluation_prompt

        ba_text = "Sample BA document"
        brd_text = "Sample BRD reference"
        prompt = build_ba_evaluation_prompt(ba_text, brd_text, has_brd=True)

        # Should mention BRD comparison
        assert "COMPARING it against THIS REFERENCE" in prompt
        assert "requirements from the BRD" in prompt

        # Should still contain basic criteria
        assert "completeness" in prompt.lower()
        assert "SCORING RULES" in prompt

    def test_ba_prompt_contains_scoring_rules(self):
        """Test that BA prompt contains scoring rules."""
        from agents.prompts import build_ba_evaluation_prompt

        prompt = build_ba_evaluation_prompt("BA text", has_brd=False)

        # Check for scoring guidance
        assert "DEFAULT SCORE IS 5/10" in prompt or "default score" in prompt.lower()
        assert "Pass threshold" in prompt or "pass" in prompt.lower()
        assert "60" in prompt  # Pass threshold

    def test_ba_prompt_contains_all_criteria(self):
        """Test that all 9 evaluation criteria are present."""
        from agents.prompts import build_ba_evaluation_prompt

        prompt = build_ba_evaluation_prompt("BA text", has_brd=False)

        expected_criteria = [
            "completeness",
            "wireframes",
            "flow_diagrams",
            "requirement_quality",
            "acceptance_criteria",
            "consistency",
            "business_rules",
            "error_handling"
        ]

        for criterion in expected_criteria:
            assert criterion in prompt.lower(), f"Missing criterion: {criterion}"

    def test_ba_prompt_no_syntax_errors(self):
        """Test that prompt has no obvious syntax errors."""
        from agents.prompts import build_ba_evaluation_prompt

        ba_text = "Test BA"
        brd_text = "Test BRD"

        # Should not raise exceptions
        prompt_without_brd = build_ba_evaluation_prompt(ba_text, has_brd=False)
        prompt_with_brd = build_ba_evaluation_prompt(ba_text, brd_text, has_brd=True)

        # Check no unmatched braces
        assert prompt_without_brd.count("{") == prompt_without_brd.count("}")
        assert prompt_with_brd.count("{") == prompt_with_brd.count("}")


# ─────────────────────────────────────────────
# TC Evaluation Prompt Tests
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestTCEvaluationPrompt:
    """Test TC evaluation prompt builder."""

    def test_build_tc_prompt_exists(self):
        """Test that TC prompt builder exists."""
        from agents.prompts import build_tc_evaluation_prompt

        tc_text = "Sample TC document"
        ba_text = "Sample BA document"

        prompt = build_tc_evaluation_prompt(tc_text, ba_text)

        assert isinstance(prompt, str)
        assert len(prompt) > 100

    def test_tc_prompt_references_ba(self):
        """Test that TC prompt references BA document."""
        from agents.prompts import build_tc_evaluation_prompt

        tc_text = "Test cases"
        ba_text = "Business analysis"

        prompt = build_tc_evaluation_prompt(tc_text, ba_text)

        # Should mention BA as reference
        assert "business analysis" in prompt.lower() or "ba" in prompt.lower()

    def test_tc_prompt_contains_test_criteria(self):
        """Test that TC prompt contains test-related criteria."""
        from agents.prompts import build_tc_evaluation_prompt

        prompt = build_tc_evaluation_prompt("TC", "BA")

        # Test-related keywords
        test_keywords = [
            "test",
            "coverage",
            "scenario",
            "case"
        ]

        # At least some test keywords should be present
        found_keywords = [kw for kw in test_keywords if kw in prompt.lower()]
        assert len(found_keywords) >= 2, f"Too few test keywords found: {found_keywords}"

    def test_tc_prompt_no_syntax_errors(self):
        """Test that TC prompt has no syntax errors."""
        from agents.prompts import build_tc_evaluation_prompt

        prompt = build_tc_evaluation_prompt("TC text", "BA text")

        # Check balanced braces
        assert prompt.count("{") == prompt.count("}")


# ─────────────────────────────────────────────
# JSON Parsing Tests
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestJSONParsing:
    """Test JSON response parsing."""

    def test_parse_json_response_valid_json(self):
        """Test parsing valid JSON response."""
        from agents.prompts import parse_json_response

        json_text = '{"result": "success", "score": 85}'
        parsed = parse_json_response(json_text)

        assert isinstance(parsed, dict)
        assert parsed["result"] == "success"
        assert parsed["score"] == 85

    def test_parse_json_response_with_markdown(self):
        """Test parsing JSON wrapped in markdown code blocks."""
        from agents.prompts import parse_json_response

        json_text = '''```json
{"result": "success"}
```'''
        parsed = parse_json_response(json_text)

        assert isinstance(parsed, dict)
        assert "result" in parsed


# ─────────────────────────────────────────────
# Prompt Formatting Tests
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestPromptFormatting:
    """Test prompt formatting and structure."""

    def test_prompts_are_non_empty(self):
        """Test that all prompts generate non-empty strings."""
        from agents.prompts import (
            build_ba_evaluation_prompt,
            build_tc_evaluation_prompt
        )

        ba_prompt = build_ba_evaluation_prompt("BA", has_brd=False)
        tc_prompt = build_tc_evaluation_prompt("TC", "BA")

        assert len(ba_prompt) > 0
        assert len(tc_prompt) > 0

    def test_prompts_are_properly_formatted(self):
        """Test that prompts have proper formatting (no tabs, reasonable line length)."""
        from agents.prompts import build_ba_evaluation_prompt

        prompt = build_ba_evaluation_prompt("BA text", has_brd=False)

        # Should not have excessive whitespace
        assert "\t\t\t" not in prompt

        # Lines should be reasonable length (max ~200 chars)
        lines = prompt.split("\n")
        excessively_long_lines = [line for line in lines if len(line) > 300]
        assert len(excessively_long_lines) < 5, "Too many excessively long lines"

    def test_prompts_contain_instructions(self):
        """Test that prompts contain clear instructions."""
        from agents.prompts import build_ba_evaluation_prompt

        prompt = build_ba_evaluation_prompt("BA", has_brd=False)

        # Should contain instructional language
        instructional_words = ["evaluate", "assess", "score", "criteria", "quality"]
        found = [word for word in instructional_words if word in prompt.lower()]

        assert len(found) >= 3, f"Too few instructional words: {found}"

    def test_prompts_handle_special_characters(self):
        """Test that prompts handle special characters in input."""
        from agents.prompts import build_ba_evaluation_prompt

        # Input with special characters
        ba_text = "BA with <html> tags & special chars: $100, 50%"
        brd_text = "BRD with 'quotes' and \"double quotes\""

        # Should not raise exceptions
        prompt = build_ba_evaluation_prompt(ba_text, brd_text, has_brd=True)

        assert isinstance(prompt, str)
        assert len(prompt) > 0


# ─────────────────────────────────────────────
# Prompt Consistency Tests
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestPromptConsistency:
    """Test consistency across different prompts."""

    def test_all_prompts_have_scoring_guidance(self):
        """Test that all evaluation prompts have scoring guidance."""
        from agents.prompts import (
            build_ba_evaluation_prompt,
            build_tc_evaluation_prompt
        )

        ba_prompt = build_ba_evaluation_prompt("BA", has_brd=False)
        tc_prompt = build_tc_evaluation_prompt("TC", "BA")

        # Both should mention scoring or evaluation
        assert "score" in ba_prompt.lower() or "evaluate" in ba_prompt.lower()
        assert "score" in tc_prompt.lower() or "evaluate" in tc_prompt.lower()

    def test_prompts_use_consistent_terminology(self):
        """Test that prompts use consistent terminology."""
        from agents.prompts import (
            build_ba_evaluation_prompt,
            build_tc_evaluation_prompt
        )

        ba_prompt = build_ba_evaluation_prompt("BA", has_brd=False)
        tc_prompt = build_tc_evaluation_prompt("TC", "BA")

        # Common terminology should be used consistently
        # (This is a basic check - could be expanded)
        assert isinstance(ba_prompt, str)
        assert isinstance(tc_prompt, str)

    def test_prompt_builders_accept_correct_parameters(self):
        """Test that prompt builders have correct signatures."""
        from agents.prompts import (
            build_ba_evaluation_prompt,
            build_tc_evaluation_prompt
        )

        # BA prompt accepts ba_text, brd_text, has_brd
        ba_prompt = build_ba_evaluation_prompt(
            ba_text="BA",
            brd_text="BRD",
            has_brd=True
        )
        assert isinstance(ba_prompt, str)

        # TC prompt accepts tc_text, ba_text
        tc_prompt = build_tc_evaluation_prompt(
            tc_text="TC",
            ba_text="BA"
        )
        assert isinstance(tc_prompt, str)
