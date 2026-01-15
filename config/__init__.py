"""Configuration module for Alter-5 Origination Engine."""

from config.settings import get_settings, Settings, get_airtable_config, get_llm_config
from config.airtable_schema import (
    TABLES,
    COMPANY_FIELDS,
    BUSINESS_UNIT_FIELDS,
    CONTACT_FIELDS,
    CAMPAIGN_FIELDS,
    CAMPAIGN_TARGET_FIELDS,
    MARKET_CONTEXT_FIELDS,
    FEI_STATUS_OPTIONS,
    FEI_CRITERIA_OPTIONS,
)

__all__ = [
    # Settings
    "get_settings",
    "Settings",
    "get_airtable_config",
    "get_llm_config",
    # Schema
    "TABLES",
    "COMPANY_FIELDS",
    "BUSINESS_UNIT_FIELDS",
    "CONTACT_FIELDS",
    "CAMPAIGN_FIELDS",
    "CAMPAIGN_TARGET_FIELDS",
    "MARKET_CONTEXT_FIELDS",
    "FEI_STATUS_OPTIONS",
    "FEI_CRITERIA_OPTIONS",
]

