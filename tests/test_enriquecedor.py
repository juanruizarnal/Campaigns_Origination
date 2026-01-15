"""Tests for EnriquecedorDatos agent."""

import os
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
    }
    with patch.dict(os.environ, env_vars, clear=False):
        yield


@pytest.fixture
def mock_airtable():
    """Mock AirtableClient."""
    with patch("agents.enriquecedor.get_airtable_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_gemini():
    """Mock GeminiClient."""
    with patch("agents.enriquecedor.get_gemini_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


class TestCompanyInfo:
    """Tests for CompanyInfo dataclass."""
    
    def test_has_data_true(self) -> None:
        """Test has_data returns True when data exists."""
        from agents.enriquecedor import CompanyInfo
        
        info = CompanyInfo(num_employees=100)
        assert info.has_data() is True
        
        info = CompanyInfo(description="Test company")
        assert info.has_data() is True
    
    def test_has_data_false(self) -> None:
        """Test has_data returns False when no data."""
        from agents.enriquecedor import CompanyInfo
        
        info = CompanyInfo()
        assert info.has_data() is False


class TestFinancialInfo:
    """Tests for FinancialInfo dataclass."""
    
    def test_has_data_true(self) -> None:
        """Test has_data returns True when financial data exists."""
        from agents.enriquecedor import FinancialInfo
        
        info = FinancialInfo(annual_revenues=1000000)
        assert info.has_data() is True
        
        info = FinancialInfo(ebitda=500000)
        assert info.has_data() is True
    
    def test_has_data_false(self) -> None:
        """Test has_data returns False when no financial data."""
        from agents.enriquecedor import FinancialInfo
        
        info = FinancialInfo()
        assert info.has_data() is False


class TestEnriquecedorDatos:
    """Tests for EnriquecedorDatos agent."""
    
    def test_init(self, mock_airtable, mock_gemini) -> None:
        """Test EnriquecedorDatos initializes correctly."""
        from agents.enriquecedor import EnriquecedorDatos
        
        agent = EnriquecedorDatos()
        
        assert agent._airtable is not None
        assert agent._gemini is not None
        assert agent._system_prompt is not None
    
    def test_enrich_company_success(self, mock_airtable, mock_gemini) -> None:
        """Test successful company enrichment."""
        from agents.enriquecedor import EnriquecedorDatos
        
        # Setup mocks
        mock_airtable.get_record.return_value = {
            "id": "recTestCompany",
            "fields": {
                "Company Name": "Test Corp",
                "Home URL": "https://testcorp.com",
            }
        }
        
        mock_gemini.search_and_generate.return_value = {
            "response": '{"num_employees": 150, "description": "A test company"}'
        }
        mock_gemini.generate_json.return_value = {
            "num_employees": 150,
            "description": "A test company",
            "linkedin_url": None,
            "hq_address": "Madrid, Spain",
            "sector": "Technology",
        }
        
        agent = EnriquecedorDatos()
        result = agent.enrich_company("recTestCompany", dry_run=True)
        
        assert result.success is True
        assert result.company_id == "recTestCompany"
        assert result.company_info is not None
        assert result.company_info.num_employees == 150
    
    def test_enrich_company_no_company_name(self, mock_airtable, mock_gemini) -> None:
        """Test enrichment fails when company name is empty."""
        from agents.enriquecedor import EnriquecedorDatos
        
        mock_airtable.get_record.return_value = {
            "id": "recTestCompany",
            "fields": {}  # No company name
        }
        
        agent = EnriquecedorDatos()
        result = agent.enrich_company("recTestCompany")
        
        assert result.success is False
        assert "Company name is empty" in result.errors
    
    def test_search_company_info(self, mock_airtable, mock_gemini) -> None:
        """Test _search_company_info extracts data correctly."""
        from agents.enriquecedor import EnriquecedorDatos
        
        mock_gemini.search_and_generate.return_value = {
            "response": "Company info"
        }
        mock_gemini.generate_json.return_value = {
            "num_employees": 250,
            "linkedin_url": "https://linkedin.com/company/test",
            "description": "Technology company",
            "hq_address": "Barcelona, Spain",
            "sector": "Software",
            "founded_year": 2015,
        }
        
        agent = EnriquecedorDatos()
        result = agent._search_company_info("Test Corp", "https://test.com")
        
        assert result.num_employees == 250
        assert result.linkedin_url == "https://linkedin.com/company/test"
        assert result.description == "Technology company"
        assert result.hq_address == "Barcelona, Spain"
        assert result.sector == "Software"
    
    def test_extract_financials(self, mock_airtable, mock_gemini) -> None:
        """Test _extract_financials extracts financial data."""
        from agents.enriquecedor import EnriquecedorDatos
        
        mock_gemini.search_and_generate.return_value = {
            "response": "Financial info"
        }
        mock_gemini.generate_json.return_value = {
            "annual_revenues": 10000000,
            "ebitda": 2000000,
            "net_financial_debt": 5000000,
            "year": 2024,
            "currency": "EUR",
            "source": "Annual Report",
        }
        
        agent = EnriquecedorDatos()
        result = agent._extract_financials("Test Corp", "https://test.com")
        
        assert result.annual_revenues == 10000000
        assert result.ebitda == 2000000
        assert result.net_financial_debt == 5000000
        assert result.year == 2024
        assert result.currency == "EUR"
    
    def test_extract_financials_old_year(self, mock_airtable, mock_gemini) -> None:
        """Test _extract_financials rejects old financial data."""
        from agents.enriquecedor import EnriquecedorDatos
        
        mock_gemini.search_and_generate.return_value = {
            "response": "Financial info"
        }
        mock_gemini.generate_json.return_value = {
            "annual_revenues": 10000000,
            "year": 2018,  # Too old
            "currency": "EUR",
        }
        
        agent = EnriquecedorDatos()
        result = agent._extract_financials("Test Corp", "https://test.com")
        
        # Year should be None because it's too old
        assert result.year is None
    
    def test_identify_key_persons(self, mock_airtable, mock_gemini) -> None:
        """Test _identify_key_persons finds executives."""
        from agents.enriquecedor import EnriquecedorDatos
        
        mock_gemini.search_and_generate.return_value = {
            "response": "Key persons"
        }
        mock_gemini.generate_json.return_value = {
            "key_persons": [
                {
                    "first_name": "Juan",
                    "last_name": "García",
                    "role": "CEO",
                    "linkedin_url": "https://linkedin.com/in/jgarcia",
                    "email": "jgarcia@test.com",
                },
                {
                    "first_name": "María",
                    "last_name": "López",
                    "role": "CFO",
                    "email": "mlopez@test.com",
                },
            ]
        }
        
        agent = EnriquecedorDatos()
        result = agent._identify_key_persons("Test Corp", "https://test.com")
        
        assert len(result) == 2
        assert result[0].first_name == "Juan"
        assert result[0].last_name == "García"
        assert result[0].role == "CEO"
        assert result[0].is_key_person is True
        assert result[1].first_name == "María"
        assert result[1].role == "CFO"
    
    def test_identify_key_persons_max_5(self, mock_airtable, mock_gemini) -> None:
        """Test _identify_key_persons returns max 5 contacts."""
        from agents.enriquecedor import EnriquecedorDatos
        
        mock_gemini.search_and_generate.return_value = {
            "response": "Key persons"
        }
        mock_gemini.generate_json.return_value = {
            "key_persons": [
                {"first_name": f"Person{i}", "last_name": "Test", "role": "Executive"}
                for i in range(10)  # 10 people
            ]
        }
        
        agent = EnriquecedorDatos()
        result = agent._identify_key_persons("Test Corp", "https://test.com")
        
        assert len(result) == 5  # Should be limited to 5
    
    def test_save_results_updates_company(self, mock_airtable, mock_gemini) -> None:
        """Test _save_results updates company record."""
        from agents.enriquecedor import (
            EnriquecedorDatos,
            EnrichmentResult,
            CompanyInfo,
        )
        
        mock_airtable.update_record.return_value = {"id": "recTest"}
        
        agent = EnriquecedorDatos()
        result = EnrichmentResult(company_id="recTest", success=True)
        
        company_info = CompanyInfo(
            num_employees=100,
            description="Test company",
        )
        
        company_record = {
            "id": "recTest",
            "fields": {"Company Name": "Test Corp"}
        }
        
        agent._save_results(
            company_id="recTest",
            company_record=company_record,
            company_info=company_info,
            financial_info=None,
            key_persons=[],
            result=result,
        )
        
        mock_airtable.update_record.assert_called_once()
        call_args = mock_airtable.update_record.call_args
        assert call_args[0][0] == "companies"
        assert call_args[0][1] == "recTest"
        assert "Num Employees" in call_args[0][2]
    
    def test_save_results_creates_financials(self, mock_airtable, mock_gemini) -> None:
        """Test _save_results creates financial record."""
        from agents.enriquecedor import (
            EnriquecedorDatos,
            EnrichmentResult,
            FinancialInfo,
        )
        
        mock_airtable.create_record.return_value = {"id": "recFinancials"}
        
        agent = EnriquecedorDatos()
        result = EnrichmentResult(company_id="recTest", success=True)
        
        financial_info = FinancialInfo(
            annual_revenues=1000000,
            ebitda=200000,
            year=2024,
        )
        
        company_record = {
            "id": "recTest",
            "fields": {"Company Name": "Test Corp"}
        }
        
        agent._save_results(
            company_id="recTest",
            company_record=company_record,
            company_info=None,
            financial_info=financial_info,
            key_persons=[],
            result=result,
        )
        
        assert result.financials_created is True
        # Check create_record was called for financials
        create_calls = [
            c for c in mock_airtable.create_record.call_args_list
            if c[0][0] == "financials"
        ]
        assert len(create_calls) == 1


class TestEnrichmentResult:
    """Tests for EnrichmentResult."""
    
    def test_str_success(self) -> None:
        """Test string representation for successful result."""
        from agents.enriquecedor import EnrichmentResult, CompanyInfo
        
        result = EnrichmentResult(
            company_id="recTest",
            success=True,
            company_info=CompanyInfo(num_employees=100),
            contacts_created=2,
        )
        
        str_repr = str(result)
        assert "✅" in str_repr
        assert "recTest" in str_repr
    
    def test_str_failure(self) -> None:
        """Test string representation for failed result."""
        from agents.enriquecedor import EnrichmentResult
        
        result = EnrichmentResult(
            company_id="recTest",
            success=False,
            errors=["Some error"],
        )
        
        str_repr = str(result)
        assert "❌" in str_repr


class TestBatchEnrichment:
    """Tests for batch enrichment."""
    
    def test_enrich_batch(self, mock_airtable, mock_gemini) -> None:
        """Test enrich_batch processes multiple companies."""
        from agents.enriquecedor import EnriquecedorDatos
        
        mock_airtable.get_record.return_value = {
            "id": "recTest",
            "fields": {
                "Company Name": "Test Corp",
                "Home URL": "https://test.com",
            }
        }
        
        mock_gemini.search_and_generate.return_value = {"response": "{}"}
        mock_gemini.generate_json.return_value = {}
        
        agent = EnriquecedorDatos()
        
        results = agent.enrich_batch(
            company_ids=["rec1", "rec2", "rec3"],
            dry_run=True,
        )
        
        assert len(results) == 3
        assert all(r.success for r in results)
    
    def test_enrich_batch_with_progress(self, mock_airtable, mock_gemini) -> None:
        """Test enrich_batch calls progress callback."""
        from agents.enriquecedor import EnriquecedorDatos
        
        mock_airtable.get_record.return_value = {
            "id": "recTest",
            "fields": {
                "Company Name": "Test Corp",
            }
        }
        
        mock_gemini.search_and_generate.return_value = {"response": "{}"}
        mock_gemini.generate_json.return_value = {}
        
        agent = EnriquecedorDatos()
        
        progress_calls = []
        
        def on_progress(current, total, result):
            progress_calls.append((current, total))
        
        agent.enrich_batch(
            company_ids=["rec1", "rec2"],
            dry_run=True,
            on_progress=on_progress,
        )
        
        assert len(progress_calls) == 2
        assert progress_calls[0] == (1, 2)
        assert progress_calls[1] == (2, 2)


class TestFactoryFunction:
    """Tests for get_enriquecedor factory function."""
    
    def test_get_enriquecedor_singleton(self, mock_airtable, mock_gemini) -> None:
        """Test get_enriquecedor returns singleton."""
        # Reset singleton
        import agents.enriquecedor as module
        module._agent = None
        
        from agents.enriquecedor import get_enriquecedor
        
        agent1 = get_enriquecedor()
        agent2 = get_enriquecedor()
        
        assert agent1 is agent2

