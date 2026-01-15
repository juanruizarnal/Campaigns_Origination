"""Claude client for Anthropic API with structured output support.

This module provides a robust client for Anthropic's Claude API with:
- Text generation using Claude Sonnet 4
- Structured JSON output for data extraction
- Automatic retries with exponential backoff
- Structured logging for debugging and monitoring

Usage:
    from integrations.claude import ClaudeClient, get_claude_client
    
    client = get_claude_client()
    response = await client.generate(
        prompt="Analyze this company's financials",
        system_prompt="You are a financial analyst"
    )
    
    # For structured output
    response = client.generate_structured(
        prompt="Extract key information",
        response_format={"name": "str", "revenue": "float"}
    )
"""

from typing import Any, Optional
import json

from anthropic import Anthropic, APIError, RateLimitError
import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config.settings import get_settings

logger = structlog.get_logger()


class ClaudeError(Exception):
    """Base exception for Claude operations."""
    pass


class ClaudeClient:
    """Client for Anthropic Claude API.
    
    Provides text generation and structured output extraction using
    Claude Sonnet 4 (or configurable model). All operations include 
    automatic retries and structured logging.
    
    Attributes:
        model: The Claude model being used
        
    Example:
        client = ClaudeClient()
        response = client.generate(
            prompt="Evaluate this company for FEI eligibility",
            system_prompt="You are an FEI eligibility expert"
        )
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """Initialize Claude client.
        
        Args:
            api_key: Anthropic API key. If not provided, loads from settings.
            model: Model to use. Defaults to settings or claude-sonnet-4-20250514.
        """
        settings = get_settings()
        self._api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = model or settings.CLAUDE_MODEL
        
        # Initialize Anthropic client
        self._client = Anthropic(api_key=self._api_key)
        
        logger.info(
            "claude_client_initialized",
            model=self.model,
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((ConnectionError, TimeoutError, RateLimitError)),
        reraise=True,
    )
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """Generate text response from prompt.
        
        Args:
            prompt: The user prompt/question
            system_prompt: Optional system instructions
            model: Override default model
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum output tokens
            
        Returns:
            Generated text response
            
        Raises:
            ClaudeError: If generation fails after retries
        """
        logger.debug(
            "claude_generate_start",
            prompt_length=len(prompt),
            has_system_prompt=system_prompt is not None,
            model=model or self.model,
        )
        
        try:
            # Build messages
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            # Create message
            response = self._client.messages.create(
                model=model or self.model,
                max_tokens=max_tokens,
                system=system_prompt or "",
                messages=messages,
                temperature=temperature,
            )
            
            # Extract text from response
            result = ""
            if response.content:
                for block in response.content:
                    if hasattr(block, 'text'):
                        result += block.text
            
            # Log usage
            logger.info(
                "claude_generate_complete",
                response_length=len(result),
                model=model or self.model,
                input_tokens=response.usage.input_tokens if response.usage else None,
                output_tokens=response.usage.output_tokens if response.usage else None,
                stop_reason=response.stop_reason,
            )
            
            return result
            
        except RateLimitError as e:
            logger.warning(
                "claude_rate_limit",
                error=str(e),
            )
            raise  # Let tenacity handle retry
            
        except APIError as e:
            logger.error(
                "claude_api_error",
                error_type=type(e).__name__,
                error_message=str(e),
                status_code=getattr(e, 'status_code', None),
            )
            raise ClaudeError(f"Claude API error: {e}") from e
            
        except Exception as e:
            logger.error(
                "claude_generate_error",
                error_type=type(e).__name__,
                error_message=str(e),
            )
            raise ClaudeError(f"Claude generation failed: {e}") from e
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((ConnectionError, TimeoutError, RateLimitError)),
        reraise=True,
    )
    def generate_structured(
        self,
        prompt: str,
        response_format: Optional[dict] = None,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
    ) -> dict:
        """Generate a structured JSON response.
        
        Prompts Claude to return valid JSON and parses it.
        Optionally provide a response_format dict to guide the structure.
        
        Args:
            prompt: The user prompt (should describe what to extract)
            response_format: Optional dict showing expected structure
            system_prompt: Optional additional system instructions
            model: Override default model
            
        Returns:
            Parsed JSON as dict
            
        Raises:
            ClaudeError: If generation or parsing fails
        """
        logger.debug(
            "claude_structured_start",
            prompt_length=len(prompt),
            has_format=response_format is not None,
        )
        
        # Build system prompt for JSON output
        json_system = (
            "You are a data extraction assistant. "
            "You must respond with valid JSON only. "
            "No markdown code blocks, no explanations, just pure JSON."
        )
        
        if response_format:
            format_str = json.dumps(response_format, indent=2)
            json_system += f"\n\nExpected response structure:\n{format_str}"
        
        if system_prompt:
            json_system = f"{system_prompt}\n\n{json_system}"
        
        try:
            # Generate with low temperature for consistency
            response = self.generate(
                prompt=prompt,
                system_prompt=json_system,
                model=model,
                temperature=0.3,
            )
            
            # Clean response (remove markdown if present)
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            # Parse JSON
            result = json.loads(cleaned)
            
            logger.info(
                "claude_structured_complete",
                keys=list(result.keys()) if isinstance(result, dict) else "list",
            )
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(
                "claude_json_parse_error",
                response_preview=response[:200] if response else "",
                error=str(e),
            )
            raise ClaudeError(f"Failed to parse JSON response: {e}") from e
    
    def generate_with_examples(
        self,
        prompt: str,
        examples: list[tuple[str, str]],
        system_prompt: Optional[str] = None,
    ) -> str:
        """Generate with few-shot examples.
        
        Args:
            prompt: The user prompt
            examples: List of (input, output) example tuples
            system_prompt: Optional system instructions
            
        Returns:
            Generated response
        """
        # Build examples into conversation format
        messages_text = ""
        for i, (ex_input, ex_output) in enumerate(examples):
            messages_text += f"\nExample {i+1}:\nInput: {ex_input}\nOutput: {ex_output}\n"
        
        full_prompt = f"{messages_text}\nNow process this:\nInput: {prompt}\nOutput:"
        
        return self.generate(
            prompt=full_prompt,
            system_prompt=system_prompt,
            temperature=0.5,
        )
    
    def analyze_text(
        self,
        text: str,
        analysis_type: str = "summary",
        language: str = "es",
    ) -> str:
        """Analyze text for common tasks.
        
        Args:
            text: Text to analyze
            analysis_type: Type of analysis (summary, sentiment, key_points)
            language: Output language (es, en)
            
        Returns:
            Analysis result
        """
        prompts = {
            "summary": f"Proporciona un resumen conciso del siguiente texto en {language}:",
            "sentiment": f"Analiza el sentimiento del siguiente texto. Responde con: positivo, negativo, o neutro, y explica brevemente.",
            "key_points": f"Extrae los puntos clave del siguiente texto en formato de lista:",
        }
        
        system = prompts.get(analysis_type, prompts["summary"])
        
        return self.generate(
            prompt=text,
            system_prompt=system,
            temperature=0.3,
        )


# Singleton instance
_client: Optional[ClaudeClient] = None


def get_claude_client() -> ClaudeClient:
    """Get shared ClaudeClient instance.
    
    Returns:
        Singleton ClaudeClient instance
    """
    global _client
    if _client is None:
        _client = ClaudeClient()
    return _client

