"""Application settings using Pydantic Settings.

This module provides centralized configuration management for the Alter-5
Origination Engine, loading settings from environment variables and .env files.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    
    All settings can be overridden via environment variables or a .env file.
    Required settings (no default) must be provided.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    # ==========================================================================
    # API Keys (Required)
    # ==========================================================================
    
    ANTHROPIC_API_KEY: str = Field(
        ...,
        description="Anthropic API key for Claude",
    )
    
    GOOGLE_API_KEY: str = Field(
        ...,
        description="Google API key for Gemini",
    )
    
    AIRTABLE_PAT: str = Field(
        ...,
        description="Airtable Personal Access Token",
    )
    
    # ==========================================================================
    # Airtable Configuration
    # ==========================================================================
    
    AIRTABLE_BASE_ID: str = Field(
        default="appEgNSP0tOLJ9YJ9",
        description="Airtable Base ID for Origination Campaigns",
    )
    
    # ==========================================================================
    # Application Defaults
    # ==========================================================================
    
    DEFAULT_LANGUAGE: Literal["es", "en", "pt"] = Field(
        default="es",
        description="Default language for messages and content",
    )
    
    COOLING_OFF_DAYS: int = Field(
        default=90,
        ge=0,
        le=365,
        description="Days before a company can be contacted again",
    )
    
    MAX_TARGETS_PER_CAMPAIGN: int = Field(
        default=30,
        ge=1,
        le=100,
        description="Maximum number of targets per campaign",
    )
    
    MAX_EMAIL_WORDS: int = Field(
        default=150,
        ge=50,
        le=500,
        description="Maximum words in email body",
    )
    
    MIN_FIT_SCORE: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Minimum fit score to include a target (0-1)",
    )
    
    # ==========================================================================
    # LLM Configuration
    # ==========================================================================
    
    CLAUDE_MODEL: str = Field(
        default="claude-sonnet-4-20250514",
        description="Claude model to use for reasoning and writing",
    )
    
    GEMINI_MODEL: str = Field(
        default="gemini-1.5-flash",
        description="Gemini model to use for search and grounding",
    )
    
    LLM_MAX_RETRIES: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum retries for LLM API calls",
    )
    
    LLM_TIMEOUT_SECONDS: int = Field(
        default=60,
        ge=10,
        le=300,
        description="Timeout for LLM API calls in seconds",
    )
    
    # ==========================================================================
    # Mailchimp Configuration
    # ==========================================================================
    
    MAILCHIMP_API_KEY: str = Field(
        default="",
        description="Mailchimp API key (format: xxx-dc)",
    )
    
    MAILCHIMP_LIST_ID: str = Field(
        default="",
        description="Default Mailchimp audience/list ID",
    )
    
    # ==========================================================================
    # Logging Configuration
    # ==========================================================================
    
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Logging level",
    )
    
    LOG_FORMAT: Literal["console", "json"] = Field(
        default="console",
        description="Log output format",
    )
    
    # ==========================================================================
    # Property accessors for snake_case naming
    # ==========================================================================
    
    @property
    def mailchimp_api_key(self) -> str:
        """Get Mailchimp API key."""
        return self.MAILCHIMP_API_KEY
    
    @property
    def mailchimp_list_id(self) -> str:
        """Get Mailchimp default list ID."""
        return self.MAILCHIMP_LIST_ID
    
    # ==========================================================================
    # Validators
    # ==========================================================================
    
    @field_validator("ANTHROPIC_API_KEY")
    @classmethod
    def validate_anthropic_key(cls, v: str) -> str:
        """Validate Anthropic API key format."""
        if not v.startswith("sk-ant-"):
            raise ValueError("ANTHROPIC_API_KEY must start with 'sk-ant-'")
        return v
    
    @field_validator("GOOGLE_API_KEY")
    @classmethod
    def validate_google_key(cls, v: str) -> str:
        """Validate Google API key format."""
        if not v.startswith("AIza"):
            raise ValueError("GOOGLE_API_KEY must start with 'AIza'")
        return v
    
    @field_validator("AIRTABLE_PAT")
    @classmethod
    def validate_airtable_pat(cls, v: str) -> str:
        """Validate Airtable PAT format."""
        if not v.startswith("pat"):
            raise ValueError("AIRTABLE_PAT must start with 'pat'")
        return v
    
    @field_validator("AIRTABLE_BASE_ID")
    @classmethod
    def validate_airtable_base_id(cls, v: str) -> str:
        """Validate Airtable Base ID format."""
        if not v.startswith("app"):
            raise ValueError("AIRTABLE_BASE_ID must start with 'app'")
        return v


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings.
    
    Uses lru_cache to ensure settings are only loaded once.
    
    Returns:
        Settings: Application settings instance.
        
    Raises:
        ValidationError: If required settings are missing or invalid.
    """
    return Settings()


# Convenience function for quick access
def get_airtable_config() -> tuple[str, str]:
    """Get Airtable configuration.
    
    Returns:
        Tuple of (PAT, Base ID)
    """
    settings = get_settings()
    return settings.AIRTABLE_PAT, settings.AIRTABLE_BASE_ID


def get_llm_config() -> dict[str, str]:
    """Get LLM configuration.
    
    Returns:
        Dict with API keys and model names.
    """
    settings = get_settings()
    return {
        "anthropic_api_key": settings.ANTHROPIC_API_KEY,
        "google_api_key": settings.GOOGLE_API_KEY,
        "claude_model": settings.CLAUDE_MODEL,
        "gemini_model": settings.GEMINI_MODEL,
    }

