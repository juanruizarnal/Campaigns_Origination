"""Pytest configuration and shared fixtures for Alter-5 Origination Engine tests.

This module provides:
- Common fixtures for mocking external services
- Environment setup for tests
- Shared test utilities
"""

import os
from datetime import date, datetime
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest


# ==============================================================================
# ENVIRONMENT FIXTURES
# ==============================================================================


@pytest.fixture(scope="session", autouse=True)
def mock_env_session() -> Generator[None, None, None]:
    """Set up mock environment variables for entire test session.
    
    This ensures tests don't accidentally use real API keys.
    """
    env_vars = {
        "ANTHROPIC_API_KEY": "sk-ant-test-key-12345",
        "GOOGLE_API_KEY": "AIzaTestKey12345",
        "AIRTABLE_PAT": "patTestToken12345",
        "AIRTABLE_BASE_ID": "appTestBase12345",
        "LOG_LEVEL": "DEBUG",
        "LOG_FORMAT": "console",
    }
    with patch.dict(os.environ, env_vars, clear=False):
        yield


@pytest.fixture
def clear_settings_cache() -> Generator[None, None, None]:
    """Clear settings cache before and after test."""
    from config.settings import get_settings
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def reset_airtable_singleton() -> Generator[None, None, None]:
    """Reset Airtable client singleton before test."""
    import core.airtable_client as module
    original = module._client
    module._client = None
    yield
    module._client = original


# ==============================================================================
# MOCK DATA FIXTURES
# ==============================================================================


@pytest.fixture
def sample_company_record() -> dict:
    """Sample Airtable company record."""
    return {
        "id": "recCompanySample123",
        "createdTime": "2024-01-01T00:00:00.000Z",
        "fields": {
            "Company Name": "Green Energy Corp",
            "Home URL": "https://greenenergy.com",
            "Linkedin URL": "https://linkedin.com/company/greenenergy",
            "Description": "A leading renewable energy company",
            "Num Employees": 500,
            "HQ Country": ["recSpain"],
            "HQ Address": "Madrid, Spain",
            "Tax ID": "B12345678",
            "FEI_Status": "Eligible",
            "FEI_Criteria_Met": ["1.4_Green_Business_90", "1.6_Environmental_Certificate"],
            "FEI_Confidence": 0.85,
            "FEI_Last_Check": "2024-01-15",
            "FEI_Notes": "ISO 14001 certified, >90% green revenue",
            "Source": ["Research", "LinkedIn"],
        },
    }


@pytest.fixture
def sample_business_unit_record() -> dict:
    """Sample Airtable business unit record."""
    return {
        "id": "recBUSample123",
        "createdTime": "2024-01-01T00:00:00.000Z",
        "fields": {
            "Business Unit Name": "Solar Division",
            "Company": ["recCompanySample123"],
            "Sector": ["recSectorRenewables"],
            "Focus Region": ["EMEA", "AMER"],
            "Record Status": "Active",
            "Last_Outreach_Date": "2023-10-01",
            "Is_In_Cooling_Off": False,
            "Revenue_Percentage": 0.95,
        },
    }


@pytest.fixture
def sample_contact_record() -> dict:
    """Sample Airtable contact record."""
    return {
        "id": "recContactSample123",
        "createdTime": "2024-01-01T00:00:00.000Z",
        "fields": {
            "First Name": "John",
            "Last Name": "Doe",
            "Full Name": "John Doe",
            "Email": "john.doe@greenenergy.com",
            "Phone Number": "+34123456789",
            "Linkedin URL": "https://linkedin.com/in/johndoe",
            "Role": "CFO",
            "Key Person": "Yes",
            "Business Unit": ["recBUSample123"],
        },
    }


@pytest.fixture
def sample_campaign_record() -> dict:
    """Sample Airtable campaign record."""
    return {
        "id": "recCampaignSample123",
        "createdTime": "2024-01-01T00:00:00.000Z",
        "fields": {
            "Campaign_Name": "Q1 Green Finance Outreach",
            "Description": "Target FEI-eligible renewable energy companies",
            "Campaign_Size": "Micro-Targeting",
            "Status": "Draft",
            "Product_Line": ["FEI_Guarantee", "Project_Finance"],
            "Priority": "High",
            "Scheduled_Start_Date": "2024-02-01",
            "Scheduled_End_Date": "2024-03-31",
            "Target_Ticket_Min": 1000000,
            "Target_Ticket_Max": 10000000,
            "AI_Generated": True,
        },
    }


