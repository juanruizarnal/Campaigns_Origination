"""Tests for Airtable client wrapper."""

import os
from unittest.mock import MagicMock, patch

import pytest

from config.airtable_schema import TABLES
from core.airtable_client import AirtableClient, AirtableError, get_airtable_client


# Mock environment for all tests
@pytest.fixture(autouse=True)
def mock_env():
    """Set up mock environment variables for all tests."""
    env_vars = {
        "ANTHROPIC_API_KEY": "sk-ant-test-key-12345",
        "GOOGLE_API_KEY": "AIzaTestKey12345",
        "AIRTABLE_PAT": "patTestToken12345",
        "AIRTABLE_BASE_ID": "appTestBase12345",
    }
    with patch.dict(os.environ, env_vars, clear=False):
        yield


@pytest.fixture
def reset_singleton():
    """Reset the singleton client before each test."""
    import core.airtable_client as module
    module._client = None
    # Clear settings cache
    from config.settings import get_settings
    get_settings.cache_clear()
    yield
    module._client = None


class TestAirtableClientInit:
    """Test AirtableClient initialization."""
    
    def test_init_with_defaults(self, reset_singleton) -> None:
        """Test client initializes with settings."""
        client = AirtableClient()
        assert client._base_id == "appTestBase12345"
        assert client._pat == "patTestToken12345"
    
    def test_init_with_custom_values(self, reset_singleton) -> None:
        """Test client accepts custom PAT and base ID."""
        client = AirtableClient(pat="patCustom123", base_id="appCustomBase123")
        assert client._base_id == "appCustomBase123"
        assert client._pat == "patCustom123"
    
    def test_tables_cache_initialized_empty(self, reset_singleton) -> None:
        """Test tables cache is empty on init."""
        client = AirtableClient()
        assert client._tables_cache == {}


class TestTableIdResolution:
    """Test table name to ID resolution."""
    
    def test_get_table_id_known_table(self, reset_singleton) -> None:
        """Test getting ID for known table name."""
        client = AirtableClient()
        table_id = client._get_table_id("companies")
        assert table_id == TABLES["companies"]
    
    def test_get_table_id_raw_id(self, reset_singleton) -> None:
        """Test passing raw table ID returns as-is."""
        client = AirtableClient()
        table_id = client._get_table_id("tblCustomTable123")
        assert table_id == "tblCustomTable123"
    
    def test_get_table_id_unknown_raises(self, reset_singleton) -> None:
        """Test unknown table name raises AirtableError."""
        client = AirtableClient()
        with pytest.raises(AirtableError) as exc_info:
            client._get_table_id("unknown_table")
        assert "Unknown table name" in str(exc_info.value)
    
    def test_get_table_caches_result(self, reset_singleton) -> None:
        """Test that get_table caches Table objects."""
        client = AirtableClient()
        
        with patch.object(client._api, 'table') as mock_table:
            mock_table.return_value = MagicMock()
            
            # First call should create table
            table1 = client.get_table("companies")
            assert mock_table.called
            
            # Second call should use cache
            mock_table.reset_mock()
            table2 = client.get_table("companies")
            assert not mock_table.called
            
            assert table1 is table2


class TestCRUDOperations:
    """Test CRUD operations with mocked Airtable API."""
    
    @pytest.fixture
    def mock_client(self, reset_singleton) -> AirtableClient:
        """Create client with mocked table."""
        client = AirtableClient()
        mock_table = MagicMock()
        client._tables_cache["companies"] = mock_table
        return client
    
    def test_get_record_success(self, mock_client: AirtableClient) -> None:
        """Test successful record retrieval."""
        expected = {
            "id": "recTest123",
            "createdTime": "2024-01-01T00:00:00.000Z",
            "fields": {"Company Name": "Test Corp"},
        }
        mock_client._tables_cache["companies"].get.return_value = expected
        
        result = mock_client.get_record("companies", "recTest123")
        
        assert result == expected
        mock_client._tables_cache["companies"].get.assert_called_once_with("recTest123")
    
    def test_get_record_failure(self, mock_client: AirtableClient) -> None:
        """Test record retrieval failure raises AirtableError."""
        mock_client._tables_cache["companies"].get.side_effect = Exception("Not found")
        
        with pytest.raises(AirtableError) as exc_info:
            mock_client.get_record("companies", "recNotFound")
        
        assert "Failed to get record" in str(exc_info.value)
    
    def test_create_record_success(self, mock_client: AirtableClient) -> None:
        """Test successful record creation."""
        fields = {"Company Name": "New Corp"}
        expected = {"id": "recNew123", "fields": fields}
        mock_client._tables_cache["companies"].create.return_value = expected
        
        result = mock_client.create_record("companies", fields)
        
        assert result == expected
        mock_client._tables_cache["companies"].create.assert_called_once_with(fields)
    
    def test_update_record_success(self, mock_client: AirtableClient) -> None:
        """Test successful record update."""
        fields = {"Company Name": "Updated Corp"}
        expected = {"id": "recTest123", "fields": fields}
        mock_client._tables_cache["companies"].update.return_value = expected
        
        result = mock_client.update_record("companies", "recTest123", fields)
        
        assert result == expected
        mock_client._tables_cache["companies"].update.assert_called_once_with(
            "recTest123", fields, typecast=False
        )
    
    def test_delete_record_success(self, mock_client: AirtableClient) -> None:
        """Test successful record deletion."""
        mock_client._tables_cache["companies"].delete.return_value = None
        
        result = mock_client.delete_record("companies", "recTest123")
        
        assert result is True
        mock_client._tables_cache["companies"].delete.assert_called_once_with("recTest123")


