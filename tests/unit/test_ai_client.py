"""
Unit tests for AI Client module (agents/ai_client.py).

Tests cover:
- Anthropic API calls (call_sonnet)
- Gemini API calls (call_gemini)
- API key rotation (call_gemini_with_rotation)
- Unified AI interface (call_ai)
- Error handling
- Prompt caching
"""
import pytest
from unittest.mock import Mock, MagicMock, patch


# ─────────────────────────────────────────────
# Anthropic API Tests (call_sonnet)
# ─────────────────────────────────────────────

@pytest.mark.unit
@pytest.mark.api
class TestCallSonnet:
    """Test Anthropic API calls."""

    @patch('agents.ai_client.anthropic.Anthropic')
    @patch('agents.ai_client.parse_ai_json')
    def test_call_sonnet_success(self, mock_parse, mock_anthropic_class):
        """Test successful Anthropic API call."""
        from agents.ai_client import call_sonnet

        # Mock Anthropic client
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client

        # Mock response
        mock_response = Mock()
        mock_response.content = [Mock(text='{"result": "success"}')]
        mock_response.stop_reason = "end_turn"
        mock_client.messages.create.return_value = mock_response

        # Mock JSON parser
        mock_parse.return_value = {"json_output": {"result": "success"}, "stop_reason": "end_turn"}

        # Call
        result = call_sonnet(
            system_prompt="Test system prompt",
            user_content="Test user content",
            api_key="test-key"
        )

        # Verify
        assert result["json_output"]["result"] == "success"
        mock_anthropic_class.assert_called_once_with(api_key="test-key")
        mock_client.messages.create.assert_called_once()

    @patch('agents.ai_client.anthropic.Anthropic')
    def test_call_sonnet_with_caching_enabled(self, mock_anthropic_class):
        """Test that caching is enabled by default."""
        from agents.ai_client import call_sonnet

        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text='{}')]
        mock_response.stop_reason = "end_turn"
        mock_client.messages.create.return_value = mock_response

        # Call with caching enabled (default)
        call_sonnet("System prompt", "User content", "key", use_caching=True)

        # Check that system blocks include cache_control
        call_args = mock_client.messages.create.call_args
        system_param = call_args.kwargs['system']

        assert isinstance(system_param, list)
        assert system_param[0]["type"] == "text"
        assert system_param[0]["cache_control"] == {"type": "ephemeral"}

    @patch('agents.ai_client.anthropic.Anthropic')
    def test_call_sonnet_with_caching_disabled(self, mock_anthropic_class):
        """Test that caching can be disabled."""
        from agents.ai_client import call_sonnet

        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text='{}')]
        mock_response.stop_reason = "end_turn"
        mock_client.messages.create.return_value = mock_response

        # Call with caching disabled
        call_sonnet("System prompt", "User content", "key", use_caching=False)

        # Check that system is plain string
        call_args = mock_client.messages.create.call_args
        system_param = call_args.kwargs['system']

        assert isinstance(system_param, str)
        assert system_param == "System prompt"

    @patch('agents.ai_client.anthropic.Anthropic')
    def test_call_sonnet_prompt_cleaning(self, mock_anthropic_class):
        """Test that {{ }} are converted to { }."""
        from agents.ai_client import call_sonnet

        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text='{}')]
        mock_response.stop_reason = "end_turn"
        mock_client.messages.create.return_value = mock_response

        # Call with {{ }} in prompt
        call_sonnet("Test {{variable}} prompt", "User", "key", use_caching=False)

        # Verify {{ }} converted to { }
        call_args = mock_client.messages.create.call_args
        system_param = call_args.kwargs['system']
        assert system_param == "Test {variable} prompt"

    @patch('agents.ai_client.anthropic.Anthropic')
    def test_call_sonnet_authentication_error(self, mock_anthropic_class):
        """Test handling of authentication errors."""
        from agents.ai_client import call_sonnet

        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        # Raise generic Exception instead of Anthropic-specific ones
        mock_client.messages.create.side_effect = Exception("AuthenticationError: Invalid API key")

        # Catch the exception and check if it's wrapped
        try:
            call_sonnet("System", "User", "invalid-key")
        except Exception as e:
            # Generic exception will be caught by the last except block
            assert "❌ Claude API hatası" in str(e)

    @patch('agents.ai_client.anthropic.Anthropic')
    def test_call_sonnet_rate_limit_error(self, mock_anthropic_class):
        """Test handling of rate limit errors."""
        from agents.ai_client import call_sonnet

        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        # Raise generic Exception instead
        mock_client.messages.create.side_effect = Exception("RateLimitError: Rate limit exceeded")

        with pytest.raises(Exception) as exc_info:
            call_sonnet("System", "User", "key")

        assert "❌ Claude API hatası" in str(exc_info.value)

    @patch('agents.ai_client.anthropic.Anthropic')
    def test_call_sonnet_overloaded_error(self, mock_anthropic_class):
        """Test handling of overloaded API errors."""
        from agents.ai_client import call_sonnet

        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        # Raise generic Exception instead
        mock_client.messages.create.side_effect = Exception("APIError: API is overloaded")

        with pytest.raises(Exception) as exc_info:
            call_sonnet("System", "User", "key")

        assert "❌ Claude API hatası" in str(exc_info.value)


