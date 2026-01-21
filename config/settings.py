"""Application settings using Pydantic Settings.

This module provides centralized configuration management for the Alter-5
Origination Engine, loading settings from environment variables and .env files.
"""

from functools import lru_cache
import os
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _load_streamlit_secrets() -> None:
    """Load Streamlit Cloud secrets into environment variables when available."""
    try:
        import tomllib
    except Exception:
        return

    secrets_path = Path(__file__).resolve().parent.parent / ".streamlit" / "secrets.toml"
    if not secrets_path.exists():
        return

    try:
        with secrets_path.open("rb") as handle:
            secrets = tomllib.load(handle)
    except Exception:
        return

    def inject(payload: dict) -> None:
        for key, value in payload.items():
            if isinstance(value, dict):
                inject(value)
                continue
            if isinstance(value, (str, int, float, bool)) and key not in os.environ:
                os.environ[key] = str(value)

    inject(secrets)


_load_streamlit_secrets()


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
        default="gemini-2.0-flash",
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
    
    MAILCHIMP_WEBHOOK_SECRET: str = Field(
        default="",
        description="Secret for validating Mailchimp webhooks",
    )
    
    # ==========================================================================
    # LinkedIn / Proxycurl Configuration (Fase 2)
    # ==========================================================================
    
    PROXYCURL_API_KEY: str = Field(
        default="",
        description="Proxycurl API key for LinkedIn data",
    )
    
    # ==========================================================================
    # OpenAI / Embeddings Configuration (Fase 3)
    # ==========================================================================
    
    OPENAI_API_KEY: str = Field(
        default="",
        description="OpenAI API key for embeddings",
    )
    
    PINECONE_API_KEY: str = Field(
        default="",
        description="Pinecone API key for vector database",
    )
    
    PINECONE_ENVIRONMENT: str = Field(
        default="us-east-1",
        description="Pinecone environment",
    )
    
    PINECONE_INDEX_NAME: str = Field(
        default="alter5-companies",
        description="Pinecone index name",
    )
    
    # ==========================================================================
    # Slack Configuration (Fase 4)
    # ==========================================================================
    
    SLACK_BOT_TOKEN: str = Field(
        default="",
        description="Slack bot token for alerts",
    )
    
    SLACK_CHANNEL_ORIGINATION: str = Field(
        default="#origination",
        description="Slack channel for origination alerts",
    )
    
    SLACK_CHANNEL_TECH: str = Field(
        default="#tech-alerts",
        description="Slack channel for tech alerts",
    )
    
    # ==========================================================================
    # Database Configuration (Fase 3-4)
    # ==========================================================================
    
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis URL for Celery and cache",
    )
    
    MONGODB_URL: str = Field(
        default="mongodb://localhost:27017/alter5",
        description="MongoDB URL for sync and cache",
    )
    
    # ==========================================================================
    # Scraping Configuration
    # ==========================================================================
    
    SCRAPING_TIMEOUT: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Timeout for web scraping in seconds",
    )
    
    USER_AGENT: str = Field(
        default="Mozilla/5.0 (compatible; Alter5Bot/1.0; +https://alter-5.com)",
        description="User agent for HTTP requests",
    )
    
    # ==========================================================================
    # Trigger Detector Configuration (Fase 4)
    # ==========================================================================
    
    TRIGGER_SCAN_INTERVAL: int = Field(
        default=15,
        ge=5,
        le=60,
        description="Interval for RSS scanning in minutes",
    )
    
    TRIGGER_RELEVANCE_THRESHOLD: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum relevance to create trigger",
    )
    
    # ==========================================================================
    # Follow-up Configuration (Fase 4)
    # ==========================================================================
    
    FOLLOWUP_1_DAYS: int = Field(
        default=3,
        ge=1,
        le=14,
        description="Days until first follow-up",
    )
    
    FOLLOWUP_2_DAYS: int = Field(
        default=5,
        ge=1,
        le=14,
        description="Days until second follow-up after first",
    )
    
    MAX_FOLLOWUPS: int = Field(
        default=2,
        ge=1,
        le=5,
        description="Maximum follow-ups per target",
    )
    
    # ==========================================================================
    # Campaign Configuration
    # ==========================================================================
    
    MAX_TARGETS_MASS_CAMPAIGN: int = Field(
        default=200,
        ge=50,
        le=1000,
        description="Maximum targets for mass campaigns",
    )
    
    APPROVAL_MODE: Literal["always_approve", "notify_only", "auto"] = Field(
        default="notify_only",
        description="Mode for campaign approval",
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


def get_scraping_config() -> dict:
    """Get scraping configuration.
    
    Returns:
        Dict with scraping settings.
    """
    settings = get_settings()
    return {
        "timeout": settings.SCRAPING_TIMEOUT,
        "user_agent": settings.USER_AGENT,
    }


def get_linkedin_config() -> dict:
    """Get LinkedIn/Proxycurl configuration.
    
    Returns:
        Dict with Proxycurl API key.
    """
    settings = get_settings()
    return {
        "api_key": settings.PROXYCURL_API_KEY,
    }


def get_redis_url() -> str:
    """Get Redis URL for Celery and caching."""
    return get_settings().REDIS_URL


def get_mongodb_url() -> str:
    """Get MongoDB URL for sync."""
    return get_settings().MONGODB_URL


def get_slack_config() -> dict:
    """Get Slack configuration for alerts."""
    settings = get_settings()
    return {
        "bot_token": settings.SLACK_BOT_TOKEN,
        "channel_origination": settings.SLACK_CHANNEL_ORIGINATION,
        "channel_tech": settings.SLACK_CHANNEL_TECH,
    }


def get_followup_config() -> dict:
    """Get follow-up configuration."""
    settings = get_settings()
    return {
        "followup_1_days": settings.FOLLOWUP_1_DAYS,
        "followup_2_days": settings.FOLLOWUP_2_DAYS,
        "max_followups": settings.MAX_FOLLOWUPS,
    }

