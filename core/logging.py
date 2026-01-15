"""Structured logging configuration for Alter-5 Origination Engine.

This module configures structlog for consistent, structured logging across
the entire application. Supports both console (human-readable) and JSON
(machine-readable) output formats.

Usage:
    from core.logging import get_logger, configure_logging
    
    # Configure once at startup
    configure_logging(level="INFO", format="console")
    
    # Get logger in any module
    logger = get_logger()
    logger.info("event_name", key="value", other_key=123)
"""

import logging
import sys
from typing import Literal

import structlog
from structlog.typing import Processor

from config.settings import get_settings


def _add_log_level_name(
    logger: logging.Logger | None,
    method_name: str,
    event_dict: dict,
) -> dict:
    """Add log level name to event dict."""
    event_dict["level"] = method_name.upper()
    return event_dict


def _add_service_info(
    logger: logging.Logger | None,
    method_name: str,
    event_dict: dict,
) -> dict:
    """Add service information to event dict."""
    event_dict["service"] = "origination-engine"
    return event_dict


def _filter_debug_in_production(
    logger: logging.Logger | None,
    method_name: str,
    event_dict: dict,
) -> dict:
    """Filter debug messages in production (when LOG_LEVEL != DEBUG)."""
    settings = get_settings()
    if method_name == "debug" and settings.LOG_LEVEL != "DEBUG":
        raise structlog.DropEvent
    return event_dict


def configure_logging(
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] | None = None,
    format_type: Literal["console", "json"] | None = None,
) -> None:
    """Configure structlog for the application.
    
    Should be called once at application startup. Uses settings if 
    parameters are not provided.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        format_type: Output format (console for dev, json for prod)
    """
    settings = get_settings()
    
    log_level = level or settings.LOG_LEVEL
    log_format = format_type or settings.LOG_FORMAT
    
    # Common processors for all formats
    shared_processors: list[Processor] = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        _add_log_level_name,
        _add_service_info,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Format-specific processors and renderer
    if log_format == "json":
        # JSON format for production/logging aggregation
        processors: list[Processor] = [
            *shared_processors,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Console format for development
        processors = [
            *shared_processors,
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.plain_traceback,
            ),
        ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level),
    )
    
    # Set log level for third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a configured structlog logger.
    
    Args:
        name: Optional logger name. If not provided, uses the calling module.
        
    Returns:
        Configured structlog logger instance.
        
    Example:
        logger = get_logger()
        logger.info("user_created", user_id="123", email="test@example.com")
    """
    return structlog.get_logger(name)


def log_agent_start(
    agent_name: str,
    **context: dict,
) -> None:
    """Log the start of an AI agent execution.
    
    Args:
        agent_name: Name of the agent (e.g., "Buscador_Empresas")
        **context: Additional context to log
    """
    logger = get_logger()
    logger.info(
        "agent_started",
        agent=agent_name,
        **context,
    )


def log_agent_complete(
    agent_name: str,
    duration_seconds: float,
    result_count: int | None = None,
    **context: dict,
) -> None:
    """Log the completion of an AI agent execution.
    
    Args:
        agent_name: Name of the agent
        duration_seconds: Execution time in seconds
        result_count: Number of results produced (optional)
        **context: Additional context to log
    """
    logger = get_logger()
    logger.info(
        "agent_completed",
        agent=agent_name,
        duration_seconds=round(duration_seconds, 3),
        result_count=result_count,
        **context,
    )


def log_agent_error(
    agent_name: str,
    error: Exception,
    **context: dict,
) -> None:
    """Log an AI agent error.
    
    Args:
        agent_name: Name of the agent
        error: The exception that occurred
        **context: Additional context to log
    """
    logger = get_logger()
    logger.error(
        "agent_error",
        agent=agent_name,
        error_type=type(error).__name__,
        error_message=str(error),
        **context,
        exc_info=True,
    )


def log_airtable_operation(
    operation: str,
    table: str,
    record_count: int = 1,
    **context: dict,
) -> None:
    """Log an Airtable operation.
    
    Args:
        operation: Type of operation (get, create, update, delete, query)
        table: Table name
        record_count: Number of records affected
        **context: Additional context to log
    """
    logger = get_logger()
    logger.debug(
        "airtable_operation",
        operation=operation,
        table=table,
        record_count=record_count,
        **context,
    )


def log_llm_call(
    model: str,
    prompt_tokens: int | None = None,
    completion_tokens: int | None = None,
    duration_seconds: float | None = None,
    **context: dict,
) -> None:
    """Log an LLM API call.
    
    Args:
        model: Model name (e.g., "claude-sonnet-4-20250514")
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
        duration_seconds: Call duration in seconds
        **context: Additional context to log
    """
    logger = get_logger()
    logger.info(
        "llm_call",
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        duration_seconds=round(duration_seconds, 3) if duration_seconds else None,
        total_tokens=(prompt_tokens or 0) + (completion_tokens or 0),
        **context,
    )


def log_campaign_event(
    event: str,
    campaign_id: str,
    **context: dict,
) -> None:
    """Log a campaign-related event.
    
    Args:
        event: Event type (created, updated, targets_selected, sent, etc.)
        campaign_id: Campaign record ID
        **context: Additional context to log
    """
    logger = get_logger()
    logger.info(
        "campaign_event",
        event=event,
        campaign_id=campaign_id,
        **context,
    )


def log_fei_evaluation(
    company_id: str,
    status: str,
    confidence: float,
    criteria_met: list[str] | None = None,
    **context: dict,
) -> None:
    """Log an FEI eligibility evaluation.
    
    Args:
        company_id: Company record ID
        status: FEI status result
        confidence: Confidence score (0-100)
        criteria_met: List of criteria codes met
        **context: Additional context to log
    """
    logger = get_logger()
    logger.info(
        "fei_evaluation",
        company_id=company_id,
        status=status,
        confidence=round(confidence, 1),
        criteria_met=criteria_met or [],
        criteria_count=len(criteria_met) if criteria_met else 0,
        **context,
    )


# Auto-configure logging on import if not already configured
# This ensures logging works even if configure_logging() is not called
_configured = False


def _auto_configure() -> None:
    """Auto-configure logging with defaults if not already configured."""
    global _configured
    if not _configured:
        try:
            configure_logging()
            _configured = True
        except Exception:
            # Silently fail if settings can't be loaded
            # This allows import to work even without .env
            pass


_auto_configure()

