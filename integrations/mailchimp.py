"""Mailchimp integration for Alter-5 Origination Engine.

This module implements the Mailchimp client for sending campaigns
and tracking engagement metrics (opens, clicks, bounces).

Usage:
    from integrations.mailchimp import MailchimpClient, get_mailchimp_client
    
    client = get_mailchimp_client()
    campaign = client.create_campaign(
        name="FEI Q1 2026",
        subject="Financing opportunity for your green projects",
        from_email="sales@alter5.com",
        from_name="Alter-5 Team",
    )
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Any, Optional
from enum import Enum
import hashlib
import uuid

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config.settings import get_settings
from config.airtable_schema import TABLES, CAMPAIGN_TARGET_FIELDS
from core.airtable_client import AirtableClient, AirtableError, get_airtable_client

logger = structlog.get_logger()
settings = get_settings()


# ==============================================================================
# CONSTANTS
# ==============================================================================

# Mailchimp API version
MAILCHIMP_API_VERSION = "3.0"

# Default timeout for API calls
API_TIMEOUT_SECONDS = 30

# Batch size for recipient operations
RECIPIENT_BATCH_SIZE = 500


# ==============================================================================
# ENUMS
# ==============================================================================

class CampaignStatus(str, Enum):
    """Mailchimp campaign status."""
    SAVE = "save"  # Draft
    PAUSED = "paused"
    SCHEDULE = "schedule"
    SENDING = "sending"
    SENT = "sent"


class RecipientStatus(str, Enum):
    """Recipient delivery status."""
    PENDING = "Pending"
    SENT = "Sent"
    DELIVERED = "Delivered"
    OPENED = "Opened"
    CLICKED = "Clicked"
    BOUNCED = "Bounced"
    UNSUBSCRIBED = "Unsubscribed"
    COMPLAINED = "Complained"


# ==============================================================================
# DATA CLASSES
# ==============================================================================

@dataclass
class MailchimpCampaign:
    """Represents a Mailchimp campaign."""
    id: str
    web_id: int
    name: str
    status: CampaignStatus
    subject: str
    from_email: str
    from_name: str
    created_at: datetime
    sent_at: Optional[datetime] = None
    recipients_count: int = 0
    open_rate: float = 0.0
    click_rate: float = 0.0
    bounce_rate: float = 0.0
    unsubscribe_rate: float = 0.0
    
    def __str__(self) -> str:
        return (
            f"Campaign '{self.name}' ({self.status.value}): "
            f"{self.recipients_count} recipients, "
            f"{self.open_rate:.1%} opens, {self.click_rate:.1%} clicks"
        )


@dataclass
class Recipient:
    """Represents an email recipient."""
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    target_id: Optional[str] = None  # Airtable Campaign_Target record ID
    merge_fields: dict[str, Any] = field(default_factory=dict)
    
    def get_email_hash(self) -> str:
        """Get MD5 hash of lowercase email for Mailchimp API."""
        return hashlib.md5(self.email.lower().encode()).hexdigest()


@dataclass
class CampaignStats:
    """Campaign statistics from Mailchimp."""
    campaign_id: str
    sent: int = 0
    delivered: int = 0
    opens: int = 0
    unique_opens: int = 0
    clicks: int = 0
    unique_clicks: int = 0
    bounces: int = 0
    soft_bounces: int = 0
    hard_bounces: int = 0
    unsubscribes: int = 0
    complaints: int = 0
    open_rate: float = 0.0
    click_rate: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def __str__(self) -> str:
        return (
            f"Stats for {self.campaign_id}: "
            f"sent={self.sent}, opens={self.unique_opens}, clicks={self.unique_clicks}, "
            f"bounces={self.bounces}, unsubscribes={self.unsubscribes}"
        )


@dataclass
class RecipientActivity:
    """Activity record for a recipient."""
    email: str
    target_id: Optional[str]
    action: str  # "open", "click", "bounce", "unsubscribe"
    timestamp: datetime
    url: Optional[str] = None  # For click events
    bounce_type: Optional[str] = None  # "soft" or "hard"


@dataclass
class SyncResult:
    """Result of syncing metrics to Airtable."""
    campaign_id: str
    targets_updated: int = 0
    opens_recorded: int = 0
    clicks_recorded: int = 0
    bounces_recorded: int = 0
    unsubscribes_recorded: int = 0
    errors: list[str] = field(default_factory=list)
    success: bool = False
    
    def __str__(self) -> str:
        status = "✅" if self.success else "❌"
        return (
            f"{status} Sync for {self.campaign_id}: "
            f"{self.targets_updated} targets, "
            f"{self.opens_recorded} opens, {self.clicks_recorded} clicks"
        )


# ==============================================================================
# EXCEPTIONS
# ==============================================================================

class MailchimpError(Exception):
    """Base exception for Mailchimp errors."""
    pass


class MailchimpAPIError(MailchimpError):
    """Mailchimp API returned an error."""
    def __init__(self, message: str, status_code: int = 0, detail: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail


class MailchimpConfigError(MailchimpError):
    """Mailchimp configuration error."""
    pass


# ==============================================================================
# MAILCHIMP CLIENT
# ==============================================================================

class MailchimpClient:
    """Client for Mailchimp API.
    
    Provides methods to:
    - Create and manage email campaigns
    - Add/manage recipients via audiences
    - Send campaigns
    - Retrieve campaign statistics
    - Sync metrics back to Airtable
    
    Example:
        client = MailchimpClient(api_key="xxx-us1", list_id="abc123")
        
        # Create campaign
        campaign = client.create_campaign(
            name="Q1 Outreach",
            subject="Green Financing for Your Business",
            from_email="team@alter5.com",
            from_name="Alter-5",
        )
        
        # Add recipients
        client.add_recipients(campaign.id, recipients=[
            Recipient(email="ceo@company.com", first_name="John"),
        ])
        
        # Send
        client.send_campaign(campaign.id)
        
        # Get stats
        stats = client.get_campaign_stats(campaign.id)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        list_id: Optional[str] = None,
        airtable_client: Optional[AirtableClient] = None,
    ):
        """Initialize Mailchimp client.
        
        Args:
            api_key: Mailchimp API key (format: xxx-dc)
            list_id: Default audience/list ID
            airtable_client: Optional Airtable client for syncing
        """
        self._api_key = api_key or settings.mailchimp_api_key
        self._list_id = list_id or settings.mailchimp_list_id
        self._airtable = airtable_client or get_airtable_client()
        
        # Extract data center from API key
        if self._api_key and "-" in self._api_key:
            self._dc = self._api_key.split("-")[-1]
        else:
            self._dc = "us1"  # Default
        
        self._base_url = f"https://{self._dc}.api.mailchimp.com/{MAILCHIMP_API_VERSION}"
        
        logger.info(
            "mailchimp_client_initialized",
            data_center=self._dc,
            has_api_key=bool(self._api_key),
        )
    
    def _get_headers(self) -> dict[str, str]:
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.TimeoutException),
    )
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict:
        """Make API request to Mailchimp.
        
        Args:
            method: HTTP method
            endpoint: API endpoint (without base URL)
            data: Request body
            params: Query parameters
            
        Returns:
            Response data as dict
        """
        url = f"{self._base_url}/{endpoint.lstrip('/')}"
        
        logger.debug(
            "mailchimp_request",
            method=method,
            endpoint=endpoint,
        )
        
        try:
            with httpx.Client(timeout=API_TIMEOUT_SECONDS) as client:
                response = client.request(
                    method=method,
                    url=url,
                    headers=self._get_headers(),
                    json=data,
                    params=params,
                )
                
                if response.status_code >= 400:
                    error_data = response.json() if response.content else {}
                    raise MailchimpAPIError(
                        message=error_data.get("title", "API Error"),
                        status_code=response.status_code,
                        detail=error_data.get("detail", ""),
                    )
                
                return response.json() if response.content else {}
                
        except httpx.TimeoutException as e:
            logger.error("mailchimp_timeout", endpoint=endpoint)
            raise
        except MailchimpAPIError:
            raise
        except Exception as e:
            logger.error("mailchimp_request_error", error=str(e))
            raise MailchimpError(f"Request failed: {e}")
    
    # =========================================================================
    # CAMPAIGN MANAGEMENT
    # =========================================================================
    
    def create_campaign(
        self,
        name: str,
        subject: str,
        from_email: str,
        from_name: str,
        preview_text: str = "",
        list_id: Optional[str] = None,
        template_id: Optional[int] = None,
        html_content: Optional[str] = None,
    ) -> MailchimpCampaign:
        """Create a new email campaign.
        
        Args:
            name: Campaign name (internal)
            subject: Email subject line
            from_email: Sender email address
            from_name: Sender name
            preview_text: Email preview text
            list_id: Audience ID (uses default if not specified)
            template_id: Mailchimp template ID
            html_content: Custom HTML content
            
        Returns:
            Created MailchimpCampaign
        """
        logger.info("creating_mailchimp_campaign", name=name, subject=subject)
        
        campaign_data = {
            "type": "regular",
            "recipients": {
                "list_id": list_id or self._list_id,
            },
            "settings": {
                "subject_line": subject,
                "preview_text": preview_text,
                "title": name,
                "from_name": from_name,
                "reply_to": from_email,
            },
        }
        
        response = self._request("POST", "/campaigns", data=campaign_data)
        
        campaign = MailchimpCampaign(
            id=response["id"],
            web_id=response.get("web_id", 0),
            name=name,
            status=CampaignStatus(response.get("status", "save")),
            subject=subject,
            from_email=from_email,
            from_name=from_name,
            created_at=datetime.fromisoformat(
                response["create_time"].replace("Z", "+00:00")
            ),
        )
        
        # Set content if provided
        if html_content:
            self.set_campaign_content(campaign.id, html_content)
        elif template_id:
            self.set_campaign_template(campaign.id, template_id)
        
        logger.info(
            "mailchimp_campaign_created",
            campaign_id=campaign.id,
            name=name,
        )
        
        return campaign
    
    def set_campaign_content(
        self,
        campaign_id: str,
        html: str,
        plain_text: Optional[str] = None,
    ) -> None:
        """Set campaign email content.
        
        Args:
            campaign_id: Campaign ID
            html: HTML content
            plain_text: Plain text version (optional)
        """
        content_data = {"html": html}
        if plain_text:
            content_data["plain_text"] = plain_text
        
        self._request(
            "PUT",
            f"/campaigns/{campaign_id}/content",
            data=content_data,
        )
        
        logger.debug("campaign_content_set", campaign_id=campaign_id)
    
    def set_campaign_template(
        self,
        campaign_id: str,
        template_id: int,
    ) -> None:
        """Set campaign to use a template.
        
        Args:
            campaign_id: Campaign ID
            template_id: Mailchimp template ID
        """
        self._request(
            "PUT",
            f"/campaigns/{campaign_id}/content",
            data={"template": {"id": template_id}},
        )
        
        logger.debug("campaign_template_set", campaign_id=campaign_id)
    
    def get_campaign(self, campaign_id: str) -> MailchimpCampaign:
        """Get campaign details.
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            MailchimpCampaign
        """
        response = self._request("GET", f"/campaigns/{campaign_id}")
        
        return MailchimpCampaign(
            id=response["id"],
            web_id=response.get("web_id", 0),
            name=response["settings"]["title"],
            status=CampaignStatus(response["status"]),
            subject=response["settings"]["subject_line"],
            from_email=response["settings"]["reply_to"],
            from_name=response["settings"]["from_name"],
            created_at=datetime.fromisoformat(
                response["create_time"].replace("Z", "+00:00")
            ),
            sent_at=datetime.fromisoformat(
                response["send_time"].replace("Z", "+00:00")
            ) if response.get("send_time") else None,
            recipients_count=response.get("recipients", {}).get("recipient_count", 0),
        )
    
    def send_campaign(self, campaign_id: str) -> bool:
        """Send a campaign immediately.
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            True if sent successfully
        """
        logger.info("sending_mailchimp_campaign", campaign_id=campaign_id)
        
        try:
            self._request("POST", f"/campaigns/{campaign_id}/actions/send")
            
            logger.info("mailchimp_campaign_sent", campaign_id=campaign_id)
            return True
            
        except MailchimpAPIError as e:
            logger.error(
                "mailchimp_send_failed",
                campaign_id=campaign_id,
                error=str(e),
            )
            raise
    
    def schedule_campaign(
        self,
        campaign_id: str,
        send_time: datetime,
    ) -> bool:
        """Schedule a campaign for later.
        
        Args:
            campaign_id: Campaign ID
            send_time: When to send (UTC)
            
        Returns:
            True if scheduled successfully
        """
        self._request(
            "POST",
            f"/campaigns/{campaign_id}/actions/schedule",
            data={"schedule_time": send_time.isoformat()},
        )
        
        logger.info(
            "mailchimp_campaign_scheduled",
            campaign_id=campaign_id,
            send_time=send_time.isoformat(),
        )
        return True
    
    # =========================================================================
    # RECIPIENT MANAGEMENT
    # =========================================================================
    
    def add_recipients(
        self,
        recipients: list[Recipient],
        list_id: Optional[str] = None,
        update_existing: bool = True,
    ) -> int:
        """Add recipients to an audience list.
        
        Args:
            recipients: List of recipients to add
            list_id: Audience ID (uses default if not specified)
            update_existing: Update if email already exists
            
        Returns:
            Number of recipients added/updated
        """
        list_id = list_id or self._list_id
        added_count = 0
        
        logger.info(
            "adding_mailchimp_recipients",
            count=len(recipients),
            list_id=list_id,
        )
        
        # Process in batches
        for i in range(0, len(recipients), RECIPIENT_BATCH_SIZE):
            batch = recipients[i:i + RECIPIENT_BATCH_SIZE]
            
            members = []
            for recipient in batch:
                member_data = {
                    "email_address": recipient.email,
                    "status": "subscribed",
                    "merge_fields": {
                        "FNAME": recipient.first_name or "",
                        "LNAME": recipient.last_name or "",
                        "COMPANY": recipient.company or "",
                        **recipient.merge_fields,
                    },
                }
                members.append(member_data)
            
            response = self._request(
                "POST",
                f"/lists/{list_id}",
                data={
                    "members": members,
                    "update_existing": update_existing,
                },
            )
            
            added_count += response.get("total_created", 0)
            added_count += response.get("total_updated", 0)
        
        logger.info(
            "mailchimp_recipients_added",
            added=added_count,
            list_id=list_id,
        )
        
        return added_count
    
    def get_list_member(
        self,
        email: str,
        list_id: Optional[str] = None,
    ) -> Optional[dict]:
        """Get a member's info from a list.
        
        Args:
            email: Member email
            list_id: Audience ID
            
        Returns:
            Member data or None if not found
        """
        list_id = list_id or self._list_id
        email_hash = hashlib.md5(email.lower().encode()).hexdigest()
        
        try:
            return self._request("GET", f"/lists/{list_id}/members/{email_hash}")
        except MailchimpAPIError as e:
            if e.status_code == 404:
                return None
            raise
    
    # =========================================================================
    # STATISTICS & REPORTING
    # =========================================================================
    
    def get_campaign_stats(self, campaign_id: str) -> CampaignStats:
        """Get campaign statistics.
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            CampaignStats with engagement data
        """
        response = self._request("GET", f"/reports/{campaign_id}")
        
        stats = CampaignStats(
            campaign_id=campaign_id,
            sent=response.get("emails_sent", 0),
            opens=response.get("opens", {}).get("opens_total", 0),
            unique_opens=response.get("opens", {}).get("unique_opens", 0),
            clicks=response.get("clicks", {}).get("clicks_total", 0),
            unique_clicks=response.get("clicks", {}).get("unique_clicks", 0),
            bounces=response.get("bounces", {}).get("hard_bounces", 0) + 
                   response.get("bounces", {}).get("soft_bounces", 0),
            hard_bounces=response.get("bounces", {}).get("hard_bounces", 0),
            soft_bounces=response.get("bounces", {}).get("soft_bounces", 0),
            unsubscribes=response.get("unsubscribed", 0),
            complaints=response.get("abuse_reports", 0),
            open_rate=response.get("opens", {}).get("open_rate", 0),
            click_rate=response.get("clicks", {}).get("click_rate", 0),
        )
        
        # Calculate delivered
        stats.delivered = stats.sent - stats.bounces
        
        logger.debug("campaign_stats_retrieved", campaign_id=campaign_id, stats=str(stats))
        
        return stats
    
    def get_open_details(
        self,
        campaign_id: str,
        count: int = 100,
    ) -> list[RecipientActivity]:
        """Get list of recipients who opened the email.
        
        Args:
            campaign_id: Campaign ID
            count: Maximum results
            
        Returns:
            List of open activities
        """
        response = self._request(
            "GET",
            f"/reports/{campaign_id}/open-details",
            params={"count": count},
        )
        
        activities = []
        for member in response.get("members", []):
            activities.append(
                RecipientActivity(
                    email=member["email_address"],
                    target_id=None,  # Will be matched later
                    action="open",
                    timestamp=datetime.fromisoformat(
                        member["opens"][0]["timestamp"].replace("Z", "+00:00")
                    ) if member.get("opens") else datetime.now(),
                )
            )
        
        return activities
    
    def get_click_details(
        self,
        campaign_id: str,
        count: int = 100,
    ) -> list[RecipientActivity]:
        """Get list of recipients who clicked links.
        
        Args:
            campaign_id: Campaign ID
            count: Maximum results
            
        Returns:
            List of click activities
        """
        response = self._request(
            "GET",
            f"/reports/{campaign_id}/click-details",
            params={"count": count},
        )
        
        activities = []
        for url_record in response.get("urls_clicked", []):
            for member in url_record.get("members", []):
                activities.append(
                    RecipientActivity(
                        email=member["email_address"],
                        target_id=None,
                        action="click",
                        timestamp=datetime.fromisoformat(
                            member["clicks"][0]["timestamp"].replace("Z", "+00:00")
                        ) if member.get("clicks") else datetime.now(),
                        url=url_record.get("url"),
                    )
                )
        
        return activities
    
    def get_bounce_details(
        self,
        campaign_id: str,
        count: int = 100,
    ) -> list[RecipientActivity]:
        """Get list of bounced emails.
        
        Args:
            campaign_id: Campaign ID
            count: Maximum results
            
        Returns:
            List of bounce activities
        """
        # Hard bounces
        hard_response = self._request(
            "GET",
            f"/reports/{campaign_id}/abuse-reports",
            params={"count": count},
        )
        
        activities = []
        
        # Get unsubscribes
        unsub_response = self._request(
            "GET",
            f"/reports/{campaign_id}/unsubscribed",
            params={"count": count},
        )
        
        for member in unsub_response.get("unsubscribes", []):
            activities.append(
                RecipientActivity(
                    email=member["email_address"],
                    target_id=None,
                    action="unsubscribe",
                    timestamp=datetime.fromisoformat(
                        member["timestamp"].replace("Z", "+00:00")
                    ) if member.get("timestamp") else datetime.now(),
                )
            )
        
        return activities
    
    # =========================================================================
    # AIRTABLE SYNC
    # =========================================================================
    
    def sync_campaign_stats(
        self,
        mailchimp_campaign_id: str,
        airtable_campaign_id: str,
    ) -> SyncResult:
        """Sync Mailchimp stats to Airtable Campaign_Targets.
        
        Args:
            mailchimp_campaign_id: Mailchimp campaign ID
            airtable_campaign_id: Airtable Origination_Campaigns record ID
            
        Returns:
            SyncResult with details
        """
        logger.info(
            "syncing_campaign_stats",
            mailchimp_id=mailchimp_campaign_id,
            airtable_id=airtable_campaign_id,
        )
        
        result = SyncResult(campaign_id=mailchimp_campaign_id)
        
        try:
            # Get campaign stats
            stats = self.get_campaign_stats(mailchimp_campaign_id)
            
            # Get targets for this campaign from Airtable
            targets = self._airtable.query_records(
                table_name="campaign_targets",
                filter_formula=f"{{Campaign_ID}} = '{airtable_campaign_id}'",
            )
            
            # Build email to target mapping
            email_to_target: dict[str, str] = {}
            for target in targets:
                email = target.get("fields", {}).get("Contact_Email", "")
                if email:
                    email_to_target[email.lower()] = target["id"]
            
            # Get detailed activity
            opens = self.get_open_details(mailchimp_campaign_id)
            clicks = self.get_click_details(mailchimp_campaign_id)
            bounces = self.get_bounce_details(mailchimp_campaign_id)
            
            # Process opens
            for activity in opens:
                target_id = email_to_target.get(activity.email.lower())
                if target_id:
                    self._update_target_status(
                        target_id,
                        status=RecipientStatus.OPENED,
                        interaction_date=activity.timestamp,
                    )
                    result.opens_recorded += 1
                    result.targets_updated += 1
            
            # Process clicks (overrides opens)
            for activity in clicks:
                target_id = email_to_target.get(activity.email.lower())
                if target_id:
                    self._update_target_status(
                        target_id,
                        status=RecipientStatus.CLICKED,
                        interaction_date=activity.timestamp,
                    )
                    result.clicks_recorded += 1
            
            # Process bounces/unsubscribes
            for activity in bounces:
                target_id = email_to_target.get(activity.email.lower())
                if target_id:
                    status = (
                        RecipientStatus.UNSUBSCRIBED
                        if activity.action == "unsubscribe"
                        else RecipientStatus.BOUNCED
                    )
                    self._update_target_status(
                        target_id,
                        status=status,
                        interaction_date=activity.timestamp,
                    )
                    if activity.action == "unsubscribe":
                        result.unsubscribes_recorded += 1
                    else:
                        result.bounces_recorded += 1
            
            # Update campaign record with overall stats
            self._airtable.update_record(
                table_name="campaigns",
                record_id=airtable_campaign_id,
                fields={
                    "Emails_Sent": stats.sent,
                    "Open_Rate": stats.open_rate,
                    "Click_Rate": stats.click_rate,
                    "Bounce_Rate": stats.bounces / stats.sent if stats.sent > 0 else 0,
                    "Last_Sync_Date": datetime.now().isoformat(),
                },
            )
            
            result.success = True
            
            logger.info(
                "campaign_stats_synced",
                campaign_id=mailchimp_campaign_id,
                targets_updated=result.targets_updated,
            )
            
        except (MailchimpError, AirtableError) as e:
            result.errors.append(str(e))
            logger.error(
                "sync_failed",
                campaign_id=mailchimp_campaign_id,
                error=str(e),
            )
        
        return result
    
    def _update_target_status(
        self,
        target_id: str,
        status: RecipientStatus,
        interaction_date: datetime,
    ) -> None:
        """Update a Campaign_Target record status.
        
        Args:
            target_id: Airtable record ID
            status: New status
            interaction_date: When the interaction occurred
        """
        self._airtable.update_record(
            table_name="campaign_targets",
            record_id=target_id,
            fields={
                "Outreach_Status": status.value,
                "Last_Interaction_Date": interaction_date.isoformat(),
            },
        )


# ==============================================================================
# FACTORY FUNCTIONS
# ==============================================================================

_client: Optional[MailchimpClient] = None


def get_mailchimp_client() -> MailchimpClient:
    """Get shared MailchimpClient instance.
    
    Returns:
        Singleton MailchimpClient instance
    """
    global _client
    if _client is None:
        _client = MailchimpClient()
    return _client

