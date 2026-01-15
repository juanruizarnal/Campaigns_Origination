"""Tests for application settings."""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError


class TestSettings:
    """Test suite for Settings configuration."""
    
    def test_settings_loads_from_env(self) -> None:
        """Test that settings load correctly from environment variables."""
        # Clear cache to force reload
        from config.settings import get_settings
        get_settings.cache_clear()
        
        env_vars = {
            "ANTHROPIC_API_KEY": "sk-ant-test-key-12345",
            "GOOGLE_API_KEY": "AIzaTestKey12345",
            "AIRTABLE_PAT": "patTestToken12345",
            "AIRTABLE_BASE_ID": "appTestBase12345",
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            from config.settings import Settings
            settings = Settings()
            
            assert settings.ANTHROPIC_API_KEY == "sk-ant-test-key-12345"
            assert settings.GOOGLE_API_KEY == "AIzaTestKey12345"
            assert settings.AIRTABLE_PAT == "patTestToken12345"
            assert settings.AIRTABLE_BASE_ID == "appTestBase12345"
    
    def test_default_values(self) -> None:
        """Test that default values are applied correctly when not overridden."""
        # Set only required API keys, verify defaults for optional fields
        env_vars = {
            "ANTHROPIC_API_KEY": "sk-ant-test-key-12345",
            "GOOGLE_API_KEY": "AIzaTestKey12345",
            "AIRTABLE_PAT": "patTestToken12345",
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            from config.settings import Settings
            settings = Settings()
            
            # Check defaults that should not be affected by session fixture
            assert settings.DEFAULT_LANGUAGE == "es"
            assert settings.COOLING_OFF_DAYS == 90
            assert settings.MAX_TARGETS_PER_CAMPAIGN == 30
            assert settings.MAX_EMAIL_WORDS == 150
            assert settings.MIN_FIT_SCORE == 0.6
            # AIRTABLE_BASE_ID starts with 'app' (could be test or production value)
            assert settings.AIRTABLE_BASE_ID.startswith("app")
            # LOG_LEVEL and LOG_FORMAT may be set by conftest
            assert settings.LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR"]
            assert settings.LOG_FORMAT in ["console", "json"]
    
    def test_error_if_required_missing(self) -> None:
        """Test that ValidationError is raised if required settings are missing."""
        # Clear environment of required keys
        env_vars = {
            "ANTHROPIC_API_KEY": "",
            "GOOGLE_API_KEY": "",
            "AIRTABLE_PAT": "",
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            from config.settings import Settings
            with pytest.raises(ValidationError):
                Settings()
    
    def test_anthropic_key_validation(self) -> None:
        """Test Anthropic API key validation."""
        env_vars = {
            "ANTHROPIC_API_KEY": "invalid-key",
            "GOOGLE_API_KEY": "AIzaTestKey12345",
            "AIRTABLE_PAT": "patTestToken12345",
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            from config.settings import Settings
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            assert "ANTHROPIC_API_KEY must start with 'sk-ant-'" in str(exc_info.value)
    
    def test_google_key_validation(self) -> None:
        """Test Google API key validation."""
        env_vars = {
            "ANTHROPIC_API_KEY": "sk-ant-test-key-12345",
            "GOOGLE_API_KEY": "invalid-key",
            "AIRTABLE_PAT": "patTestToken12345",
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            from config.settings import Settings
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            assert "GOOGLE_API_KEY must start with 'AIza'" in str(exc_info.value)
    
    def test_airtable_pat_validation(self) -> None:
        """Test Airtable PAT validation."""
        env_vars = {
            "ANTHROPIC_API_KEY": "sk-ant-test-key-12345",
            "GOOGLE_API_KEY": "AIzaTestKey12345",
            "AIRTABLE_PAT": "invalid-pat",
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            from config.settings import Settings
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            assert "AIRTABLE_PAT must start with 'pat'" in str(exc_info.value)
    
    def test_cooling_off_days_validation(self) -> None:
        """Test cooling off days validation bounds."""
        env_vars = {
            "ANTHROPIC_API_KEY": "sk-ant-test-key-12345",
            "GOOGLE_API_KEY": "AIzaTestKey12345",
            "AIRTABLE_PAT": "patTestToken12345",
            "COOLING_OFF_DAYS": "400",  # Above max 365
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            from config.settings import Settings
            with pytest.raises(ValidationError):
                Settings()
    
    def test_min_fit_score_validation(self) -> None:
        """Test fit score validation bounds."""
        env_vars = {
            "ANTHROPIC_API_KEY": "sk-ant-test-key-12345",
            "GOOGLE_API_KEY": "AIzaTestKey12345",
            "AIRTABLE_PAT": "patTestToken12345",
            "MIN_FIT_SCORE": "1.5",  # Above max 1.0
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            from config.settings import Settings
            with pytest.raises(ValidationError):
                Settings()
    
    def test_get_settings_caching(self) -> None:
        """Test that get_settings returns cached instance."""
        from config.settings import get_settings
        get_settings.cache_clear()
        
        env_vars = {
            "ANTHROPIC_API_KEY": "sk-ant-test-key-12345",
            "GOOGLE_API_KEY": "AIzaTestKey12345",
            "AIRTABLE_PAT": "patTestToken12345",
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            settings1 = get_settings()
            settings2 = get_settings()
            assert settings1 is settings2
    
    def test_get_airtable_config(self) -> None:
        """Test get_airtable_config helper."""
        from config.settings import get_settings, get_airtable_config
        get_settings.cache_clear()
        
        env_vars = {
            "ANTHROPIC_API_KEY": "sk-ant-test-key-12345",
            "GOOGLE_API_KEY": "AIzaTestKey12345",
            "AIRTABLE_PAT": "patTestToken12345",
            "AIRTABLE_BASE_ID": "appTestBase12345",
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            pat, base_id = get_airtable_config()
            assert pat == "patTestToken12345"
            assert base_id == "appTestBase12345"
    
    def test_get_llm_config(self) -> None:
        """Test get_llm_config helper."""
        from config.settings import get_settings, get_llm_config
        get_settings.cache_clear()
        
        env_vars = {
            "ANTHROPIC_API_KEY": "sk-ant-test-key-12345",
            "GOOGLE_API_KEY": "AIzaTestKey12345",
            "AIRTABLE_PAT": "patTestToken12345",
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            config = get_llm_config()
            assert config["anthropic_api_key"] == "sk-ant-test-key-12345"
            assert config["google_api_key"] == "AIzaTestKey12345"
            assert "claude_model" in config
            assert "gemini_model" in config

