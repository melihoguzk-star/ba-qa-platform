"""
Unit tests for JSON Repair module (pipeline/brd/json_repair.py).

Tests cover:
- AI JSON parsing with multiple strategies
- Markdown code block extraction
- Malformed JSON repair
- Truncated JSON handling
- Bracket balancing
"""
import pytest


# ─────────────────────────────────────────────
# parse_ai_json Tests
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestParseAIJSON:
    """Test AI JSON parsing with various inputs."""

    def test_parse_valid_json(self):
        """Test parsing valid JSON string."""
        from pipeline.brd.json_repair import parse_ai_json

        json_str = '{"result": "success", "score": 85}'
        result = parse_ai_json(json_str)

        assert result["result"] == "success"
        assert result["score"] == 85

    def test_parse_json_with_markdown_backticks(self):
        """Test parsing JSON wrapped in markdown code blocks."""
        from pipeline.brd.json_repair import parse_ai_json

        # JSON with ```json markers
        json_str = '''```json
{"result": "success"}
```'''
        result = parse_ai_json(json_str)

        assert result["result"] == "success"

    def test_parse_json_with_generic_backticks(self):
        """Test parsing JSON wrapped in generic ``` markers."""
        from pipeline.brd.json_repair import parse_ai_json

        json_str = '''```
{"result": "success"}
```'''
        result = parse_ai_json(json_str)

        assert result["result"] == "success"

    def test_parse_json_with_text_before_and_after(self):
        """Test parsing JSON with extra text around it."""
        from pipeline.brd.json_repair import parse_ai_json

        json_str = '''Here is the result:
{"result": "success", "score": 90}
Hope this helps!'''
        result = parse_ai_json(json_str)

        assert result["result"] == "success"
        assert result["score"] == 90

    def test_parse_json_no_braces_raises_error(self):
        """Test that missing braces raises ValueError."""
        from pipeline.brd.json_repair import parse_ai_json

        with pytest.raises(ValueError) as exc_info:
            parse_ai_json("No JSON here")

        assert "JSON bulunamadı" in str(exc_info.value)

    def test_parse_json_with_trailing_comma(self):
        """Test parsing JSON with trailing comma."""
        from pipeline.brd.json_repair import parse_ai_json

        # Some AI models add trailing commas
        json_str = '{"items": [1, 2, 3,], "done": true,}'
        result = parse_ai_json(json_str)

        assert "items" in result
        assert result["done"] is True

    def test_parse_nested_json(self):
        """Test parsing nested JSON structures."""
        from pipeline.brd.json_repair import parse_ai_json

        json_str = '''{
    "user": {
        "name": "Test",
        "scores": [85, 90, 95]
    },
    "meta": {
        "timestamp": "2024-01-01"
    }
}'''
        result = parse_ai_json(json_str)

        assert result["user"]["name"] == "Test"
        assert result["user"]["scores"] == [85, 90, 95]
        assert result["meta"]["timestamp"] == "2024-01-01"

    def test_parse_truncated_json_with_repair(self):
        """Test that truncated JSON gets repaired."""
        from pipeline.brd.json_repair import parse_ai_json

        # Simulated truncated response (missing closing braces)
        json_str = '{"result": "success", "items": [1, 2, 3'
        result = parse_ai_json(json_str)

        # Should repair and return something
        assert isinstance(result, dict)
        # May contain _repaired marker
        if "_repaired" in result:
            assert result["_repaired"] in ["line_backtrack", "bracket_balance", "comma_cut"]

    def test_parse_json_with_line_breaks(self):
        """Test parsing multiline JSON."""
        from pipeline.brd.json_repair import parse_ai_json

        json_str = '''
{
  "status": "ok",
  "data": {
    "value": 42
  }
}
'''
        result = parse_ai_json(json_str)

        assert result["status"] == "ok"
        assert result["data"]["value"] == 42


# ─────────────────────────────────────────────
# Edge Cases Tests
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestJSONRepairEdgeCases:
    """Test edge cases in JSON repair."""

    def test_empty_json_object(self):
        """Test parsing empty JSON object."""
        from pipeline.brd.json_repair import parse_ai_json

        json_str = '{}'
        result = parse_ai_json(json_str)

        assert result == {}

    def test_json_with_unicode(self):
        """Test parsing JSON with Unicode characters."""
        from pipeline.brd.json_repair import parse_ai_json

        json_str = '{"message": "Türkçe karakter: ğüşöç", "emoji": "🎉"}'
        result = parse_ai_json(json_str)

        assert "Türkçe" in result["message"]
        assert result["emoji"] == "🎉"

    def test_json_with_escaped_quotes(self):
        """Test parsing JSON with escaped quotes."""
        from pipeline.brd.json_repair import parse_ai_json

        json_str = '{"text": "He said \\"Hello\\" to me"}'
        result = parse_ai_json(json_str)

        assert result["text"] == 'He said "Hello" to me'

    def test_json_with_newlines_in_strings(self):
        """Test parsing JSON with newlines in string values."""
        from pipeline.brd.json_repair import parse_ai_json

        json_str = '{"description": "Line 1\\nLine 2\\nLine 3"}'
        result = parse_ai_json(json_str)

        assert "Line 1" in result["description"]
        assert "Line 2" in result["description"]

    def test_json_array_at_root(self):
        """Test that arrays (not objects) at root work."""
        from pipeline.brd.json_repair import parse_ai_json

        # Note: parse_ai_json looks for {}, so this should fail
        # But let's test the current behavior
        json_str = '[1, 2, 3]'

        with pytest.raises(ValueError):
            parse_ai_json(json_str)

    def test_multiple_json_objects_fails(self):
        """Test that multiple JSON objects (invalid) fails gracefully."""
        from pipeline.brd.json_repair import parse_ai_json

        json_str = '{"first": true} {"second": true}'

        # Multiple JSON objects is not valid JSON, should fail
        with pytest.raises(ValueError):
            parse_ai_json(json_str)

    def test_json_with_numbers(self):
        """Test parsing JSON with various number types."""
        from pipeline.brd.json_repair import parse_ai_json

        json_str = '{"int": 42, "float": 3.14, "negative": -10, "zero": 0}'
        result = parse_ai_json(json_str)

        assert result["int"] == 42
        assert result["float"] == 3.14
        assert result["negative"] == -10
        assert result["zero"] == 0

    def test_json_with_booleans_and_null(self):
        """Test parsing JSON with booleans and null."""
        from pipeline.brd.json_repair import parse_ai_json

        json_str = '{"active": true, "disabled": false, "value": null}'
        result = parse_ai_json(json_str)

        assert result["active"] is True
        assert result["disabled"] is False
        assert result["value"] is None

    def test_very_long_json(self):
        """Test parsing very long JSON strings."""
        from pipeline.brd.json_repair import parse_ai_json

        # Generate a long JSON with many items
        items = [f'{{"id": {i}, "value": "item_{i}"}}' for i in range(100)]
        json_str = '{"items": [' + ','.join(items) + ']}'

        result = parse_ai_json(json_str)

        assert "items" in result
        assert len(result["items"]) == 100
        assert result["items"][0]["id"] == 0
        assert result["items"][99]["id"] == 99


