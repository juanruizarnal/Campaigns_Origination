"""Tests for LLM integration clients (Gemini and Claude)."""

import os
from unittest.mock import MagicMock, patch

import pytest


# Mock environment for all tests
@pytest.fixture(autouse=True)
def mock_env():
    """Set up mock environment variables for all tests."""
    env_vars = {
        "ANTHROPIC_API_KEY": "sk-ant-test-key-12345",
        "GOOGLE_API_KEY": "AIzaTestKey12345",
        "AIRTABLE_PAT": "patTestToken12345",
        "AIRTABLE_BASE_ID": "appTestBase12345",
    }
    with patch.dict(os.environ, env_vars, clear=False):
        yield


@pytest.fixture
def reset_gemini_singleton():
    """Reset Gemini client singleton."""
    import integrations.gemini as module
    original = module._client
    module._client = None
    yield
    module._client = original


@pytest.fixture
def reset_claude_singleton():
    """Reset Claude client singleton."""
    import integrations.claude as module
    original = module._client
    module._client = None
    yield
    module._client = original


class TestGeminiClient:
    """Tests for GeminiClient."""
    
    def test_gemini_client_init(self, reset_gemini_singleton) -> None:
        """Test GeminiClient initializes correctly."""
        with patch("integrations.gemini.genai.configure") as mock_configure:
            with patch("integrations.gemini.genai.GenerativeModel") as mock_model:
                mock_model.return_value = MagicMock()
                
                from integrations.gemini import GeminiClient
                client = GeminiClient()
                
                # Verify configure was called with API key
                mock_configure.assert_called_once()
                assert client.model_name is not None
    
    def test_gemini_generate(self, reset_gemini_singleton) -> None:
        """Test GeminiClient.generate() method."""
        with patch("integrations.gemini.genai.configure"):
            with patch("integrations.gemini.genai.GenerativeModel") as mock_model_class:
                mock_model = MagicMock()
                mock_response = MagicMock()
                mock_response.text = "Test response from Gemini"
                mock_model.generate_content.return_value = mock_response
                mock_model_class.return_value = mock_model
                
                from integrations.gemini import GeminiClient
                client = GeminiClient()
                
                result = client.generate("Test prompt")
                
                assert result == "Test response from Gemini"
                mock_model.generate_content.assert_called_once()
    
    def test_gemini_generate_with_system_prompt(self, reset_gemini_singleton) -> None:
        """Test generate with system prompt."""
        with patch("integrations.gemini.genai.configure"):
            with patch("integrations.gemini.genai.GenerativeModel") as mock_model_class:
                mock_model = MagicMock()
                mock_response = MagicMock()
                mock_response.text = "Response"
                mock_model.generate_content.return_value = mock_response
                mock_model_class.return_value = mock_model
                
                from integrations.gemini import GeminiClient
                client = GeminiClient()
                
                result = client.generate(
                    prompt="User prompt",
                    system_prompt="You are a helpful assistant"
                )
                
                assert result == "Response"
                # Check that the full prompt includes system prompt
                call_args = mock_model.generate_content.call_args
                full_prompt = call_args[0][0]
                assert "You are a helpful assistant" in full_prompt
                assert "User prompt" in full_prompt
    
    def test_gemini_generate_json(self, reset_gemini_singleton) -> None:
        """Test generate_json returns parsed dict."""
        with patch("integrations.gemini.genai.configure"):
            with patch("integrations.gemini.genai.GenerativeModel") as mock_model_class:
                mock_model = MagicMock()
                mock_response = MagicMock()
                mock_response.text = '{"name": "Test", "value": 42}'
                mock_model.generate_content.return_value = mock_response
                mock_model_class.return_value = mock_model
                
                from integrations.gemini import GeminiClient
                client = GeminiClient()
                
                result = client.generate_json("Return JSON")
                
                assert result == {"name": "Test", "value": 42}
    
    def test_gemini_generate_json_with_markdown(self, reset_gemini_singleton) -> None:
        """Test generate_json handles markdown code blocks."""
        with patch("integrations.gemini.genai.configure"):
            with patch("integrations.gemini.genai.GenerativeModel") as mock_model_class:
                mock_model = MagicMock()
                mock_response = MagicMock()
                mock_response.text = '```json\n{"key": "value"}\n```'
                mock_model.generate_content.return_value = mock_response
                mock_model_class.return_value = mock_model
                
                from integrations.gemini import GeminiClient
                client = GeminiClient()
                
                result = client.generate_json("Return JSON")
                
                assert result == {"key": "value"}
    
    def test_gemini_singleton(self, reset_gemini_singleton) -> None:
        """Test get_gemini_client returns singleton."""
        with patch("integrations.gemini.genai.configure"):
            with patch("integrations.gemini.genai.GenerativeModel") as mock_model:
                mock_model.return_value = MagicMock()
                
                from integrations.gemini import get_gemini_client
                
                client1 = get_gemini_client()
                client2 = get_gemini_client()
                
                assert client1 is client2