class TestQueryOperations:
    """Test query operations with mocked Airtable API."""
    
    @pytest.fixture
    def mock_client(self, reset_singleton) -> AirtableClient:
        """Create client with mocked table."""
        client = AirtableClient()
        mock_table = MagicMock()
        client._tables_cache["companies"] = mock_table
        return client
    
    def test_query_records_no_filter(self, mock_client: AirtableClient) -> None:
        """Test query without filter."""
        expected = [
            {"id": "rec1", "fields": {"Company Name": "Corp 1"}},
            {"id": "rec2", "fields": {"Company Name": "Corp 2"}},
        ]
        mock_client._tables_cache["companies"].all.return_value = expected
        
        result = mock_client.query_records("companies")
        
        assert result == expected
        mock_client._tables_cache["companies"].all.assert_called_once_with()
    
    def test_query_records_with_formula(self, mock_client: AirtableClient) -> None:
        """Test query with formula filter."""
        expected = [{"id": "rec1", "fields": {"FEI_Status": "Eligible"}}]
        mock_client._tables_cache["companies"].all.return_value = expected
        
        result = mock_client.query_records(
            "companies",
            formula="{FEI_Status}='Eligible'"
        )
        
        assert result == expected
        mock_client._tables_cache["companies"].all.assert_called_once_with(
            formula="{FEI_Status}='Eligible'"
        )
    
    def test_query_records_with_all_params(self, mock_client: AirtableClient) -> None:
        """Test query with all parameters."""
        mock_client._tables_cache["companies"].all.return_value = []
        
        mock_client.query_records(
            "companies",
            formula="{FEI_Status}='Eligible'",
            fields=["Company Name", "FEI_Status"],
            max_records=10,
            sort=["Company Name"],
            view="Main View",
        )
        
        mock_client._tables_cache["companies"].all.assert_called_once_with(
            formula="{FEI_Status}='Eligible'",
            fields=["Company Name", "FEI_Status"],
            max_records=10,
            sort=["Company Name"],
            view="Main View",
        )
    
    def test_query_by_field(self, mock_client: AirtableClient) -> None:
        """Test query_by_field helper."""
        expected = [{"id": "rec1", "fields": {"FEI_Status": "Unknown"}}]
        mock_client._tables_cache["companies"].all.return_value = expected
        
        result = mock_client.query_by_field("companies", "FEI_Status", "Unknown")
        
        assert result == expected
    
    def test_count_records(self, mock_client: AirtableClient) -> None:
        """Test count_records method."""
        mock_client._tables_cache["companies"].all.return_value = [
            {"id": "rec1"},
            {"id": "rec2"},
            {"id": "rec3"},
        ]
        
        count = mock_client.count_records("companies")
        
        assert count == 3


class TestBatchOperations:
    """Test batch operations with mocked Airtable API."""
    
    @pytest.fixture
    def mock_client(self, reset_singleton) -> AirtableClient:
        """Create client with mocked table."""
        client = AirtableClient()
        mock_table = MagicMock()
        client._tables_cache["companies"] = mock_table
        return client
    
    def test_batch_create(self, mock_client: AirtableClient) -> None:
        """Test batch record creation."""
        records = [
            {"Company Name": "Corp 1"},
            {"Company Name": "Corp 2"},
        ]
        expected = [
            {"id": "rec1", "fields": records[0]},
            {"id": "rec2", "fields": records[1]},
        ]
        mock_client._tables_cache["companies"].batch_create.return_value = expected
        
        result = mock_client.batch_create("companies", records)
        
        assert result == expected
        mock_client._tables_cache["companies"].batch_create.assert_called_once_with(
            records, typecast=False
        )
    
    def test_batch_update(self, mock_client: AirtableClient) -> None:
        """Test batch record update."""
        records = [
            {"id": "rec1", "fields": {"Company Name": "Updated 1"}},
            {"id": "rec2", "fields": {"Company Name": "Updated 2"}},
        ]
        mock_client._tables_cache["companies"].batch_update.return_value = records
        
        result = mock_client.batch_update("companies", records)
        
        assert result == records


class TestSingleton:
    """Test singleton pattern for client."""
    
    def test_get_airtable_client_returns_same_instance(self, reset_singleton) -> None:
        """Test that get_airtable_client returns singleton."""
        client1 = get_airtable_client()
        client2 = get_airtable_client()
        assert client1 is client2
    
    def test_get_airtable_client_creates_instance(self, reset_singleton) -> None:
        """Test that get_airtable_client creates instance if none exists."""
        import core.airtable_client as module
        assert module._client is None
        
        client = get_airtable_client()
        
        assert client is not None
        assert module._client is client


class TestRecordExists:
    """Test record existence check."""
    
    @pytest.fixture
    def mock_client(self, reset_singleton) -> AirtableClient:
        """Create client with mocked table."""
        client = AirtableClient()
        mock_table = MagicMock()
        client._tables_cache["companies"] = mock_table
        return client
    
    def test_record_exists_true(self, mock_client: AirtableClient) -> None:
        """Test record_exists returns True when record found."""
        mock_client._tables_cache["companies"].get.return_value = {"id": "recTest123"}
        
        result = mock_client.record_exists("companies", "recTest123")
        
        assert result is True
    
    def test_record_exists_false(self, mock_client: AirtableClient) -> None:
        """Test record_exists returns False when record not found."""
        mock_client._tables_cache["companies"].get.side_effect = Exception("Not found")
        
        result = mock_client.record_exists("companies", "recNotFound")
        
        assert result is False

