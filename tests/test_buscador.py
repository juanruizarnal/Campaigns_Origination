"""Tests for BuscadorEmpresas agent."""

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
    with patch("agents.buscador.get_airtable_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_gemini():
    """Mock GeminiClient."""
    with patch("agents.buscador.get_gemini_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


class TestSearchCriteria:
    """Tests for SearchCriteria dataclass."""
    
    def test_criteria_creation(self) -> None:
        """Test SearchCriteria can be created."""
        from agents.buscador import SearchCriteria
        
        criteria = SearchCriteria(
            sector="renovables",
            country="ES",
            region="Andalucía",
            min_employees=50,
            limit=25,
        )
        
        assert criteria.sector == "renovables"
        assert criteria.country == "ES"
        assert criteria.limit == 25
    
    def test_to_query(self) -> None:
        """Test SearchCriteria converts to query string."""
        from agents.buscador import SearchCriteria
        
        criteria = SearchCriteria(
            sector="energía solar",
            country="ES",
            region="Andalucía",
            min_employees=50,
        )
        
        query = criteria.to_query()
        
        assert "energía solar" in query
        assert "Andalucía" in query
        assert "ES" in query
        assert "50 empleados" in query
    
    def test_is_valid_with_sector(self) -> None:
        """Test is_valid returns True with sector."""
        from agents.buscador import SearchCriteria
        
        criteria = SearchCriteria(sector="renovables")
        assert criteria.is_valid() is True
    
    def test_is_valid_with_keywords(self) -> None:
        """Test is_valid returns True with keywords."""
        from agents.buscador import SearchCriteria
        
        criteria = SearchCriteria(keywords=["solar", "fotovoltaica"])
        assert criteria.is_valid() is True
    
    def test_is_valid_empty(self) -> None:
        """Test is_valid returns False without criteria."""
        from agents.buscador import SearchCriteria
        
        criteria = SearchCriteria()
        assert criteria.is_valid() is False


class TestCompanyCandidate:
    """Tests for CompanyCandidate dataclass."""
    
    def test_candidate_creation(self) -> None:
        """Test CompanyCandidate can be created."""
        from agents.buscador import CompanyCandidate
        
        candidate = CompanyCandidate(
            name="Solar Tech España",
            home_url="https://www.solartech.es",
            sector="Renewables",
            country="ES",
        )
        
        assert candidate.name == "Solar Tech España"
        assert candidate.url_verified is False
        assert candidate.is_duplicate is False
    
    def test_get_domain(self) -> None:
        """Test get_domain extracts domain correctly."""
        from agents.buscador import CompanyCandidate
        
        candidate = CompanyCandidate(
            name="Test",
            home_url="https://www.example.com/page",
        )
        
        assert candidate.get_domain() == "example.com"
    
    def test_get_domain_no_www(self) -> None:
        """Test get_domain works without www."""
        from agents.buscador import CompanyCandidate
        
        candidate = CompanyCandidate(
            name="Test",
            home_url="https://example.com",
        )
        
        assert candidate.get_domain() == "example.com"
    
    def test_get_domain_none(self) -> None:
        """Test get_domain returns None when no URL."""
        from agents.buscador import CompanyCandidate
        
        candidate = CompanyCandidate(name="Test")
        assert candidate.get_domain() is None


class TestSearchResult:
    """Tests for SearchResult dataclass."""
    
    def test_result_str_success(self) -> None:
        """Test SearchResult string for success."""
        from agents.buscador import SearchResult, SearchCriteria, CompanyCandidate
        
        result = SearchResult(
            criteria=SearchCriteria(sector="renovables"),
            success=True,
            candidates_found=[
                CompanyCandidate(name="Company 1"),
                CompanyCandidate(name="Company 2"),
            ],
            candidates_verified=2,
            candidates_created=2,
        )
        
        result_str = str(result)
        assert "✅" in result_str
        assert "2 candidates" in result_str
    
    def test_result_str_failure(self) -> None:
        """Test SearchResult string for failure."""
        from agents.buscador import SearchResult, SearchCriteria
        
        result = SearchResult(
            criteria=SearchCriteria(sector="test"),
            success=False,
            errors=["No companies found"],
        )
        
        result_str = str(result)
        assert "❌" in result_str
        assert "No companies found" in result_str
    
    def test_get_new_candidates(self) -> None:
        """Test get_new_candidates filters correctly."""
        from agents.buscador import SearchResult, SearchCriteria, CompanyCandidate
        
        result = SearchResult(
            criteria=SearchCriteria(sector="test"),
            candidates_found=[
                CompanyCandidate(name="Valid", url_verified=True, is_duplicate=False),
                CompanyCandidate(name="No URL", url_verified=False, is_duplicate=False),
                CompanyCandidate(name="Duplicate", url_verified=True, is_duplicate=True),
            ],
        )
        
        new = result.get_new_candidates()
        assert len(new) == 1
        assert new[0].name == "Valid"


class TestBuscadorEmpresas:
    """Tests for BuscadorEmpresas agent."""
    
    def test_init(self, mock_airtable, mock_gemini) -> None:
        """Test BuscadorEmpresas initializes correctly."""
        from agents.buscador import BuscadorEmpresas
        
        agent = BuscadorEmpresas()
        
        assert agent._airtable is not None
        assert agent._gemini is not None
        assert agent._system_prompt is not None
    
    def test_search_invalid_criteria(self, mock_airtable, mock_gemini) -> None:
        """Test search fails with invalid criteria."""
        from agents.buscador import BuscadorEmpresas
        
        agent = BuscadorEmpresas()
        result = agent.search()  # No criteria
        
        assert result.success is False
        assert "Invalid criteria" in result.errors[0]
    
    def test_search_success(self, mock_airtable, mock_gemini) -> None:
        """Test successful company search."""
        from agents.buscador import BuscadorEmpresas
        
        # Mock Gemini responses
        mock_gemini.search_and_generate.return_value = {
            "response": "Found companies"
        }
        mock_gemini.generate_json.return_value = {
            "companies": [
                {
                    "name": "SolarTech España",
                    "home_url": "https://www.solartech.es",
                    "description": "Empresa de energía solar",
                    "sector": "Renewables",
                    "country": "ES",
                    "region": "Andalucía",
                    "estimated_employees": 100,
                },
                {
                    "name": "EcoEnergía",
                    "home_url": "https://www.ecoenergia.es",
                    "description": "Empresa de energías renovables",
                    "sector": "Renewables",
                    "country": "ES",
                    "region": "Cataluña",
                    "estimated_employees": 50,
                },
            ]
        }
        
        # Mock deduplication query
        mock_airtable.query_records.return_value = []
        
        # Mock record creation
        mock_airtable.create_record.side_effect = [
            {"id": "recCo001"},
            {"id": "recBU001"},
            {"id": "recCo002"},
            {"id": "recBU002"},
        ]
        
        agent = BuscadorEmpresas()
        result = agent.search(
            sector="renovables",
            country="ES",
            limit=10,
            verify_urls=False,  # Skip URL verification in test
            dry_run=True,  # Don't create records
        )
        
        assert result.success is True
        assert len(result.candidates_found) == 2
        assert result.candidates_found[0].name == "SolarTech España"
    
    def test_search_with_deduplication(self, mock_airtable, mock_gemini) -> None:
        """Test search deduplicates against existing companies."""
        from agents.buscador import BuscadorEmpresas
        
        # Mock Gemini responses
        mock_gemini.search_and_generate.return_value = {"response": "Found"}
        mock_gemini.generate_json.return_value = {
            "companies": [
                {
                    "name": "Existing Company",
                    "home_url": "https://www.existing.es",
                    "sector": "Renewables",
                    "country": "ES",
                },
                {
                    "name": "New Company",
                    "home_url": "https://www.newco.es",
                    "sector": "Renewables",
                    "country": "ES",
                },
            ]
        }
        
        # Mock existing companies
        mock_airtable.query_records.return_value = [
            {
                "id": "recExisting",
                "fields": {
                    "Company Name": "Existing Company",
                    "Home_URL": "https://www.existing.es",
                },
            },
        ]
        
        agent = BuscadorEmpresas()
        result = agent.search(
            sector="renovables",
            country="ES",
            verify_urls=False,
            dry_run=True,
        )
        
        assert result.success is True
        assert result.duplicates_found == 1
        
        # Check duplicate is marked
        duplicates = [c for c in result.candidates_found if c.is_duplicate]
        assert len(duplicates) == 1
        assert duplicates[0].name == "Existing Company"


class TestBuildSearchQuery:
    """Tests for _build_search_query method."""
    
    def test_query_with_all_params(self, mock_airtable, mock_gemini) -> None:
        """Test query building with all parameters."""
        from agents.buscador import BuscadorEmpresas, SearchCriteria
        
        criteria = SearchCriteria(
            sector="energía solar",
            country="ES",
            region="Andalucía",
            min_employees=50,
            keywords=["fotovoltaica"],
        )
        
        agent = BuscadorEmpresas()
        query = agent._build_search_query(criteria)
        
        assert "energía solar" in query
        assert "Andalucía" in query
        assert "España" in query
        assert "50 empleados" in query
        assert "fotovoltaica" in query
    
    def test_query_minimal(self, mock_airtable, mock_gemini) -> None:
        """Test query building with minimal parameters."""
        from agents.buscador import BuscadorEmpresas, SearchCriteria
        
        criteria = SearchCriteria(sector="tecnología")
        
        agent = BuscadorEmpresas()
        query = agent._build_search_query(criteria)
        
        assert "tecnología" in query


class TestDeduplicate:
    """Tests for _deduplicate method."""
    
    def test_dedupe_exact_name(self, mock_airtable, mock_gemini) -> None:
        """Test deduplication by exact name match."""
        from agents.buscador import BuscadorEmpresas, CompanyCandidate
        
        candidates = [
            CompanyCandidate(name="Test Company", home_url="https://test.com"),
        ]
        
        mock_airtable.query_records.return_value = [
            {
                "id": "recExisting",
                "fields": {
                    "Company Name": "Test Company",
                    "Home_URL": "https://other.com",
                },
            },
        ]
        
        agent = BuscadorEmpresas()
        agent._deduplicate(candidates)
        
        assert candidates[0].is_duplicate is True
        assert candidates[0].duplicate_of == "recExisting"
    
    def test_dedupe_same_domain(self, mock_airtable, mock_gemini) -> None:
        """Test deduplication by domain match."""
        from agents.buscador import BuscadorEmpresas, CompanyCandidate
        
        candidates = [
            CompanyCandidate(name="Different Name", home_url="https://www.example.com"),
        ]
        
        mock_airtable.query_records.return_value = [
            {
                "id": "recExisting",
                "fields": {
                    "Company Name": "Original Company",
                    "Home_URL": "https://example.com",
                },
            },
        ]
        
        agent = BuscadorEmpresas()
        agent._deduplicate(candidates)
        
        assert candidates[0].is_duplicate is True
    
    def test_dedupe_similar_name(self, mock_airtable, mock_gemini) -> None:
        """Test deduplication by similar name (>90%)."""
        from agents.buscador import BuscadorEmpresas, CompanyCandidate
        
        candidates = [
            CompanyCandidate(name="Test Company SL", home_url="https://test.com"),
        ]
        
        mock_airtable.query_records.return_value = [
            {
                "id": "recExisting",
                "fields": {
                    "Company Name": "Test Company S.L.",
                    "Home_URL": "https://other.com",
                },
            },
        ]
        
        agent = BuscadorEmpresas()
        agent._deduplicate(candidates)
        
        assert candidates[0].is_duplicate is True


class TestCreateRecords:
    """Tests for _create_records method."""
    
    def test_creates_company_and_bu(self, mock_airtable, mock_gemini) -> None:
        """Test creates Company and BU Default records."""
        from agents.buscador import BuscadorEmpresas, CompanyCandidate
        
        candidate = CompanyCandidate(
            name="New Company",
            home_url="https://www.newco.es",
            description="A new company",
            sector="Technology",
            country="ES",
            estimated_employees=100,
        )
        
        mock_airtable.create_record.side_effect = [
            {"id": "recCompany001"},
            {"id": "recBU001"},
        ]
        
        agent = BuscadorEmpresas()
        company_id, bu_id = agent._create_records(candidate)
        
        assert company_id == "recCompany001"
        assert bu_id == "recBU001"
        
        # Verify calls
        assert mock_airtable.create_record.call_count == 2
        
        # Verify Company record
        company_call = mock_airtable.create_record.call_args_list[0]
        assert company_call[0][0] == "companies"
        fields = company_call[0][1]
        assert fields["Company Name"] == "New Company"
        assert fields["Source"] == "AI_Scraping"
        
        # Verify BU record
        bu_call = mock_airtable.create_record.call_args_list[1]
        assert bu_call[0][0] == "business_units"
        bu_fields = bu_call[0][1]
        assert bu_fields["Business Unit Name"] == "Default"
        assert bu_fields["Company"] == ["recCompany001"]


class TestFactoryFunction:
    """Tests for get_buscador factory function."""
    
    def test_get_buscador_singleton(self, mock_airtable, mock_gemini) -> None:
        """Test get_buscador returns singleton."""
        # Reset singleton
        import agents.buscador as module
        module._agent = None
        
        from agents.buscador import get_buscador
        
        agent1 = get_buscador()
        agent2 = get_buscador()
        
        assert agent1 is agent2

