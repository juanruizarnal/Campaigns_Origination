"""Agente Follow-up Manager for Alter-5 Origination Engine.

This module implements the FollowupManager agent (Agent 8) which manages
automatic follow-up sequences after campaigns are sent.

Features:
- Process Mailchimp webhook events (opens, clicks, replies)
- Schedule follow-up emails based on engagement
- Generate alerts for hot leads and responses
- Track follow-up state in Airtable

Usage:
    from agents.followup_manager import FollowupManager
    
    agent = FollowupManager()
    action = await agent.process_email_event(event)
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional
import uuid

import structlog

from config.settings import get_settings
from core.airtable_client import AirtableClient, AirtableError, get_airtable_client
from core.models import (
    FollowupAction,
    FollowupTask,
    MailchimpWebhookEvent,
    MailchimpEventType,
    AlertNotification,
)
from integrations.claude import ClaudeClient, get_claude_client
from integrations.slack import SlackClient, get_slack_client

logger = structlog.get_logger(__name__)


class FollowupManager:
    """Agent for managing automatic follow-up sequences.
    
    Processes email engagement events and decides on follow-up actions:
    - Opens without click -> Schedule follow-up after N days
    - Clicks -> Alert as hot lead
    - Replies -> Urgent alert to sales team
    - Bounces -> Mark as invalid
    
    Example:
        agent = FollowupManager()
        
        # Process a webhook event
        event = MailchimpWebhookEvent(
            event_type=MailchimpEventType.CLICK,
            email="cfo@company.com",
            campaign_id="abc123",
        )
        action = await agent.process_email_event(event)
    """
    
    def __init__(
        self,
        airtable_client: Optional[AirtableClient] = None,
        claude_client: Optional[ClaudeClient] = None,
        slack_client: Optional[SlackClient] = None,
    ):
        """Initialize the FollowupManager agent.
        
        Args:
            airtable_client: Optional custom Airtable client
            claude_client: Optional custom Claude client for generating follow-ups
            slack_client: Optional custom Slack client for alerts
        """
        self._airtable = airtable_client or get_airtable_client()
        self._claude = claude_client or get_claude_client()
        self._slack = slack_client or get_slack_client()
        
        settings = get_settings()
        self._followup_1_days = settings.FOLLOWUP_1_DAYS
        self._followup_2_days = settings.FOLLOWUP_2_DAYS
        self._max_followups = settings.MAX_FOLLOWUPS
        
        logger.info(
            "followup_manager_initialized",
            followup_1_days=self._followup_1_days,
            followup_2_days=self._followup_2_days,
            max_followups=self._max_followups,
        )
    
    async def process_email_event(
        self,
        event: MailchimpWebhookEvent,
    ) -> FollowupAction:
        """Process an email engagement event and decide action.
        
        Args:
            event: Mailchimp webhook event
            
        Returns:
            FollowupAction indicating what to do
        """
        task_id = str(uuid.uuid4())[:8]
        
        logger.info(
            "processing_email_event",
            task_id=task_id,
            event_type=event.event_type.value,
            email=event.email,
            campaign_id=event.campaign_id,
        )
        
        try:
            # Get target info from Airtable
            target = await self._get_target_by_email(event.campaign_id, event.email)
            
            if not target:
                logger.warning(
                    "target_not_found",
                    task_id=task_id,
                    email=event.email,
                    campaign_id=event.campaign_id,
                )
                return FollowupAction.NONE
            
            # Determine action based on event type
            if event.event_type == MailchimpEventType.CLICK:
                return await self._handle_click(task_id, event, target)
            
            elif event.event_type == MailchimpEventType.OPEN:
                return await self._handle_open(task_id, event, target)
            
            elif event.event_type == MailchimpEventType.BOUNCE:
                return await self._handle_bounce(task_id, event, target)
            
            elif event.event_type == MailchimpEventType.UNSUBSCRIBE:
                return await self._handle_unsubscribe(task_id, event, target)
            
            return FollowupAction.NONE
            
        except Exception as e:
            logger.error(
                "event_processing_failed",
                task_id=task_id,
                error=str(e),
            )
            return FollowupAction.NONE
    
    async def _handle_click(
        self,
        task_id: str,
        event: MailchimpWebhookEvent,
        target: dict,
    ) -> FollowupAction:
        """Handle click event - hot lead!
        
        Args:
            task_id: Task ID for logging
            event: The webhook event
            target: Target record from Airtable
            
        Returns:
            FollowupAction
        """
        logger.info("hot_lead_detected", task_id=task_id, email=event.email)
        
        # Update target status in Airtable
        try:
            self._airtable.update_record(
                "campaign_targets",
                target["id"],
                {
                    "Status": "Clicked",
                    "Last_Interaction_Date": event.timestamp.isoformat(),
                    "Follow_Up_Notes": f"Click detected at {event.timestamp}",
                },
            )
        except AirtableError as e:
            logger.warning("failed_to_update_target", error=str(e))
        
        # Send Slack alert
        await self._slack.send_hot_lead_alert(
            contact_name=target.get("contact_name", "Unknown"),
            company_name=target.get("company_name", "Unknown"),
            campaign_name=target.get("campaign_name", "Unknown"),
            action="click",
            email=event.email,
            target_id=target["id"],
        )
        
        return FollowupAction.ALERT_HOT_LEAD
    
    async def _handle_open(
        self,
        task_id: str,
        event: MailchimpWebhookEvent,
        target: dict,
    ) -> FollowupAction:
        """Handle open event - schedule follow-up if not yet done.
        
        Args:
            task_id: Task ID for logging
            event: The webhook event
            target: Target record from Airtable
            
        Returns:
            FollowupAction
        """
        followup_count = target.get("followup_count", 0)
        
        if followup_count >= self._max_followups:
            logger.info(
                "max_followups_reached",
                task_id=task_id,
                email=event.email,
                count=followup_count,
            )
            return FollowupAction.NONE
        
        # Calculate follow-up schedule
        days = self._followup_1_days if followup_count == 0 else self._followup_2_days
        scheduled_for = event.timestamp + timedelta(days=days)
        
        # Create follow-up task
        followup_task = FollowupTask(
            target_id=target["id"],
            campaign_id=event.campaign_id,
            email=event.email,
            followup_number=followup_count + 1,
            scheduled_for=scheduled_for,
            template=f"followup_{followup_count + 1}",
        )
        
        # Save follow-up task to Airtable
        try:
            await self._save_followup_task(followup_task)
            
            logger.info(
                "followup_scheduled",
                task_id=task_id,
                email=event.email,
                followup_number=followup_task.followup_number,
                scheduled_for=scheduled_for.isoformat(),
            )
        except Exception as e:
            logger.error("failed_to_schedule_followup", error=str(e))
        
        return FollowupAction.SCHEDULE_FOLLOWUP
    
    async def _handle_bounce(
        self,
        task_id: str,
        event: MailchimpWebhookEvent,
        target: dict,
    ) -> FollowupAction:
        """Handle bounce - mark contact as invalid.
        
        Args:
            task_id: Task ID for logging
            event: The webhook event
            target: Target record from Airtable
            
        Returns:
            FollowupAction
        """
        logger.warning("email_bounced", task_id=task_id, email=event.email)
        
        try:
            self._airtable.update_record(
                "campaign_targets",
                target["id"],
                {
                    "Status": "Bounced",
                    "Follow_Up_Notes": f"Email bounced at {event.timestamp}",
                },
            )
        except AirtableError as e:
            logger.warning("failed_to_update_target", error=str(e))
        
        return FollowupAction.MARK_COLD
    
    async def _handle_unsubscribe(
        self,
        task_id: str,
        event: MailchimpWebhookEvent,
        target: dict,
    ) -> FollowupAction:
        """Handle unsubscribe - mark and don't contact again.
        
        Args:
            task_id: Task ID for logging
            event: The webhook event
            target: Target record from Airtable
            
        Returns:
            FollowupAction
        """
        logger.info("contact_unsubscribed", task_id=task_id, email=event.email)
        
        try:
            self._airtable.update_record(
                "campaign_targets",
                target["id"],
                {
                    "Status": "Unsubscribed",
                    "Follow_Up_Notes": f"Unsubscribed at {event.timestamp}",
                },
            )
        except AirtableError as e:
            logger.warning("failed_to_update_target", error=str(e))
        
        return FollowupAction.MARK_COLD
    
    async def process_response(
        self,
        email: str,
        campaign_id: str,
        response_preview: Optional[str] = None,
    ) -> FollowupAction:
        """Process an email response (reply).
        
        This is triggered when a reply is detected (via email parsing).
        
        Args:
            email: Email address that replied
            campaign_id: Campaign ID
            response_preview: Preview of the response
            
        Returns:
            FollowupAction
        """
        task_id = str(uuid.uuid4())[:8]
        logger.info("response_received", task_id=task_id, email=email)
        
        target = await self._get_target_by_email(campaign_id, email)
        
        if not target:
            logger.warning("target_not_found_for_response", email=email)
            return FollowupAction.NONE
        
        # Update target status
        try:
            self._airtable.update_record(
                "campaign_targets",
                target["id"],
                {
                    "Status": "Replied",
                    "Last_Interaction_Date": datetime.now().isoformat(),
                    "Response_Summary": response_preview[:500] if response_preview else "Response received",
                },
            )
        except AirtableError as e:
            logger.warning("failed_to_update_target", error=str(e))
        
        # Send urgent alert
        await self._slack.send_response_alert(
            contact_name=target.get("contact_name", "Unknown"),
            company_name=target.get("company_name", "Unknown"),
            campaign_name=target.get("campaign_name", "Unknown"),
            email=email,
            response_preview=response_preview,
        )
        
        return FollowupAction.ALERT_RESPONSE
    
    async def generate_followup_email(
        self,
        target_id: str,
        template: str = "followup_1",
    ) -> tuple[str, str]:
        """Generate a follow-up email for a target.
        
        Args:
            target_id: Campaign target ID
            template: Which follow-up template to use
            
        Returns:
            Tuple of (subject, body)
        """
        # Get target and original email context
        try:
            target_record = self._airtable.get_record("campaign_targets", target_id)
            fields = target_record.get("fields", {})
            
            contact_name = fields.get("Contact_Name", "")
            company_name = fields.get("Company_Name", "")
            original_subject = fields.get("Personalized_Email_Subject", "")
            days_since = fields.get("Days_Since_Sent", 3)
            
        except AirtableError as e:
            logger.error("failed_to_get_target", error=str(e))
            return "", ""
        
        # Generate follow-up with Claude
        if template == "followup_1":
            prompt = f"""
