"""Tests for Mailchimp integration."""

import os
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest


# Mock environment for all tests
@pytest.fixture(autouse=True)
def mock_env():
    """Set up mock environment variables for all tests."""
    env_vars = {
        "ANTHROPIC_API_KEY": "sk-ant-test-key-12345",
        "GOOGLE_API_KEY": "AIzaTestKey12345",
        "AIRTABLE_PAT": "patTestToken12345",
        "AIRTABLE_BASE_ID": "appTestBase12345",
        "MAILCHIMP_API_KEY": "abc123-us1",
        "MAILCHIMP_LIST_ID": "list123",
    }
    with patch.dict(os.environ, env_vars, clear=False):
        yield


@pytest.fixture
def mock_airtable():
    """Mock AirtableClient."""
    with patch("integrations.mailchimp.get_airtable_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_httpx():
    """Mock httpx.Client for API calls."""
    with patch("integrations.mailchimp.httpx.Client") as mock:
        client = MagicMock()
        mock.return_value.__enter__ = MagicMock(return_value=client)
        mock.return_value.__exit__ = MagicMock(return_value=None)
        yield client


class TestRecipient:
    """Tests for Recipient dataclass."""
    
    def test_recipient_creation(self) -> None:
        """Test Recipient can be created."""
        from integrations.mailchimp import Recipient
        
        recipient = Recipient(
            email="ceo@company.com",
            first_name="John",
            last_name="Doe",
            company="Test Company",
        )
        
        assert recipient.email == "ceo@company.com"
        assert recipient.first_name == "John"
    
    def test_get_email_hash(self) -> None:
        """Test email hash generation."""
        from integrations.mailchimp import Recipient
        
        recipient = Recipient(email="Test@Example.Com")
        
        # MD5 of "test@example.com"
        expected_hash = "55502f40dc8b7c769880b10874abc9d0"
        assert recipient.get_email_hash() == expected_hash


class TestCampaignStats:
    """Tests for CampaignStats dataclass."""
    
    def test_stats_str(self) -> None:
        """Test CampaignStats string representation."""
        from integrations.mailchimp import CampaignStats
        
        stats = CampaignStats(
            campaign_id="camp123",
            sent=100,
            unique_opens=25,
            unique_clicks=10,
            bounces=5,
            unsubscribes=2,
        )
        
        result_str = str(stats)
        assert "camp123" in result_str
        assert "100" in result_str
        assert "25" in result_str


class TestMailchimpCampaign:
    """Tests for MailchimpCampaign dataclass."""
    
    def test_campaign_str(self) -> None:
        """Test MailchimpCampaign string representation."""
        from integrations.mailchimp import MailchimpCampaign, CampaignStatus
        
        campaign = MailchimpCampaign(
            id="camp123",
            web_id=12345,
            name="Q1 Outreach",
            status=CampaignStatus.SENT,
            subject="Hello",
            from_email="test@example.com",
            from_name="Test",
            created_at=datetime.now(),
            recipients_count=100,
            open_rate=0.25,
            click_rate=0.10,
        )
        
        result_str = str(campaign)
        assert "Q1 Outreach" in result_str
        assert "100 recipients" in result_str


class TestSyncResult:
    """Tests for SyncResult dataclass."""
    
    def test_sync_result_success(self) -> None:
        """Test SyncResult string for success."""
        from integrations.mailchimp import SyncResult
        
        result = SyncResult(
            campaign_id="camp123",
            success=True,
            targets_updated=50,
            opens_recorded=25,
            clicks_recorded=10,
        )
        
        result_str = str(result)
        assert "✅" in result_str
        assert "50 targets" in result_str
    
    def test_sync_result_failure(self) -> None:
        """Test SyncResult string for failure."""
        from integrations.mailchimp import SyncResult
        
        result = SyncResult(
            campaign_id="camp123",
            success=False,
            errors=["API error"],
        )
        
        result_str = str(result)
        assert "❌" in result_str


class TestMailchimpClient:
    """Tests for MailchimpClient."""
    
    def test_init(self, mock_airtable) -> None:
        """Test MailchimpClient initializes correctly."""
        from integrations.mailchimp import MailchimpClient
        
        client = MailchimpClient(api_key="abc123-us1", list_id="list123")
        
        assert client._dc == "us1"
        assert client._list_id == "list123"
    
    def test_init_extracts_datacenter(self, mock_airtable) -> None:
        """Test data center extraction from API key."""
        from integrations.mailchimp import MailchimpClient
        
        client = MailchimpClient(api_key="somekey-us19")
        assert client._dc == "us19"
        
        client2 = MailchimpClient(api_key="somekey-eu1")
        assert client2._dc == "eu1"
    
    def test_get_headers(self, mock_airtable) -> None:
        """Test headers generation."""
        from integrations.mailchimp import MailchimpClient
        
        client = MailchimpClient(api_key="testkey-us1")
        headers = client._get_headers()
        
        assert "Authorization" in headers
        assert "Bearer testkey-us1" in headers["Authorization"]


class TestCreateCampaign:
    """Tests for create_campaign method."""
    
    def test_create_campaign_success(self, mock_airtable, mock_httpx) -> None:
        """Test successful campaign creation."""
        from integrations.mailchimp import MailchimpClient, CampaignStatus
        
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{"id": "camp123"}'
        mock_response.json.return_value = {
            "id": "camp123",
            "web_id": 12345,
            "status": "save",
            "create_time": "2026-01-05T10:00:00Z",
        }
        mock_httpx.request.return_value = mock_response
        
        client = MailchimpClient(api_key="testkey-us1", list_id="list123")
        campaign = client.create_campaign(
            name="Test Campaign",
            subject="Test Subject",
            from_email="test@example.com",
            from_name="Test",
        )
        
        assert campaign.id == "camp123"
        assert campaign.status == CampaignStatus.SAVE


class TestGetCampaignStats:
    """Tests for get_campaign_stats method."""
    
    def test_get_stats_success(self, mock_airtable, mock_httpx) -> None:
        """Test successful stats retrieval."""
        from integrations.mailchimp import MailchimpClient
        
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{}'
        mock_response.json.return_value = {
            "emails_sent": 100,
            "opens": {"opens_total": 50, "unique_opens": 25, "open_rate": 0.25},
            "clicks": {"clicks_total": 20, "unique_clicks": 10, "click_rate": 0.10},
            "bounces": {"hard_bounces": 2, "soft_bounces": 3},
            "unsubscribed": 1,
            "abuse_reports": 0,
        }
        mock_httpx.request.return_value = mock_response
        
        client = MailchimpClient(api_key="testkey-us1")
        stats = client.get_campaign_stats("camp123")
        
        assert stats.sent == 100
        assert stats.unique_opens == 25
        assert stats.unique_clicks == 10
        assert stats.bounces == 5
        assert stats.delivered == 95


class TestSyncCampaignStats:
    """Tests for sync_campaign_stats method."""
    
    def test_sync_stats_success(self, mock_airtable, mock_httpx) -> None:
        """Test successful stats sync."""
        from integrations.mailchimp import MailchimpClient
        
        # Mock Mailchimp API responses
        def mock_request(method, url, **kwargs):
            response = MagicMock()
            response.status_code = 200
            response.content = b'{}'
            
            if "/reports/" in url and "/open-details" not in url and "/click-details" not in url:
                response.json.return_value = {
                    "emails_sent": 10,
                    "opens": {"opens_total": 5, "unique_opens": 5, "open_rate": 0.5},
                    "clicks": {"clicks_total": 2, "unique_clicks": 2, "click_rate": 0.2},
                    "bounces": {"hard_bounces": 0, "soft_bounces": 0},
                    "unsubscribed": 0,
                    "abuse_reports": 0,
                }
            elif "/open-details" in url:
                response.json.return_value = {"members": []}
            elif "/click-details" in url:
                response.json.return_value = {"urls_clicked": []}
            elif "/abuse-reports" in url:
                response.json.return_value = {"abuse_reports": []}
            elif "/unsubscribed" in url:
                response.json.return_value = {"unsubscribes": []}
            else:
                response.json.return_value = {}
            
            return response
        
        mock_httpx.request.side_effect = mock_request
        
        # Mock Airtable
        mock_airtable.query_records.return_value = []
        
        client = MailchimpClient(api_key="testkey-us1")
        result = client.sync_campaign_stats("camp123", "recCampaign001")
        
        assert result.success is True


class TestRecipientStatus:
    """Tests for RecipientStatus enum."""
    
    def test_status_values(self) -> None:
        """Test RecipientStatus values."""
        from integrations.mailchimp import RecipientStatus
        
        assert RecipientStatus.PENDING.value == "Pending"
        assert RecipientStatus.SENT.value == "Sent"
        assert RecipientStatus.DELIVERED.value == "Delivered"
        assert RecipientStatus.OPENED.value == "Opened"
        assert RecipientStatus.CLICKED.value == "Clicked"
        assert RecipientStatus.BOUNCED.value == "Bounced"
        assert RecipientStatus.UNSUBSCRIBED.value == "Unsubscribed"


class TestFactoryFunction:
    """Tests for get_mailchimp_client factory function."""
    
    def test_get_client_singleton(self, mock_airtable) -> None:
        """Test get_mailchimp_client returns singleton."""
        # Reset singleton
        import integrations.mailchimp as module
        module._client = None
        
        from integrations.mailchimp import get_mailchimp_client
        
        client1 = get_mailchimp_client()
        client2 = get_mailchimp_client()
        
        assert client1 is client2

