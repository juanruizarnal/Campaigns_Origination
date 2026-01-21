"""Gemini client for Google AI with search grounding capabilities.

This module provides a robust client for Google's Gemini API with:
- Text generation using Gemini 1.5 Flash
- Search grounding for real-time web information
- Automatic retries with exponential backoff
- Structured logging for debugging and monitoring

Usage:
    from integrations.gemini import GeminiClient, get_gemini_client
    
    client = get_gemini_client()
    response = await client.generate("Describe renewable energy trends")
    
    # With search grounding
    response = await client.search_and_generate("Latest solar panel prices 2024")
"""

from typing import Optional
import json

import google.generativeai as genai
from google.generativeai.types import GenerationConfig, HarmCategory, HarmBlockThreshold
import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config.settings import get_settings

logger = structlog.get_logger()


class GeminiError(Exception):
    """Base exception for Gemini operations."""
    pass


class GeminiClient:
    """Client for Google Gemini API with search grounding support.
    
    Provides text generation and search-grounded generation using
    Gemini 1.5 Flash model. All operations include automatic retries
    and structured logging.
    
    Attributes:
        model_name: The Gemini model being used
        
    Example:
        client = GeminiClient()
        response = await client.generate(
            prompt="Analyze this company",
            system_prompt="You are a financial analyst"
        )
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        """Initialize Gemini client.
        
        Args:
            api_key: Google API key. If not provided, loads from settings.
            model_name: Model to use. Defaults to settings or gemini-1.5-flash.
        """
        settings = get_settings()
        self._api_key = api_key or settings.GOOGLE_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL
        
        # Configure the API
        genai.configure(api_key=self._api_key)
        
        # Initialize the model
        self._model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=GenerationConfig(
                temperature=0.7,
                top_p=0.95,
                top_k=40,
                max_output_tokens=8192,
            ),
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            },
        )
        
        # Model with search grounding (use google_search for 2.0+ models)
        try:
            from google.generativeai.types import Tool
            # For Gemini 2.0+ use google_search tool
            self._search_model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=GenerationConfig(
                    temperature=0.3,  # Lower for factual search
                    top_p=0.95,
                    max_output_tokens=8192,
                ),
                tools=[Tool(google_search={})],
            )
        except Exception:
            # Fallback: use regular model for search (without grounding)
            self._search_model = self._model
        
        logger.info(
            "gemini_client_initialized",
            model=self.model_name,
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True,
    )
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate text response from prompt.
        
        Args:
            prompt: The user prompt/question
            system_prompt: Optional system instructions
            temperature: Override default temperature (0-1)
            max_tokens: Override default max output tokens
            
        Returns:
            Generated text response
            
        Raises:
            GeminiError: If generation fails after retries
        """
        logger.debug(
            "gemini_generate_start",
            prompt_length=len(prompt),
            has_system_prompt=system_prompt is not None,
        )
        
        try:
            # Build the full prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n---\n\n{prompt}"
            
            # Override generation config if needed
            generation_config = None
            if temperature is not None or max_tokens is not None:
                generation_config = GenerationConfig(
                    temperature=temperature or 0.7,
                    max_output_tokens=max_tokens or 8192,
                )
            
            # Generate response
            response = self._model.generate_content(
                full_prompt,
                generation_config=generation_config,
            )
            
            # Extract text
            if response.text:
                result = response.text
            else:
                # Handle blocked or empty responses
                logger.warning(
                    "gemini_empty_response",
                    prompt_length=len(prompt),
                    finish_reason=str(response.candidates[0].finish_reason) if response.candidates else "unknown",
                )
                result = ""
            
            # Log usage
            logger.info(
                "gemini_generate_complete",
                response_length=len(result),
                model=self.model_name,
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "gemini_generate_error",
                error_type=type(e).__name__,
                error_message=str(e),
            )
            raise GeminiError(f"Gemini generation failed: {e}") from e
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True,
    )
    def search_and_generate(
        self,
        query: str,
        system_prompt: Optional[str] = None,
    ) -> dict:
        """Search the web and generate response using Google Search Grounding.
        
        Uses Gemini's built-in Google Search capability to find current
        information and generate a grounded response.
        
        Args:
            query: Search query or question requiring web search
            system_prompt: Optional system instructions for response format
            
        Returns:
            Dict containing:
                - response: The generated text
                - grounding_metadata: Search sources and citations (if available)
                
        Raises:
            GeminiError: If search or generation fails
        """
        logger.debug(
            "gemini_search_start",
            query_length=len(query),
        )
        
        try:
            # Build prompt with system instructions if provided
            full_query = query
            if system_prompt:
                full_query = f"{system_prompt}\n\n---\n\nQuery: {query}"
            
            # Generate with search grounding
            response = self._search_model.generate_content(full_query)
            
            # Extract response text
            response_text = ""
            if response.text:
                response_text = response.text
            
            # Extract grounding metadata if available
            grounding_metadata = None
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata'):
                    grounding_metadata = candidate.grounding_metadata
            
            result = {
                "response": response_text,
                "grounding_metadata": grounding_metadata,
            }
            
            logger.info(
                "gemini_search_complete",
                response_length=len(response_text),
                has_grounding=grounding_metadata is not None,
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "gemini_search_error",
                error_type=type(e).__name__,
                error_message=str(e),
            )
            raise GeminiError(f"Gemini search failed: {e}") from e
    
    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> dict:
        """Generate a structured JSON response.
        
        Prompts the model to return valid JSON and parses it.
        
        Args:
            prompt: The user prompt (should request JSON output)
            system_prompt: Optional system instructions
            
        Returns:
            Parsed JSON as dict
            
        Raises:
            GeminiError: If generation or parsing fails
        """
        # Add JSON instruction to system prompt
        json_system = "You must respond with valid JSON only. No markdown, no explanations."
        if system_prompt:
            json_system = f"{system_prompt}\n\n{json_system}"
        
        response = self.generate(prompt, system_prompt=json_system, temperature=0.3)
        
        # Clean response (remove markdown code blocks if present)
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(
                "gemini_json_parse_error",
                response_preview=response[:200],
                error=str(e),
            )
            raise GeminiError(f"Failed to parse JSON response: {e}") from e


# Singleton instance
_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Get shared GeminiClient instance.
    
    Returns:
        Singleton GeminiClient instance
    """
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client

