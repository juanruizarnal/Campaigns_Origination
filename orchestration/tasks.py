"""Celery tasks for the 24/7 autonomous origination system.

Defines background tasks for:
- Trigger scanning (RSS, Twitter, etc.)
- Follow-up execution
- Campaign creation from triggers
- Data enrichment and FEI evaluation

Usage:
    # Start worker
    celery -A orchestration.tasks worker -l info

    # Start beat scheduler
    celery -A orchestration.tasks beat -l info
"""

from datetime import datetime, timedelta

from celery import Celery
from celery.schedules import crontab
import structlog

from config.settings import get_settings
from core.async_utils import run_async

logger = structlog.get_logger(__name__)
settings = get_settings()

# Initialize Celery - Use REDIS_URL from settings
celery_app = Celery(
    "alter5_origination",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Madrid",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max
    task_soft_time_limit=540,  # 9 minutes soft limit
    worker_prefetch_multiplier=1,  # Process one task at a time
    task_acks_late=True,  # Acknowledge after task completes
    # Retry configuration
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
)

# Beat schedule - periodic tasks
celery_app.conf.beat_schedule = {
    # Scan triggers every hour
    "scan-triggers-hourly": {
        "task": "orchestration.tasks.scan_triggers",
        "schedule": crontab(minute=0),  # Every hour at :00
    },
    # Execute due follow-ups every 30 minutes
    "execute-followups": {
        "task": "orchestration.tasks.execute_scheduled_followups",
        "schedule": crontab(minute="*/30"),  # Every 30 minutes
    },
    # Process high-relevance triggers into campaigns every 2 hours
    "auto-create-campaigns": {
        "task": "orchestration.tasks.auto_create_campaigns_from_triggers",
        "schedule": crontab(minute=15, hour="*/2"),  # Every 2 hours at :15
    },
    # Send daily summary at 8 AM
    "daily-summary": {
        "task": "orchestration.tasks.send_daily_summary",
        "schedule": crontab(minute=0, hour=8),  # 8:00 AM
    },
}


# ==============================================================================
# TRIGGER DETECTION TASKS
# ==============================================================================

@celery_app.task(bind=True, name="orchestration.tasks.scan_triggers")
def scan_triggers(self):
    """Scan configured sources for new market triggers.

    Runs hourly to detect new triggers from RSS feeds, Twitter, etc.
    """
    logger.info("celery_task_started", task="scan_triggers")

    try:
        from agents.trigger_detector import TriggerDetector
        from core.airtable_client import get_airtable_client

        detector = TriggerDetector()
        airtable = get_airtable_client()

        # Run async scan using safe helper
        triggers = run_async(detector.scan_feeds())

        # Save triggers to Airtable
        saved_count = 0
        high_relevance_count = 0

        for trigger in triggers:
            try:
                fields = {
                    "Context_Title": trigger.title,
                    "Source_Name": trigger.source_name,
                    "Source_URL": trigger.source_url,
                    "Summary": trigger.summary,
                    "Campaign_Potential": int(trigger.relevance_score * 5),
                    "Status": "New",
                    "Context_Type": "News_Sectoral",
                }
                airtable.create_record("market_contexts", fields)
                saved_count += 1

                if trigger.relevance_score >= 0.8:
                    high_relevance_count += 1

            except Exception as e:
                logger.warning("trigger_save_failed", error=str(e))

        # Send alert if high relevance triggers found
        if high_relevance_count > 0:
            _send_slack_alert(
                f"📰 {high_relevance_count} triggers de alta relevancia detectados",
                priority="medium",
            )

        logger.info(
            "celery_task_completed",
            task="scan_triggers",
            triggers_found=len(triggers),
            saved=saved_count,
            high_relevance=high_relevance_count,
        )

        return {
            "success": True,
            "triggers_found": len(triggers),
            "saved": saved_count,
            "high_relevance": high_relevance_count,
        }

    except Exception as e:
        logger.error("celery_task_failed", task="scan_triggers", error=str(e))
        return {"success": False, "error": str(e)}


# ==============================================================================
# FOLLOW-UP TASKS
# ==============================================================================

