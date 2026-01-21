"""APScheduler-based scheduler for 24/7 automated operations.

This module provides a scheduler that runs independently of the Celery
task queue for lightweight, time-based tasks.

Features:
- Trigger scanning at configurable intervals
- Follow-up execution every 30 minutes
- Daily summary reports
- Configurable maintenance windows

Usage:
    from orchestration.scheduler import start_scheduler, stop_scheduler
    
    # Start the scheduler
    start_scheduler()
    
    # Stop the scheduler
    stop_scheduler()
"""

import asyncio
from datetime import datetime
from typing import Callable, Optional

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

from config.settings import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

# Global scheduler instance
_scheduler: Optional[AsyncIOScheduler] = None


# ==============================================================================
# JOB DEFINITIONS
# ==============================================================================

async def trigger_scan_job():
    """Scan for market triggers from RSS feeds and other sources."""
    logger.info("scheduler_job_started", job="trigger_scan")
    
    try:
        from agents.trigger_detector import get_trigger_detector
        
        detector = get_trigger_detector()
        triggers = await detector.scan_feeds()
        
        logger.info(
            "scheduler_job_completed",
            job="trigger_scan",
            triggers_found=len(triggers),
        )
        
        return len(triggers)
    except Exception as e:
        logger.error("scheduler_job_failed", job="trigger_scan", error=str(e))
        raise


async def followup_execution_job():
    """Execute scheduled follow-up emails."""
    logger.info("scheduler_job_started", job="followup_execution")
    
    try:
        from agents.followup_manager import get_followup_manager
        
        manager = get_followup_manager()
        executed = await manager.execute_scheduled_followups()
        
        logger.info(
            "scheduler_job_completed",
            job="followup_execution",
            followups_sent=len(executed),
        )
        
        return len(executed)
    except Exception as e:
        logger.error("scheduler_job_failed", job="followup_execution", error=str(e))
        raise


async def daily_summary_job():
    """Generate and send daily summary to Slack."""
    logger.info("scheduler_job_started", job="daily_summary")
    
    try:
        from integrations.slack import get_slack_client
        from core.airtable_client import get_airtable_client
        
        slack = get_slack_client()
        airtable = get_airtable_client()
        
        # Gather statistics
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Count today's activities
        campaigns = airtable.query_records(
            "Campaigns",
            formula=f"DATESTR({{Created At}}) = '{today}'",
        )
        
        triggers = airtable.query_records(
            "Detected_Triggers",
            formula=f"DATESTR({{Published_At}}) = '{today}'",
        )
        
        followups = airtable.query_records(
            "Followup_Tasks",
            formula=f"AND(DATESTR({{Executed_At}}) = '{today}', {{Executed}} = 1)",
        )
        
        # Send summary
        await slack.send_daily_summary(
            date=today,
            campaigns_created=len(campaigns),
            triggers_detected=len(triggers),
            followups_sent=len(followups),
        )
        
        logger.info(
            "scheduler_job_completed",
            job="daily_summary",
            campaigns=len(campaigns),
            triggers=len(triggers),
            followups=len(followups),
        )
    except Exception as e:
        logger.error("scheduler_job_failed", job="daily_summary", error=str(e))
        raise


async def health_check_job():
    """Perform system health check and alert if issues found."""
    logger.debug("scheduler_job_started", job="health_check")
    
    try:
        issues = []
        
        # Check Airtable connection
        try:
            from core.airtable_client import get_airtable_client
            airtable = get_airtable_client()
            airtable.query_records("Companies", max_records=1)
        except Exception as e:
            issues.append(f"Airtable: {str(e)[:50]}")
        
        # Check API keys configured
        if not settings.ANTHROPIC_API_KEY:
            issues.append("Claude API key not configured")
        if not settings.GOOGLE_API_KEY:
            issues.append("Gemini API key not configured")
        
        if issues:
            from integrations.slack import get_slack_client
            slack = get_slack_client()
            await slack.send_error_alert(
                error_type="Health Check Failed",
                error_message="\n".join(issues),
                component="Scheduler",
            )
            logger.warning("health_check_issues", issues=issues)
        else:
            logger.debug("scheduler_job_completed", job="health_check", status="healthy")
        
        return len(issues) == 0
    except Exception as e:
        logger.error("scheduler_job_failed", job="health_check", error=str(e))
        raise


# ==============================================================================
# EVENT HANDLERS
# ==============================================================================

