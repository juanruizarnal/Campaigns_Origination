"""FastAPI webhooks for receiving external service events.

Handles webhooks from:
- Mailchimp: Email opens, clicks, bounces, unsubscribes
- Slack: Slash commands and interactions (future)

Usage:
    uvicorn api.webhooks:app --host 0.0.0.0 --port 8000
"""

import asyncio
import hashlib
import hmac
from datetime import datetime
from typing import Optional

import structlog
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel

from config.settings import get_settings
from core.models import MailchimpWebhookEvent, MailchimpEventType
from agents.followup_manager import get_followup_manager, process_mailchimp_event

logger = structlog.get_logger(__name__)

app = FastAPI(
    title="Alter-5 Origination Webhooks",
    description="Webhook endpoints for external service integrations",
    version="1.0.0",
)


# ==============================================================================
# MAILCHIMP WEBHOOK MODELS
# ==============================================================================

class MailchimpWebhookPayload(BaseModel):
    """Mailchimp webhook payload structure."""
    type: str  # subscribe, unsubscribe, campaign, open, click, etc.
    fired_at: str  # ISO timestamp
    data: dict  # Event-specific data


# ==============================================================================
# MAILCHIMP WEBHOOK ENDPOINT
# ==============================================================================

@app.get("/webhook/mailchimp")
async def mailchimp_webhook_verify(request: Request):
    """Verify endpoint for Mailchimp webhook setup.
    
    Mailchimp sends a GET request to verify the webhook URL.
    We just need to return a 200 OK.
    """
    logger.info("mailchimp_webhook_verification")
    return {"status": "ok", "message": "Webhook endpoint verified"}


@app.post("/webhook/mailchimp")
async def mailchimp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """Receive and process Mailchimp webhook events.
    
    Processes events:
    - open: Email was opened
    - click: Link was clicked  
    - bounce: Email bounced
    - unsubscribe: User unsubscribed
    
    Processing is done in background to respond quickly to Mailchimp.
    """
    try:
        # Get raw body for signature verification
        body = await request.body()
        form_data = await request.form()
        
        # Log incoming webhook
        logger.info(
            "mailchimp_webhook_received",
            form_keys=list(form_data.keys()),
        )
        
        # Parse event type and data
        event_type = form_data.get("type", "")
        fired_at_str = form_data.get("fired_at", "")
        
        # Parse nested data (Mailchimp sends data as form fields)
        email = form_data.get("data[email]", "")
        campaign_id = form_data.get("data[id]", "")  # Campaign ID
        url_clicked = form_data.get("data[url]", "")  # For click events
        
        # Validate event type
        supported_events = {
            "open": MailchimpEventType.OPEN,
            "click": MailchimpEventType.CLICK,
            "bounce": MailchimpEventType.BOUNCE,
            "hard_bounce": MailchimpEventType.BOUNCE,
            "soft_bounce": MailchimpEventType.BOUNCE,
            "unsubscribe": MailchimpEventType.UNSUBSCRIBE,
            "spam": MailchimpEventType.SPAM,
        }
        
        if event_type not in supported_events:
            logger.debug("mailchimp_event_ignored", event_type=event_type)
            return {"status": "ignored", "reason": f"Event type '{event_type}' not processed"}
        
        # Parse timestamp
        try:
            timestamp = datetime.fromisoformat(fired_at_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            timestamp = datetime.now()
        
        # Create event model
        event = MailchimpWebhookEvent(
            event_type=supported_events[event_type],
            email=email,
            campaign_id=campaign_id,
            timestamp=timestamp,
            url_clicked=url_clicked if event_type == "click" else None,
            user_agent=form_data.get("data[user_agent]", ""),
            ip_address=form_data.get("data[ip]", ""),
        )
        
        logger.info(
            "mailchimp_event_parsed",
            event_type=event.event_type.value,
            email=event.email,
            campaign_id=event.campaign_id,
        )
        
        # Process in background
        background_tasks.add_task(process_mailchimp_event_task, event)
        
        return {
            "status": "accepted",
            "event_type": event_type,
            "email": email[:20] + "..." if email else None,
        }
        
    except Exception as e:
        logger.error("mailchimp_webhook_error", error=str(e))
        # Return 200 even on errors to avoid Mailchimp retries
        return {"status": "error", "message": str(e)}


async def process_mailchimp_event_task(event: MailchimpWebhookEvent):
    """Background task to process Mailchimp event."""
    try:
        action = await process_mailchimp_event(event)
        logger.info(
            "mailchimp_event_processed",
            event_type=event.event_type.value,
            email=event.email,
            action=action.value if hasattr(action, 'value') else str(action),
        )
    except Exception as e:
        logger.error(
            "mailchimp_event_processing_failed",
            event_type=event.event_type.value,
            email=event.email,
            error=str(e),
        )


# ==============================================================================
# SLACK WEBHOOK ENDPOINTS (FUTURE)
# ==============================================================================

@app.post("/webhook/slack/commands")
async def slack_commands(request: Request):
    """Handle Slack slash commands.
    
    Commands:
    - /campaign: Create a new campaign
    - /hot-leads: List current hot leads
    - /stats: Get quick stats
    """
    form_data = await request.form()
    
    command = form_data.get("command", "")
    text = form_data.get("text", "")
    user_id = form_data.get("user_id", "")
    
    logger.info("slack_command_received", command=command, user=user_id)
    
    # TODO: Implement commands
    return {
        "response_type": "ephemeral",
        "text": f"Comando `{command}` recibido. Funcionalidad en desarrollo.",
    }


@app.post("/webhook/slack/interactions")
async def slack_interactions(request: Request):
    """Handle Slack interactive components (buttons, selects).
    
    Used for:
    - Approve/Reject campaign buttons in notifications
    - Quick actions on hot leads
    """
    import json
    
    form_data = await request.form()
    payload_str = form_data.get("payload", "{}")
    
    try:
        payload = json.loads(payload_str)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    
    action_id = payload.get("actions", [{}])[0].get("action_id", "")
    user = payload.get("user", {}).get("username", "unknown")
    
    logger.info("slack_interaction_received", action=action_id, user=user)
    
    # Handle approve/reject campaign actions
    if action_id.startswith("approve_campaign_"):
        campaign_id = action_id.replace("approve_campaign_", "")
        # TODO: Approve campaign
        return {
            "text": f"✅ Campaña {campaign_id[:8]}... aprobada por {user}",
        }
    
    elif action_id.startswith("reject_campaign_"):
        campaign_id = action_id.replace("reject_campaign_", "")
        # TODO: Reject campaign
        return {
            "text": f"❌ Campaña {campaign_id[:8]}... rechazada por {user}",
        }
    
    return {"text": "Acción procesada"}


# ==============================================================================
# HEALTH CHECK
# ==============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Alter-5 Origination Webhooks",
        "version": "1.0.0",
        "endpoints": {
            "/webhook/mailchimp": "Mailchimp email events",
            "/webhook/slack/commands": "Slack slash commands",
            "/webhook/slack/interactions": "Slack interactive components",
            "/health": "Health check",
        },
    }


# ==============================================================================
# STARTUP / SHUTDOWN
# ==============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup."""
    logger.info("webhook_server_starting")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown."""
    logger.info("webhook_server_shutting_down")