@celery_app.task(bind=True, name="orchestration.tasks.execute_scheduled_followups")
def execute_scheduled_followups(self):
    """Execute follow-ups that are due.

    Runs every 30 minutes to send scheduled follow-up emails.
    """
    logger.info("celery_task_started", task="execute_followups")

    try:
        from agents.followup_manager import FollowupManager

        manager = FollowupManager()

        # Run async execution using safe helper
        executed = run_async(manager.execute_scheduled_followups())

        logger.info(
            "celery_task_completed",
            task="execute_followups",
            executed=executed,
        )

        return {"success": True, "executed": executed}

    except Exception as e:
        logger.error("celery_task_failed", task="execute_followups", error=str(e))
        return {"success": False, "error": str(e)}


@celery_app.task(bind=True, name="orchestration.tasks.process_email_event")
def process_email_event(self, event_data: dict):
    """Process a single email event (from webhook).

    Called asynchronously when Mailchimp webhook is received.
    """
    logger.info("celery_task_started", task="process_email_event", event_type=event_data.get("event_type"))

    try:
        from agents.followup_manager import FollowupManager
        from core.models import MailchimpWebhookEvent, MailchimpEventType

        # Reconstruct event
        event = MailchimpWebhookEvent(
            event_type=MailchimpEventType(event_data["event_type"]),
            email=event_data["email"],
            campaign_id=event_data["campaign_id"],
            url_clicked=event_data.get("url_clicked"),
        )

        manager = FollowupManager()

        # Run async using safe helper
        action = run_async(manager.process_email_event(event))

        logger.info(
            "celery_task_completed",
            task="process_email_event",
            action=str(action),
        )

        return {"success": True, "action": str(action)}

    except Exception as e:
        logger.error("celery_task_failed", task="process_email_event", error=str(e))
        return {"success": False, "error": str(e)}


# ==============================================================================
# CAMPAIGN AUTOMATION TASKS
# ==============================================================================

@celery_app.task(bind=True, name="orchestration.tasks.auto_create_campaigns_from_triggers")
def auto_create_campaigns_from_triggers(self):
    """Automatically create campaigns from high-relevance triggers.

    Runs every 2 hours to process new triggers with relevance >= 0.8.
    Creates draft campaigns and sends notification for approval.
    """
    logger.info("celery_task_started", task="auto_create_campaigns")

    try:
        from core.airtable_client import get_airtable_client

        airtable = get_airtable_client()

        # Get unprocessed high-relevance triggers
        contexts = airtable.query_records(
            "market_contexts",
            formula="AND({Status}='New', {Campaign_Potential}>=4)",
            max_records=5,
        )

        campaigns_created = 0

        for context in contexts:
            try:
                fields = context.get("fields", {})
                trigger_title = fields.get("Context_Title", "")

                # Create draft campaign
                campaign_fields = {
                    "Campaign Name": f"Auto: {trigger_title[:40]}",
                    "Status": "Draft",
                    "Campaign Rationale": fields.get("Summary", trigger_title),
                    "Campaign Size": "Micro-Targeting",
                    "Priority": "High",
                    "Market Context": [context["id"]],
                    "AI_Generated": True,
                }

                campaign = airtable.create_record("campaigns", campaign_fields)

                # Update trigger status
                airtable.update_record("market_contexts", context["id"], {
                    "Status": "Campaign_Created",
                    "Campaigns": [campaign["id"]],
                })

                campaigns_created += 1

                # Send notification
                _send_slack_alert(
                    f"🤖 Campaña automática creada: {trigger_title[:50]}",
                    priority="medium",
                    campaign_id=campaign["id"],
                )

            except Exception as e:
                logger.warning("campaign_creation_failed", trigger=context["id"], error=str(e))

        logger.info(
            "celery_task_completed",
            task="auto_create_campaigns",
            campaigns_created=campaigns_created,
        )

        return {"success": True, "campaigns_created": campaigns_created}

    except Exception as e:
        logger.error("celery_task_failed", task="auto_create_campaigns", error=str(e))
        return {"success": False, "error": str(e)}


# ==============================================================================
# ENRICHMENT TASKS
# ==============================================================================