def job_executed_handler(event):
    """Handle successful job execution."""
    logger.debug(
        "job_executed",
        job_id=event.job_id,
        scheduled_time=event.scheduled_run_time.isoformat() if event.scheduled_run_time else None,
    )


def job_error_handler(event):
    """Handle job execution error."""
    logger.error(
        "job_error",
        job_id=event.job_id,
        exception=str(event.exception),
        traceback=str(event.traceback) if event.traceback else None,
    )


# ==============================================================================
# SCHEDULER MANAGEMENT
# ==============================================================================

def get_scheduler() -> AsyncIOScheduler:
    """Get or create the scheduler instance."""
    global _scheduler
    
    if _scheduler is None:
        _scheduler = AsyncIOScheduler(
            timezone="Europe/Madrid",
            job_defaults={
                "coalesce": True,  # Combine missed executions
                "max_instances": 1,  # Only one instance per job
                "misfire_grace_time": 300,  # 5 minutes grace for missed jobs
            },
        )
        
        # Add event listeners
        _scheduler.add_listener(job_executed_handler, EVENT_JOB_EXECUTED)
        _scheduler.add_listener(job_error_handler, EVENT_JOB_ERROR)
        
        logger.info("scheduler_created")
    
    return _scheduler


def configure_jobs(scheduler: AsyncIOScheduler):
    """Configure all scheduled jobs."""
    
    # Trigger scan: every hour
    scheduler.add_job(
        trigger_scan_job,
        trigger=IntervalTrigger(hours=1),
        id="trigger_scan",
        name="Trigger Scanner",
        replace_existing=True,
    )
    logger.info("job_configured", job_id="trigger_scan", interval="1 hour")
    
    # Follow-up execution: every 30 minutes
    scheduler.add_job(
        followup_execution_job,
        trigger=IntervalTrigger(minutes=30),
        id="followup_execution",
        name="Follow-up Executor",
        replace_existing=True,
    )
    logger.info("job_configured", job_id="followup_execution", interval="30 minutes")
    
    # Daily summary: 8:00 AM Madrid time
    scheduler.add_job(
        daily_summary_job,
        trigger=CronTrigger(hour=8, minute=0),
        id="daily_summary",
        name="Daily Summary",
        replace_existing=True,
    )
    logger.info("job_configured", job_id="daily_summary", schedule="08:00 daily")
    
    # Health check: every 15 minutes
    scheduler.add_job(
        health_check_job,
        trigger=IntervalTrigger(minutes=15),
        id="health_check",
        name="Health Check",
        replace_existing=True,
    )
    logger.info("job_configured", job_id="health_check", interval="15 minutes")


def start_scheduler():
    """Start the scheduler with all configured jobs."""
    scheduler = get_scheduler()
    
    if scheduler.running:
        logger.warning("scheduler_already_running")
        return
    
    # Configure jobs
    configure_jobs(scheduler)
    
    # Start scheduler
    scheduler.start()
    logger.info("scheduler_started", jobs=len(scheduler.get_jobs()))


def stop_scheduler():
    """Stop the scheduler gracefully."""
    global _scheduler
    
    if _scheduler is not None and _scheduler.running:
        _scheduler.shutdown(wait=True)
        logger.info("scheduler_stopped")
    
    _scheduler = None


def get_scheduler_status() -> dict:
    """Get current scheduler status and job information."""
    scheduler = get_scheduler()
    
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger),
        })
    
    return {
        "running": scheduler.running,
        "timezone": str(scheduler.timezone),
        "jobs": jobs,
    }


def run_job_now(job_id: str):
    """Manually trigger a job to run immediately."""
    scheduler = get_scheduler()
    
    job = scheduler.get_job(job_id)
    if job is None:
        raise ValueError(f"Job '{job_id}' not found")
    
    # Run the job
    scheduler.modify_job(job_id, next_run_time=datetime.now())
    logger.info("job_triggered_manually", job_id=job_id)


# ==============================================================================
# CLI ENTRY POINT
# ==============================================================================

def main():
    """Run the scheduler as a standalone process."""
    import signal
    
    logger.info("starting_scheduler_process")
    
    # Start scheduler
    start_scheduler()
    
    # Handle shutdown signals
    loop = asyncio.get_event_loop()
    
    def shutdown(signum, frame):
        logger.info("shutdown_signal_received", signal=signum)
        stop_scheduler()
        loop.stop()
    
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    
    # Run event loop
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_scheduler()
        logger.info("scheduler_process_stopped")


if __name__ == "__main__":
    main()