Genera un email de follow-up corto y amigable para:
- Contacto: {contact_name}
- Empresa: {company_name}
- Asunto original: {original_subject}
- Días desde el envío: {days_since}

El email debe:
1. Ser breve (máximo 80 palabras)
2. Mencionar el email anterior sin ser agresivo
3. Añadir valor (no solo preguntar si recibió el email)
4. Incluir un CTA claro
5. Tono profesional pero cercano

Devuelve un JSON:
{{
    "subject": "Re: ...",
    "body": "Hola [nombre],\\n\\n..."
}}
"""
        else:  # followup_2
            prompt = f"""
Genera un ÚLTIMO email de follow-up para:
- Contacto: {contact_name}
- Empresa: {company_name}
- Asunto original: {original_subject}

Este es el último intento, así que:
1. Muy breve (máximo 60 palabras)
2. Crear urgencia sin ser pesado
3. Ofrecer alternativa (ej: "si prefieres, contacta cuando te venga bien")
4. Tono de cierre amable

Devuelve un JSON:
{{
    "subject": "Re: ...",
    "body": "Hola [nombre],\\n\\n..."
}}
"""
        
        try:
            result = self._claude.generate_structured(prompt)
            return result.get("subject", ""), result.get("body", "")
        except Exception as e:
            logger.error("failed_to_generate_followup", error=str(e))
            return "", ""
    
    async def execute_scheduled_followups(self) -> int:
        """Execute all scheduled follow-ups that are due.
        
        Returns:
            Number of follow-ups executed
        """
        logger.info("executing_scheduled_followups")
        
        # Query follow-up queue from Airtable
        try:
            formula = "AND({Executed}=FALSE(), {Scheduled_For}<=NOW())"
            records = self._airtable.query_records(
                table_name="followup_queue",
                formula=formula,
                max_records=50,
            )
        except AirtableError as e:
            logger.error("failed_to_query_followups", error=str(e))
            return 0
        
        executed = 0
        for record in records:
            fields = record.get("fields", {})
            target_id = fields.get("Target_ID")
            template = fields.get("Template", "followup_1")
            
            if target_id:
                # Generate and send follow-up
                subject, body = await self.generate_followup_email(target_id, template)
                
                if subject and body:
                    # TODO: Actually send via Mailchimp
                    logger.info(
                        "followup_generated",
                        target_id=target_id,
                        template=template,
                    )
                    
                    # Mark as executed
                    try:
                        self._airtable.update_record(
                            "followup_queue",
                            record["id"],
                            {
                                "Executed": True,
                                "Executed_At": datetime.now().isoformat(),
                            },
                        )
                        executed += 1
                    except AirtableError as e:
                        logger.warning("failed_to_mark_executed", error=str(e))
        
        logger.info("followups_executed", count=executed)
        return executed
    
    async def _get_target_by_email(
        self,
        campaign_id: str,
        email: str,
    ) -> Optional[dict]:
        """Get campaign target by email and campaign.
        
        Args:
            campaign_id: Campaign ID (Mailchimp or Airtable)
            email: Contact email
            
        Returns:
            Target record dict or None
        """
        try:
            formula = f"AND({{Contact_Email}}='{email}')"
            records = self._airtable.query_records(
                table_name="campaign_targets",
                formula=formula,
                max_records=1,
            )
            
            if records:
                record = records[0]
                fields = record.get("fields", {})
                return {
                    "id": record["id"],
                    "contact_name": fields.get("Contact_Name"),
                    "company_name": fields.get("Company_Name"),
                    "campaign_name": fields.get("Campaign_Name"),
                    "followup_count": fields.get("Followup_Count", 0),
                }
            
            return None
            
        except AirtableError as e:
            logger.warning("failed_to_get_target", error=str(e))
            return None
    
    async def _save_followup_task(self, task: FollowupTask) -> None:
        """Save follow-up task to Airtable queue.
        
        Args:
            task: Follow-up task to save
        """
        try:
            self._airtable.create_record(
                "followup_queue",
                {
                    "Target_ID": task.target_id,
                    "Campaign_ID": task.campaign_id,
                    "Email": task.email,
                    "Followup_Number": task.followup_number,
                    "Scheduled_For": task.scheduled_for.isoformat(),
                    "Template": task.template,
                    "Created_At": task.created_at.isoformat(),
                    "Executed": False,
                },
            )
        except AirtableError as e:
            logger.error("failed_to_save_followup_task", error=str(e))
            raise


# ==============================================================================
# FACTORY FUNCTIONS
# ==============================================================================

_agent: Optional[FollowupManager] = None


def get_followup_manager() -> FollowupManager:
    """Get shared FollowupManager instance."""
    global _agent
    if _agent is None:
        _agent = FollowupManager()
    return _agent


async def process_mailchimp_event(event: MailchimpWebhookEvent) -> FollowupAction:
    """Convenience function to process Mailchimp event."""
    agent = get_followup_manager()
    return await agent.process_email_event(event)