@celery_app.task(bind=True, name="orchestration.tasks.enrich_company")
def enrich_company_task(self, company_id: str):
    """Enrich a single company asynchronously.

    Called when a new company is added and needs enrichment.
    """
    logger.info("celery_task_started", task="enrich_company", company_id=company_id)

    try:
        from agents.enriquecedor import EnriquecedorDatos

        enriquecedor = EnriquecedorDatos()

        result = enriquecedor.enrich_company(
            company_id,
            include_financials=True,
            include_contacts=True,
        )

        success = getattr(result, "success", False)

        logger.info(
            "celery_task_completed",
            task="enrich_company",
            company_id=company_id,
            success=success,
        )

        return {"success": success, "company_id": company_id}

    except Exception as e:
        logger.error("celery_task_failed", task="enrich_company", company_id=company_id, error=str(e))
        return {"success": False, "error": str(e)}


@celery_app.task(bind=True, name="orchestration.tasks.evaluate_fei")
def evaluate_fei_task(self, company_id: str):
    """Evaluate FEI eligibility for a company asynchronously."""
    logger.info("celery_task_started", task="evaluate_fei", company_id=company_id)

    try:
        from agents.evaluador_fei import EvaluadorFEI

        evaluador = EvaluadorFEI()

        result = evaluador.evaluate(company_id)

        status = getattr(result, "status", None)
        status_value = status.value if hasattr(status, "value") else str(status)

        logger.info(
            "celery_task_completed",
            task="evaluate_fei",
            company_id=company_id,
            status=status_value,
        )

        return {"success": True, "company_id": company_id, "status": status_value}

    except Exception as e:
        logger.error("celery_task_failed", task="evaluate_fei", company_id=company_id, error=str(e))
        return {"success": False, "error": str(e)}


# ==============================================================================
# REPORTING TASKS
# ==============================================================================

@celery_app.task(bind=True, name="orchestration.tasks.send_daily_summary")
def send_daily_summary(self):
    """Send daily summary to Slack.

    Runs at 8 AM to provide a daily report of origination activity.
    """
    logger.info("celery_task_started", task="daily_summary")

    try:
        from core.airtable_client import get_airtable_client

        airtable = get_airtable_client()
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        # Get counts (simplified - would use proper date filtering in production)
        companies = airtable.query_records("companies", max_records=1000)
        campaigns = airtable.query_records("campaigns", max_records=100)
        targets = airtable.query_records("campaign_targets", max_records=500)

        # Calculate metrics
        total_companies = len(companies)
        fei_eligible = len([c for c in companies if c.get("fields", {}).get("FEI_Status") == "Eligible"])
        active_campaigns = len([c for c in campaigns if c.get("fields", {}).get("Status") in ["Active", "Scheduled"]])
        hot_leads = len([t for t in targets if t.get("fields", {}).get("Status") in ["Clicked", "Replied"]])

        summary = f"""📊 *Resumen Diario de Originación*

*Empresas:*
• Total: {total_companies}
• FEI Elegibles: {fei_eligible}

*Campañas:*
• Activas: {active_campaigns}

*Engagement:*
• Hot Leads: {hot_leads}

_Generado automáticamente - {datetime.now().strftime("%d/%m/%Y %H:%M")}_
"""

        _send_slack_alert(summary, priority="low", channel="general")

        logger.info(
            "celery_task_completed",
            task="daily_summary",
            total_companies=total_companies,
            fei_eligible=fei_eligible,
        )

        return {
            "success": True,
            "total_companies": total_companies,
            "fei_eligible": fei_eligible,
            "active_campaigns": active_campaigns,
        }

    except Exception as e:
        logger.error("celery_task_failed", task="daily_summary", error=str(e))
        return {"success": False, "error": str(e)}


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def _send_slack_alert(
    message: str,
    priority: str = "medium",
    channel: str = None,
    campaign_id: str = None,
):
    """Send a Slack alert (async-safe wrapper)."""
    try:
        from integrations.slack import SlackClient

        client = SlackClient()
        if not client.is_configured():
            logger.debug("slack_not_configured", message=message)
            return

        if campaign_id:
            run_async(
                client.send_campaign_created_alert(
                    campaign_name=message,
                    campaign_id=campaign_id,
                    target_count=0,
                    trigger=message,
                    is_automatic=True,
                )
            )
        else:
            target_channel = channel or settings.SLACK_CHANNEL_ORIGINATION
            run_async(
                client._send_message(target_channel, message, priority=priority)
            )

    except Exception as e:
        logger.warning("slack_alert_failed", error=str(e))