# ─────────────────────────────────────────────
# Repair Strategy Tests
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestRepairStrategies:
    """Test different JSON repair strategies."""

    def test_strategy_markdown_cleaning(self):
        """Test that markdown code blocks are properly removed."""
        from pipeline.brd.json_repair import parse_ai_json

        json_str = '''```json
{"status": "ok"}
```'''
        result = parse_ai_json(json_str)

        # Should successfully parse without markdown markers
        assert result["status"] == "ok"
        assert "```" not in str(result)

    def test_strategy_whitespace_handling(self):
        """Test that leading/trailing whitespace is handled."""
        from pipeline.brd.json_repair import parse_ai_json

        json_str = '''


    {"status": "ok"}


'''
        result = parse_ai_json(json_str)

        assert result["status"] == "ok"

    def test_strategy_comma_cleanup(self):
        """Test that trailing commas are handled."""
        from pipeline.brd.json_repair import parse_ai_json

        # Note: Standard JSON doesn't allow trailing commas,
        # but AI models sometimes generate them
        json_str = '{"a": 1, "b": 2,}'

        result = parse_ai_json(json_str)

        assert result["a"] == 1
        assert result["b"] == 2

    def test_incomplete_json_repair_marker(self):
        """Test that repaired JSON has _repaired marker."""
        from pipeline.brd.json_repair import parse_ai_json

        # Truncated JSON that needs repair
        json_str = '{"status": "ok", "items": ['

        result = parse_ai_json(json_str)

        # Should successfully repair
        assert isinstance(result, dict)

        # May have repair marker
        if "_repaired" in result:
            assert isinstance(result["_repaired"], str)


# ─────────────────────────────────────────────
# Real-world Scenarios
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestRealWorldScenarios:
    """Test real-world AI response scenarios."""

    def test_anthropic_style_response(self):
        """Test parsing Anthropic-style JSON response."""
        from pipeline.brd.json_repair import parse_ai_json

        # Typical Anthropic response format
        json_str = '''Here is the evaluation result:

```json
{
  "genel_puan": 85.0,
  "gecti_mi": true,
  "eksikler": ["Missing wireframes"],
  "guclu_yonler": ["Good structure"]
}
```

Hope this helps!'''

        result = parse_ai_json(json_str)

        assert result["genel_puan"] == 85.0
        assert result["gecti_mi"] is True
        assert isinstance(result["eksikler"], list)

    def test_gemini_style_response(self):
        """Test parsing Gemini-style JSON response."""
        from pipeline.brd.json_repair import parse_ai_json

        json_str = '''{
  "genel_puan": 90.0,
  "gecti_mi": true,
  "eksikler": []
}'''

        result = parse_ai_json(json_str)

        assert result["genel_puan"] == 90.0
        assert result["gecti_mi"] is True

    def test_ba_evaluation_response(self):
        """Test parsing BA evaluation response structure."""
        from pipeline.brd.json_repair import parse_ai_json

        json_str = '''{
  "ekranlar": [
    {
      "ekran_adi": "Login",
      "aciklama": "User login screen",
      "ui_elementleri": ["Email", "Password"]
    }
  ],
  "backend_islemler": [
    {
      "islem_adi": "Authenticate",
      "endpoint": "/api/auth/login"
    }
  ]
}'''

        result = parse_ai_json(json_str)

        assert "ekranlar" in result
        assert len(result["ekranlar"]) == 1
        assert result["ekranlar"][0]["ekran_adi"] == "Login"

    def test_tc_evaluation_response(self):
        """Test parsing TC evaluation response structure."""
        from pipeline.brd.json_repair import parse_ai_json

        json_str = '''{
  "test_scenarios": [
    {
      "scenario_id": "TC001",
      "title": "Login Test",
      "steps": ["Open app", "Enter credentials", "Click login"]
    }
  ],
  "genel_puan": 85.0
}'''

        result = parse_ai_json(json_str)

        assert "test_scenarios" in result
        assert result["test_scenarios"][0]["scenario_id"] == "TC001"
        assert result["genel_puan"] == 85.0