class TestClaudeClient:
    """Tests for ClaudeClient."""
    
    def test_claude_client_init(self, reset_claude_singleton) -> None:
        """Test ClaudeClient initializes correctly."""
        with patch("integrations.claude.Anthropic") as mock_anthropic:
            mock_anthropic.return_value = MagicMock()
            
            from integrations.claude import ClaudeClient
            client = ClaudeClient()
            
            mock_anthropic.assert_called_once()
            assert client.model is not None
    
    def test_claude_generate(self, reset_claude_singleton) -> None:
        """Test ClaudeClient.generate() method."""
        with patch("integrations.claude.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_block = MagicMock()
            mock_block.text = "Test response from Claude"
            mock_response.content = [mock_block]
            mock_response.usage = MagicMock(input_tokens=10, output_tokens=20)
            mock_response.stop_reason = "end_turn"
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client
            
            from integrations.claude import ClaudeClient
            client = ClaudeClient()
            
            result = client.generate("Test prompt")
            
            assert result == "Test response from Claude"
            mock_client.messages.create.assert_called_once()
    
    def test_claude_generate_with_system_prompt(self, reset_claude_singleton) -> None:
        """Test generate with system prompt."""
        with patch("integrations.claude.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_block = MagicMock()
            mock_block.text = "Response"
            mock_response.content = [mock_block]
            mock_response.usage = MagicMock(input_tokens=10, output_tokens=20)
            mock_response.stop_reason = "end_turn"
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client
            
            from integrations.claude import ClaudeClient
            client = ClaudeClient()
            
            result = client.generate(
                prompt="User prompt",
                system_prompt="You are a helpful assistant"
            )
            
            assert result == "Response"
            # Check system prompt was passed
            call_kwargs = mock_client.messages.create.call_args.kwargs
            assert call_kwargs["system"] == "You are a helpful assistant"
    
    def test_claude_generate_structured(self, reset_claude_singleton) -> None:
        """Test generate_structured returns parsed dict."""
        with patch("integrations.claude.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_block = MagicMock()
            mock_block.text = '{"name": "Test", "value": 42}'
            mock_response.content = [mock_block]
            mock_response.usage = MagicMock(input_tokens=10, output_tokens=20)
            mock_response.stop_reason = "end_turn"
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client
            
            from integrations.claude import ClaudeClient
            client = ClaudeClient()
            
            result = client.generate_structured("Extract data")
            
            assert result == {"name": "Test", "value": 42}
    
    def test_claude_generate_structured_with_format(self, reset_claude_singleton) -> None:
        """Test generate_structured with response_format."""
        with patch("integrations.claude.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_block = MagicMock()
            mock_block.text = '{"company": "Test Corp", "revenue": 1000000}'
            mock_response.content = [mock_block]
            mock_response.usage = MagicMock(input_tokens=10, output_tokens=20)
            mock_response.stop_reason = "end_turn"
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client
            
            from integrations.claude import ClaudeClient
            client = ClaudeClient()
            
            result = client.generate_structured(
                prompt="Extract company info",
                response_format={"company": "str", "revenue": "int"}
            )
            
            assert result["company"] == "Test Corp"
            assert result["revenue"] == 1000000
    
    def test_claude_singleton(self, reset_claude_singleton) -> None:
        """Test get_claude_client returns singleton."""
        with patch("integrations.claude.Anthropic") as mock_anthropic:
            mock_anthropic.return_value = MagicMock()
            
            from integrations.claude import get_claude_client
            
            client1 = get_claude_client()
            client2 = get_claude_client()
            
            assert client1 is client2


class TestIntegrationsModule:
    """Test the integrations module imports."""
    
    def test_imports(self, reset_gemini_singleton, reset_claude_singleton) -> None:
        """Test that all expected classes are importable."""
        with patch("integrations.gemini.genai.configure"):
            with patch("integrations.gemini.genai.GenerativeModel"):
                with patch("integrations.claude.Anthropic"):
                    from integrations import (
                        GeminiClient,
                        GeminiError,
                        get_gemini_client,
                        ClaudeClient,
                        ClaudeError,
                        get_claude_client,
                    )
                    
                    assert GeminiClient is not None
                    assert GeminiError is not None
                    assert get_gemini_client is not None
                    assert ClaudeClient is not None
                    assert ClaudeError is not None
                    assert get_claude_client is not None