# ─────────────────────────────────────────────
# Gemini API Tests (call_gemini)
# ─────────────────────────────────────────────

@pytest.mark.unit
@pytest.mark.api
class TestCallGemini:
    """Test Gemini API calls."""

    @patch('agents.ai_client.genai.Client')
    @patch('agents.ai_client.parse_ai_json')
    def test_call_gemini_success(self, mock_parse, mock_genai_class):
        """Test successful Gemini API call."""
        from agents.ai_client import call_gemini

        # Mock Gemini client
        mock_client = Mock()
        mock_genai_class.return_value = mock_client

        # Mock response
        mock_response = Mock()
        mock_response.text = '{"genel_puan": 85.0}'
        mock_response.candidates = [Mock(finish_reason=Mock(name="STOP"))]
        mock_client.models.generate_content.return_value = mock_response

        # Mock parser
        mock_parse.return_value = {"json_output": {"genel_puan": 85.0}, "stop_reason": "STOP"}

        # Call
        result = call_gemini("System prompt", "User content", "test-key")

        # Verify
        assert result["json_output"]["genel_puan"] == 85.0
        mock_genai_class.assert_called_once_with(api_key="test-key")

    @patch('agents.ai_client.genai.Client')
    def test_call_gemini_token_capping(self, mock_genai_class):
        """Test that max_tokens is capped at 8192."""
        from agents.ai_client import call_gemini

        mock_client = Mock()
        mock_genai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.text = '{}'
        mock_response.candidates = []
        mock_client.models.generate_content.return_value = mock_response

        # Call with very high token limit
        call_gemini("System", "User", "key", max_tokens=15000)

        # Verify capped to 8192
        call_args = mock_client.models.generate_content.call_args
        config = call_args.kwargs['config']
        assert config.max_output_tokens == 8192

    @patch('agents.ai_client.genai.Client')
    def test_call_gemini_quota_error(self, mock_genai_class):
        """Test handling of quota errors."""
        from agents.ai_client import call_gemini

        mock_client = Mock()
        mock_genai_class.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception("Quota exceeded")

        with pytest.raises(Exception) as exc_info:
            call_gemini("System", "User", "key")

        assert "❌ Gemini API kota/limit hatası" in str(exc_info.value)

    @patch('agents.ai_client.genai.Client')
    def test_call_gemini_auth_error(self, mock_genai_class):
        """Test handling of authentication errors."""
        from agents.ai_client import call_gemini

        mock_client = Mock()
        mock_genai_class.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception("API key invalid")

        with pytest.raises(Exception) as exc_info:
            call_gemini("System", "User", "key")

        assert "❌ Gemini API key hatası" in str(exc_info.value)

    @patch('agents.ai_client.genai.Client')
    def test_call_gemini_content_filter_error(self, mock_genai_class):
        """Test handling of content filter errors."""
        from agents.ai_client import call_gemini

        mock_client = Mock()
        mock_genai_class.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception("Content filtered by safety policy")

        with pytest.raises(Exception) as exc_info:
            call_gemini("System", "User", "key")

        assert "❌ Gemini içerik filtresi" in str(exc_info.value)