@pytest.fixture
def sample_campaign_target_record() -> dict:
    """Sample Airtable campaign target record."""
    return {
        "id": "recTargetSample123",
        "createdTime": "2024-01-01T00:00:00.000Z",
        "fields": {
            "Target_Name": "Green Energy Corp - Solar Division",
            "Campaign": ["recCampaignSample123"],
            "Business_Unit": ["recBUSample123"],
            "Contact": ["recContactSample123"],
            "Selection_Justification": "FEI-eligible with ISO 14001, matches sector criteria",
            "Personalization_Context": "Recent solar expansion project",
            "Personalized_Email_Subject": "Financing for your solar expansion",
            "Personalized_Email_Body": "Dear John, we noticed your recent solar expansion...",
            "Fit_Score": 0.87,
            "AI_Confidence": 0.92,
            "Status": "Pending_Review",
        },
    }


@pytest.fixture
def sample_market_context_record() -> dict:
    """Sample Airtable market context record."""
    return {
        "id": "recContextSample123",
        "createdTime": "2024-01-01T00:00:00.000Z",
        "fields": {
            "Context_Title": "EU Green Deal New Subsidies Announced",
            "Context_Type": "Regulatory_Change",
            "Source_URL": "https://ec.europa.eu/greendeal",
            "Source_Name": "European Commission",
            "Publication_Date": "2024-01-10",
            "Summary": "New subsidies for renewable energy projects",
            "Key_Implications": "Companies can access additional funding",
            "Campaign_Potential": 5,
            "Status": "New",
            "Tags": ["Renewables", "ESG", "FEI_Eligible"],
            "Affected_Sectors": ["recSectorRenewables"],
            "Affected_Countries": ["recSpain", "recGermany", "recFrance"],
            "AI_Generated": True,
        },
    }


# ==============================================================================
# MODEL FIXTURES
# ==============================================================================


@pytest.fixture
def sample_company() -> "Company":
    """Sample Company model instance."""
    from core.models import Company, FEIStatus, FEICriteria
    
    return Company(
        id="recCompany123",
        name="Test Green Corp",
        home_url="https://testgreen.com",
        fei_status=FEIStatus.ELIGIBLE,
        fei_criteria_met=[FEICriteria.ENVIRONMENTAL_CERTIFICATE],
        fei_confidence=90.0,
        fei_last_check=date(2024, 1, 15),
    )


@pytest.fixture
def sample_business_unit() -> "BusinessUnit":
    """Sample BusinessUnit model instance."""
    from core.models import BusinessUnit, RecordStatus
    
    return BusinessUnit(
        id="recBU123",
        name="Test Division",
        company_id="recCompany123",
        record_status=RecordStatus.ACTIVE,
        is_in_cooling_off=False,
    )


@pytest.fixture
def sample_contact() -> "Contact":
    """Sample Contact model instance."""
    from core.models import Contact, KeyPerson
    
    return Contact(
        id="recContact123",
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@test.com",
        role="CEO",
        key_person=KeyPerson.YES,
        business_unit_ids=["recBU123"],
    )


# ==============================================================================
# MOCK CLIENT FIXTURES
# ==============================================================================


@pytest.fixture
def mock_airtable_client() -> Generator[MagicMock, None, None]:
    """Mock AirtableClient for testing without API calls."""
    with patch("core.airtable_client.AirtableClient") as MockClient:
        mock_instance = MagicMock()
        MockClient.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_anthropic_client() -> Generator[MagicMock, None, None]:
    """Mock Anthropic client for testing without API calls."""
    with patch("anthropic.Anthropic") as MockClient:
        mock_instance = MagicMock()
        MockClient.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_google_client() -> Generator[MagicMock, None, None]:
    """Mock Google Generative AI client for testing without API calls."""
    with patch("google.generativeai.GenerativeModel") as MockClient:
        mock_instance = MagicMock()
        MockClient.return_value = mock_instance
        yield mock_instance


# ==============================================================================
# UTILITY FIXTURES
# ==============================================================================


@pytest.fixture
def frozen_date() -> date:
    """Fixed date for consistent testing."""
    return date(2024, 1, 15)


@pytest.fixture
def frozen_datetime() -> datetime:
    """Fixed datetime for consistent testing."""
    return datetime(2024, 1, 15, 10, 30, 0)


# ==============================================================================
# PYTEST CONFIGURATION
# ==============================================================================


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests (may require API access)",
    )
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow running",
    )
    config.addinivalue_line(
        "markers",
        "agent: marks tests for AI agent functionality",
    )

