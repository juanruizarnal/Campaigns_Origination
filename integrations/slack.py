"""Slack integration for alerts and notifications.

This module provides Slack messaging capabilities for:
- Hot lead alerts (when someone clicks/replies)
- Campaign creation notifications
- Error alerts for technical issues
- System status updates
"""

import asyncio
from typing import Optional

import structlog

from config.settings import get_settings

logger = structlog.get_logger(__name__)


class SlackClient:
    """Client for sending Slack notifications.
    
    Features:
    - Different channels for different alert types
    - Priority-based formatting
    - Async message sending
    - Fallback to logging if Slack not configured
    """
    
    def __init__(
        self,
        bot_token: Optional[str] = None,
        channel_origination: Optional[str] = None,
        channel_tech: Optional[str] = None,
    ):
        """Initialize Slack client.
        
        Args:
            bot_token: Slack bot token (xoxb-...)
            channel_origination: Channel for origination alerts
            channel_tech: Channel for technical alerts
        """
        settings = get_settings()
        self._token = bot_token or settings.SLACK_BOT_TOKEN
        self._channel_origination = channel_origination or settings.SLACK_CHANNEL_ORIGINATION
        self._channel_tech = channel_tech or settings.SLACK_CHANNEL_TECH
        
        self._client = None
        if self._token:
            try:
                from slack_sdk.web.async_client import AsyncWebClient
                self._client = AsyncWebClient(token=self._token)
                logger.info("slack_client_initialized")
            except ImportError:
                logger.warning("slack_sdk_not_installed")
        else:
            logger.warning("slack_not_configured", message="No SLACK_BOT_TOKEN set")
    
    def is_configured(self) -> bool:
        """Check if Slack is properly configured."""
        return self._client is not None
    
    async def send_hot_lead_alert(
        self,
        contact_name: str,
        company_name: str,
        campaign_name: str,
        action: str,  # "click" or "open"
        email: str,
        target_id: Optional[str] = None,
    ) -> bool:
        """Send alert for hot lead activity.
        
        Args:
            contact_name: Name of the contact
            company_name: Name of the company
            campaign_name: Name of the campaign
            action: What the contact did (click, open)
            email: Contact email
            target_id: Campaign target ID for reference
            
        Returns:
            True if message sent successfully
        """
        emoji = "🔥" if action == "click" else "👀"
        priority = "high" if action == "click" else "medium"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} Hot Lead Alert",
                    "emoji": True,
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Contacto:*\n{contact_name}"},
                    {"type": "mrkdwn", "text": f"*Empresa:*\n{company_name}"},
                    {"type": "mrkdwn", "text": f"*Campaña:*\n{campaign_name}"},
                    {"type": "mrkdwn", "text": f"*Acción:*\n{action.upper()}"},
                ],
            },
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": f"Email: {email}"},
                ],
            },
        ]
        
        if target_id:
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Ver en Airtable"},
                        "url": f"https://airtable.com/appEgNSP0tOLJ9YJ9/tblXXX/{target_id}",
                    }
                ],
            })
        
        return await self._send_message(
            channel=self._channel_origination,
            text=f"{emoji} Hot Lead: {contact_name} de {company_name} hizo {action}",
            blocks=blocks,
            priority=priority,
        )
    
    async def send_response_alert(
        self,
        contact_name: str,
        company_name: str,
        campaign_name: str,
        email: str,
        response_preview: Optional[str] = None,
    ) -> bool:
        """Send urgent alert for email response.
        
        Args:
            contact_name: Name of the contact
            company_name: Name of the company
            campaign_name: Name of the campaign
            email: Contact email
            response_preview: Preview of the response (first 200 chars)
            
        Returns:
            True if message sent successfully
        """
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📧 ¡RESPUESTA RECIBIDA!",
                    "emoji": True,
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Contacto:*\n{contact_name}"},
                    {"type": "mrkdwn", "text": f"*Empresa:*\n{company_name}"},
                    {"type": "mrkdwn", "text": f"*Campaña:*\n{campaign_name}"},
                    {"type": "mrkdwn", "text": f"*Email:*\n{email}"},
                ],
            },
        ]
        
        if response_preview:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Preview:*\n>{response_preview[:200]}...",
                },
            })
        
        return await self._send_message(
            channel=self._channel_origination,
            text=f"📧 RESPUESTA de {contact_name} ({company_name})",
            blocks=blocks,
            priority="urgent",
        )
    
    async def send_campaign_created_alert(
        self,
        campaign_name: str,
        campaign_id: str,
        target_count: int,
        trigger: str,
        is_automatic: bool = False,
    ) -> bool:
        """Send notification when campaign is created.
        
        Args:
            campaign_name: Name of the campaign
            campaign_id: Airtable campaign ID
            target_count: Number of targets in campaign
            trigger: What triggered the campaign
            is_automatic: Whether campaign was auto-created
            
        Returns:
            True if message sent successfully
        """
        emoji = "🤖" if is_automatic else "🚀"
        title = "Campaña Automática Creada" if is_automatic else "Nueva Campaña Creada"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} {title}",
                    "emoji": True,
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Campaña:*\n{campaign_name}"},
                    {"type": "mrkdwn", "text": f"*Targets:*\n{target_count}"},
                ],
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Trigger:*\n{trigger[:500]}",
                },
            },
        ]
        
        if is_automatic:
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "✅ Aprobar"},
                        "style": "primary",
                        "action_id": f"approve_campaign_{campaign_id}",
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "❌ Rechazar"},
                        "style": "danger",
                        "action_id": f"reject_campaign_{campaign_id}",
                    },
                ],
            })
        
        return await self._send_message(
            channel=self._channel_origination,
            text=f"{emoji} {title}: {campaign_name} con {target_count} targets",
            blocks=blocks,
            priority="medium",
        )
    
    async def send_error_alert(
        self,
        error_type: str,
        error_message: str,
        component: str,
        stack_trace: Optional[str] = None,
    ) -> bool:
        """Send technical error alert.
        
        Args:
            error_type: Type of error
            error_message: Error message
            component: Component where error occurred
            stack_trace: Optional stack trace
            
        Returns:
            True if message sent successfully
        """
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🚨 Error en Sistema",
                    "emoji": True,
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Tipo:*\n{error_type}"},
                    {"type": "mrkdwn", "text": f"*Componente:*\n{component}"},
                ],
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Mensaje:*\n```{error_message[:500]}```",
                },
            },
        ]
        
        if stack_trace:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Stack Trace:*\n```{stack_trace[:1000]}```",
                },
            })
        
        return await self._send_message(
            channel=self._channel_tech,
            text=f"🚨 Error en {component}: {error_message[:100]}",
            blocks=blocks,
            priority="high",
        )
    
    async def send_trigger_detected_alert(
        self,
        trigger_title: str,
        source: str,
        relevance: float,
        recommended_action: str,
    ) -> bool:
        """Send alert when market trigger is detected.
        
        Args:
            trigger_title: Title of the trigger
            source: Source of the trigger (FT, Reuters, etc.)
            relevance: Relevance score (0-1)
            recommended_action: What action is recommended
            
        Returns:
            True if message sent successfully
        """
        relevance_emoji = "🟢" if relevance >= 0.8 else "🟡" if relevance >= 0.5 else "🔴"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📰 Trigger de Mercado Detectado",
                    "emoji": True,
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{trigger_title}*",
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Fuente:*\n{source}"},
                    {"type": "mrkdwn", "text": f"*Relevancia:*\n{relevance_emoji} {relevance*100:.0f}%"},
                ],
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Acción recomendada:*\n{recommended_action}",
                },
            },
        ]
        
        return await self._send_message(
            channel=self._channel_origination,
            text=f"📰 Trigger: {trigger_title} (relevancia: {relevance*100:.0f}%)",
            blocks=blocks,
            priority="medium" if relevance >= 0.7 else "low",
        )
    
    async def _send_message(
        self,
        channel: str,
        text: str,
        blocks: Optional[list] = None,
        priority: str = "medium",
    ) -> bool:
        """Send a message to Slack.
        
        Args:
            channel: Channel to send to
            text: Fallback text
            blocks: Block Kit blocks
            priority: Priority level (low, medium, high, urgent)
            
        Returns:
            True if message sent successfully
        """
        if not self._client:
            # Fallback to logging
            log_method = logger.warning if priority in ["high", "urgent"] else logger.info
            log_method(
                "slack_message_not_sent",
                channel=channel,
                text=text,
                priority=priority,
                reason="Slack not configured",
            )
            return False
        
        try:
            response = await self._client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks,
            )
            
            logger.info(
                "slack_message_sent",
                channel=channel,
                ts=response.get("ts"),
                priority=priority,
            )
            return True
            
        except Exception as e:
            logger.error(
                "slack_message_failed",
                channel=channel,
                error=str(e),
            )
            return False


# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

_client: Optional[SlackClient] = None


def get_slack_client() -> SlackClient:
    """Get shared Slack client instance."""
    global _client
    if _client is None:
        _client = SlackClient()
    return _client


async def send_hot_lead_alert(
    contact_name: str,
    company_name: str,
    campaign_name: str,
    action: str,
    email: str,
) -> bool:
    """Convenience function to send hot lead alert."""
    client = get_slack_client()
    return await client.send_hot_lead_alert(
        contact_name=contact_name,
        company_name=company_name,
        campaign_name=campaign_name,
        action=action,
        email=email,
    )


async def send_response_alert(
    contact_name: str,
    company_name: str,
    campaign_name: str,
    email: str,
    response_preview: Optional[str] = None,
) -> bool:
    """Convenience function to send response alert."""
    client = get_slack_client()
    return await client.send_response_alert(
        contact_name=contact_name,
        company_name=company_name,
        campaign_name=campaign_name,
        email=email,
        response_preview=response_preview,
    )


async def send_error_alert(
    error_type: str,
    error_message: str,
    component: str,
) -> bool:
    """Convenience function to send error alert."""
    client = get_slack_client()
    return await client.send_error_alert(
        error_type=error_type,
        error_message=error_message,
        component=component,
    )