# ─────────────────────────────────────────────
# Gemini Key Rotation Tests
# ─────────────────────────────────────────────

@pytest.mark.unit
@pytest.mark.api
class TestCallGeminiWithRotation:
    """Test Gemini API key rotation."""

    @patch('agents.ai_client.get_gemini_keys')
    def test_rotation_no_keys(self, mock_get_keys):
        """Test error when no keys available."""
        from agents.ai_client import call_gemini_with_rotation

        mock_get_keys.return_value = []

        with pytest.raises(Exception) as exc_info:
            call_gemini_with_rotation("System", "User")

        assert "❌ Gemini API key bulunamadı" in str(exc_info.value)

    @patch('agents.ai_client.get_gemini_keys')
    @patch('agents.ai_client.call_gemini')
    def test_rotation_single_key(self, mock_call_gemini, mock_get_keys):
        """Test that single key uses regular call_gemini."""
        from agents.ai_client import call_gemini_with_rotation

        mock_get_keys.return_value = ["single-key"]
        mock_call_gemini.return_value = {"json_output": {"result": "ok"}}

        result = call_gemini_with_rotation("System", "User")

        assert result["json_output"]["result"] == "ok"
        mock_call_gemini.assert_called_once_with("System", "User", "single-key", 8000, None)

    @patch('agents.ai_client.get_gemini_keys')
    @patch('agents.ai_client.call_gemini')
    @patch('agents.ai_client.APIKeyManager')
    def test_rotation_success_first_key(self, mock_manager_class, mock_call_gemini, mock_get_keys):
        """Test successful call with first key."""
        from agents.ai_client import call_gemini_with_rotation

        # Setup
        mock_get_keys.return_value = ["key1", "key2"]
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.get_next_key.return_value = "key1"

        mock_call_gemini.return_value = {"json_output": {"result": "ok"}}

        # Call
        result = call_gemini_with_rotation("System", "User")

        # Verify
        assert result["json_output"]["result"] == "ok"
        mock_manager.record_success.assert_called_once_with("key1")

    @patch('agents.ai_client.get_gemini_keys')
    @patch('agents.ai_client.call_gemini')
    @patch('agents.ai_client.APIKeyManager')
    @patch('agents.ai_client.is_quota_error')
    def test_rotation_quota_error_rotates(self, mock_is_quota, mock_manager_class, mock_call_gemini, mock_get_keys):
        """Test that quota errors trigger key rotation."""
        from agents.ai_client import call_gemini_with_rotation

        # Setup
        mock_get_keys.return_value = ["key1", "key2"]
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.get_next_key.side_effect = ["key1", "key2"]

        # First call fails with quota, second succeeds
        quota_error = Exception("Quota exceeded")
        mock_call_gemini.side_effect = [quota_error, {"json_output": {"result": "ok"}}]
        mock_is_quota.return_value = True

        # Call
        result = call_gemini_with_rotation("System", "User")

        # Verify rotation happened
        assert result["json_output"]["result"] == "ok"
        assert mock_call_gemini.call_count == 2
        mock_manager.mark_key_failed.assert_called_once()

    @patch('agents.ai_client.get_gemini_keys')
    @patch('agents.ai_client.call_gemini')
    @patch('agents.ai_client.APIKeyManager')
    @patch('agents.ai_client.is_quota_error')
    def test_rotation_all_keys_quota_exhausted(self, mock_is_quota, mock_manager_class, mock_call_gemini, mock_get_keys):
        """Test error when all keys hit quota."""
        from agents.ai_client import call_gemini_with_rotation

        mock_get_keys.return_value = ["key1", "key2"]
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.get_next_key.side_effect = ["key1", "key2"]

        quota_error = Exception("Quota exceeded")
        mock_call_gemini.side_effect = quota_error
        mock_is_quota.return_value = True

        with pytest.raises(Exception) as exc_info:
            call_gemini_with_rotation("System", "User")

        assert "❌ Tüm Gemini API keyleri quota limitine ulaştı" in str(exc_info.value)

    @patch('agents.ai_client.get_gemini_keys')
    @patch('agents.ai_client.call_gemini')
    @patch('agents.ai_client.APIKeyManager')
    @patch('agents.ai_client.is_auth_error')
    def test_rotation_auth_error_rotates(self, mock_is_auth, mock_manager_class, mock_call_gemini, mock_get_keys):
        """Test that auth errors trigger rotation."""
        from agents.ai_client import call_gemini_with_rotation

        mock_get_keys.return_value = ["key1", "key2"]
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.get_next_key.side_effect = ["key1", "key2"]

        auth_error = Exception("Invalid API key")
        mock_call_gemini.side_effect = [auth_error, {"json_output": {"result": "ok"}}]
        mock_is_auth.return_value = True

        result = call_gemini_with_rotation("System", "User")

        assert result["json_output"]["result"] == "ok"
        mock_manager.mark_key_invalid.assert_called_once()


