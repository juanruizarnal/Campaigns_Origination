"""External integrations module for Alter-5 Origination Engine.

Contains clients for:
- Gemini (Google AI) - Search and grounding
- Claude (Anthropic) - Reasoning and writing
- Mailchimp - Email campaigns (Sprint 4)
"""

from integrations.gemini import GeminiClient, GeminiError, get_gemini_client
from integrations.claude import ClaudeClient, ClaudeError, get_claude_client

__all__ = [
    # Gemini
    "GeminiClient",
    "GeminiError",
    "get_gemini_client",
    # Claude
    "ClaudeClient",
    "ClaudeError",
    "get_claude_client",
]
