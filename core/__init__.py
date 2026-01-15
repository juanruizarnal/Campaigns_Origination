"""Core module for Alter-5 Origination Engine."""

from core.models import (
    # Enums
    FEIStatus,
    FEICriteria,
    CampaignStatus,
    CampaignSize,
    CampaignPriority,
    ProductLine,
    TargetStatus,
    ContextType,
    ContextStatus,
    RecordStatus,
    KeyPerson,
    # Entities
    Company,
    BusinessUnit,
    Contact,
    Campaign,
    CampaignTarget,
    MarketContext,
    # Evaluation
    FEIEvaluation,
    SearchCriteria,
    SelectionResult,
    EmailDraft,
)
from core.airtable_client import AirtableClient, AirtableError, get_airtable_client
from core.logging import (
    configure_logging,
    get_logger,
    log_agent_start,
    log_agent_complete,
    log_agent_error,
    log_airtable_operation,
    log_llm_call,
    log_campaign_event,
    log_fei_evaluation,
)

__all__ = [
    # Enums
    "FEIStatus",
    "FEICriteria",
    "CampaignStatus",
    "CampaignSize",
    "CampaignPriority",
    "ProductLine",
    "TargetStatus",
    "ContextType",
    "ContextStatus",
    "RecordStatus",
    "KeyPerson",
    # Entities
    "Company",
    "BusinessUnit",
    "Contact",
    "Campaign",
    "CampaignTarget",
    "MarketContext",
    # Evaluation
    "FEIEvaluation",
    "SearchCriteria",
    "SelectionResult",
    "EmailDraft",
    # Client
    "AirtableClient",
    "AirtableError",
    "get_airtable_client",
    # Logging
    "configure_logging",
    "get_logger",
    "log_agent_start",
    "log_agent_complete",
    "log_agent_error",
    "log_airtable_operation",
    "log_llm_call",
    "log_campaign_event",
    "log_fei_evaluation",
]