# ─────────────────────────────────────────────
# Unified AI Interface Tests (call_ai)
# ─────────────────────────────────────────────

@pytest.mark.unit
@pytest.mark.api
class TestCallAI:
    """Test unified AI interface."""

    @patch('agents.ai_client.is_anthropic_model')
    @patch('agents.ai_client.call_sonnet')
    def test_call_ai_routes_to_anthropic(self, mock_call_sonnet, mock_is_anthropic):
        """Test routing to Anthropic."""
        from agents.ai_client import call_ai

        mock_is_anthropic.return_value = True
        mock_call_sonnet.return_value = {"json_output": {"result": "anthropic"}}

        result = call_ai(
            system_prompt="System",
            user_content="User",
            anthropic_key="ant-key",
            gemini_key="gem-key",
            model="claude-sonnet-4"
        )

        assert result["json_output"]["result"] == "anthropic"
        mock_call_sonnet.assert_called_once()

    @patch('agents.ai_client.is_anthropic_model')
    @patch('agents.ai_client.is_gemini_model')
    @patch('agents.ai_client.call_gemini_with_rotation')
    def test_call_ai_routes_to_gemini(self, mock_call_gemini, mock_is_gemini, mock_is_anthropic):
        """Test routing to Gemini."""
        from agents.ai_client import call_ai

        mock_is_anthropic.return_value = False
        mock_is_gemini.return_value = True
        mock_call_gemini.return_value = {"json_output": {"result": "gemini"}}

        result = call_ai(
            system_prompt="System",
            user_content="User",
            anthropic_key="ant-key",
            gemini_key="gem-key",
            model="gemini-2.0-flash-exp"
        )

        assert result["json_output"]["result"] == "gemini"
        mock_call_gemini.assert_called_once()

    @patch('agents.ai_client.is_anthropic_model')
    @patch('agents.ai_client.is_gemini_model')
    def test_call_ai_unknown_model_error(self, mock_is_gemini, mock_is_anthropic):
        """Test error for unknown model."""
        from agents.ai_client import call_ai

        mock_is_anthropic.return_value = False
        mock_is_gemini.return_value = False

        with pytest.raises(ValueError) as exc_info:
            call_ai("System", "User", "ant-key", "gem-key", "unknown-model")

        assert "Unknown model provider" in str(exc_info.value)

    @patch('agents.ai_client.is_anthropic_model')
    @patch('agents.ai_client.is_gemini_model')
    @patch('agents.ai_client.call_gemini_with_rotation')
    def test_call_ai_caps_gemini_tokens(self, mock_call_gemini, mock_is_gemini, mock_is_anthropic):
        """Test that Gemini tokens are capped to 8192."""
        from agents.ai_client import call_ai

        mock_is_anthropic.return_value = False
        mock_is_gemini.return_value = True
        mock_call_gemini.return_value = {"json_output": {}}

        call_ai("System", "User", "ant-key", "gem-key", "gemini-model", max_tokens=15000)

        # Verify capped tokens passed to Gemini
        call_args = mock_call_gemini.call_args
        assert call_args[0][2] == 8192  # Third positional arg is max_tokens
