"""Tests for SelectorTargets agent."""

import os
from unittest.mock import MagicMock, patch
from datetime import date, timedelta

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
    with patch("agents.selector.get_airtable_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_claude():
    """Mock ClaudeClient."""
    with patch("agents.selector.get_claude_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


class TestTargetCandidate:
    """Tests for TargetCandidate dataclass."""
    
    def test_candidate_creation(self) -> None:
        """Test TargetCandidate can be created."""
        from agents.selector import TargetCandidate
        
        candidate = TargetCandidate(
            business_unit_id="recBU001",
            business_unit_name="Tech Unit",
            company_id="recCo001",
            company_name="Tech Corp",
            sector="Technology",
            country="ES",
            fei_status="Eligible",
        )
        
        assert candidate.business_unit_name == "Tech Unit"
        assert candidate.fei_status == "Eligible"
    
    def test_is_in_cooling_off_no_date(self) -> None:
        """Test is_in_cooling_off returns False when no last outreach."""
        from agents.selector import TargetCandidate
        
        candidate = TargetCandidate(
            business_unit_id="recBU001",
            business_unit_name="Test",
            company_id="recCo001",
            company_name="Test Corp",
        )
        
        assert candidate.is_in_cooling_off() is False
    
    def test_is_in_cooling_off_recent(self) -> None:
        """Test is_in_cooling_off returns True for recent outreach."""
        from agents.selector import TargetCandidate
        
        recent_date = date.today() - timedelta(days=30)
        
        candidate = TargetCandidate(
            business_unit_id="recBU001",
            business_unit_name="Test",
            company_id="recCo001",
            company_name="Test Corp",
            last_outreach_date=recent_date,
        )
        
        assert candidate.is_in_cooling_off() is True
    
    def test_is_in_cooling_off_old(self) -> None:
        """Test is_in_cooling_off returns False for old outreach."""
        from agents.selector import TargetCandidate
        
        old_date = date.today() - timedelta(days=120)
        
        candidate = TargetCandidate(
            business_unit_id="recBU001",
            business_unit_name="Test",
            company_id="recCo001",
            company_name="Test Corp",
            last_outreach_date=old_date,
        )
        
        assert candidate.is_in_cooling_off() is False
    
    def test_days_since_outreach(self) -> None:
        """Test days_since_outreach calculation."""
        from agents.selector import TargetCandidate
        
        past_date = date.today() - timedelta(days=45)
        
        candidate = TargetCandidate(
            business_unit_id="recBU001",
            business_unit_name="Test",
            company_id="recCo001",
            company_name="Test Corp",
            last_outreach_date=past_date,
        )
        
        assert candidate.days_since_outreach() == 45


class TestSelectionResult:
    """Tests for SelectionResult dataclass."""
    
    def test_result_str_success(self) -> None:
        """Test SelectionResult string for success."""
        from agents.selector import SelectionResult, TargetCandidate
        
        result = SelectionResult(
            campaign_id="recCamp001",
            success=True,
            targets=[
                TargetCandidate(
                    business_unit_id="recBU001",
                    business_unit_name="Test",
                    company_id="recCo001",
                    company_name="Test Corp",
                    fit_score=0.85,
                ),
            ],
            total_candidates=5,
            excluded_cooling_off=2,
            excluded_low_score=2,
        )
        
        result_str = str(result)
        assert "✅" in result_str
        assert "1/5" in result_str
    
    def test_result_str_failure(self) -> None:
        """Test SelectionResult string for failure."""
        from agents.selector import SelectionResult
        
        result = SelectionResult(
            campaign_id="recCamp001",
            success=False,
            errors=["No candidates found"],
        )
        
        result_str = str(result)
        assert "❌" in result_str
        assert "No candidates found" in result_str


class TestSelectorTargets:
    """Tests for SelectorTargets agent."""
    
    def test_init(self, mock_airtable, mock_claude) -> None:
        """Test SelectorTargets initializes correctly."""
        from agents.selector import SelectorTargets
        
        agent = SelectorTargets()
        
        assert agent._airtable is not None
        assert agent._claude is not None
        assert agent._system_prompt is not None
    
    def test_select_success(self, mock_airtable, mock_claude) -> None:
        """Test successful target selection."""
        from agents.selector import SelectorTargets
        
        # Mock BU query
        mock_airtable.query_records.return_value = [
            {
                "id": "recBU001",
                "fields": {
                    "Business Unit Name": "Tech Unit",
                    "Sector": "Industrials",
                    "Country": "ES",
                    "Company": ["recCo001"],
                    "Contacts": ["recContact001"],
                },
            },
            {
                "id": "recBU002",
                "fields": {
                    "Business Unit Name": "Green Unit",
                    "Sector": "Renewables",
                    "Country": "PT",
                    "Company": ["recCo002"],
                    "Contacts": [],
                },
            },
        ]
        
        # Mock company fetch
        mock_airtable.get_record.side_effect = [
            # Company 1
            {
                "id": "recCo001",
                "fields": {
                    "Company Name": "Tech Corp",
                    "FEI_Status": "Eligible",
                    "Sector": "Industrials",
                    "Financials": ["recFin001"],
                },
            },
            # Contact 1
            {
                "id": "recContact001",
                "fields": {
                    "First Name": "John",
                    "Last Name": "Doe",
                    "Role": "CEO",
                    "Key Person": "Yes",
                },
            },
            # Company 2
            {
                "id": "recCo002",
                "fields": {
                    "Company Name": "Green Energy",
                    "FEI_Status": "Unknown",
                    "Sector": "Renewables",
                    "Financials": [],
                },
            },
        ]
        
        # Mock Claude justifications
        mock_claude.generate_structured.return_value = {
            "justifications": [
                "Target prioritario: empresa FEI elegible con sector alineado.",
                "Target secundario: sector renovable con potencial.",
            ]
        }
        
        agent = SelectorTargets()
        result = agent.select(
            campaign_id="recCamp001",
            affected_sectors=["Industrials", "Renewables"],
            affected_countries=["ES", "PT"],
            dry_run=True,
        )
        
        assert result.success is True
        assert len(result.targets) >= 1
        assert result.total_candidates >= 1
    
    def test_select_no_candidates(self, mock_airtable, mock_claude) -> None:
        """Test selection with no candidates."""
        from agents.selector import SelectorTargets
        
        mock_airtable.query_records.return_value = []
        
        agent = SelectorTargets()
        result = agent.select(
            campaign_id="recCamp001",
            affected_sectors=["NonExistentSector"],
            affected_countries=["XX"],
            dry_run=True,
        )
        
        assert result.success is False
        assert "No candidates found" in result.errors[0]
    
    def test_select_max_targets_enforced(self, mock_airtable, mock_claude) -> None:
        """Test max targets is enforced at 30."""
        from agents.selector import SelectorTargets, MAX_TARGETS_PER_CAMPAIGN
        
        # Create 50 mock BUs
        mock_airtable.query_records.return_value = [
            {
                "id": f"recBU{i:03d}",
                "fields": {
                    "Business Unit Name": f"Unit {i}",
                    "Sector": "Industrials",
                    "Country": "ES",
                    "Company": [f"recCo{i:03d}"],
                    "Contacts": [],
                },
            }
            for i in range(50)
        ]
        
        # Mock company fetches
        mock_airtable.get_record.side_effect = [
            {
                "id": f"recCo{i:03d}",
                "fields": {
                    "Company Name": f"Corp {i}",
                    "FEI_Status": "Eligible",
                    "Sector": "Industrials",
                    "Financials": [],
                },
            }
            for i in range(50)
        ]
        
        mock_claude.generate_structured.return_value = {
            "justifications": [f"Justification {i}" for i in range(30)]
        }
        
        agent = SelectorTargets()
        result = agent.select(
            campaign_id="recCamp001",
            affected_sectors=["Industrials"],
            affected_countries=["ES"],
            max_targets=100,  # Try to request more than max
            dry_run=True,
        )
        
        # Should be capped at 30
        assert len(result.targets) <= MAX_TARGETS_PER_CAMPAIGN


class TestFilterByCriteria:
    """Tests for _filter_by_criteria method."""
    
    def test_filter_builds_correct_formula(self, mock_airtable, mock_claude) -> None:
        """Test filter builds correct Airtable formula."""
        from agents.selector import SelectorTargets
        
        mock_airtable.query_records.return_value = []
        
        agent = SelectorTargets()
        agent._filter_by_criteria(
            affected_sectors=["Industrials", "Renewables"],
            affected_countries=["ES", "PT"],
        )
        
        # Verify query was called
        mock_airtable.query_records.assert_called_once()
        call_args = mock_airtable.query_records.call_args
        assert call_args[1]["table_name"] == "business_units"
        assert "Active" in call_args[1]["formula"]


class TestCalculateFitScore:
    """Tests for _calculate_fit_score method."""
    
    def test_score_fei_eligible(self, mock_airtable, mock_claude) -> None:
        """Test FEI eligible adds 20% to score."""
        from agents.selector import SelectorTargets, TargetCandidate
        
        candidate = TargetCandidate(
            business_unit_id="recBU001",
            business_unit_name="Test",
            company_id="recCo001",
            company_name="Test Corp",
            fei_status="Eligible",
        )
        
        agent = SelectorTargets()
        agent._calculate_fit_score(candidate, [], [])
        
        assert candidate.fit_score >= 0.70  # Base 0.50 + FEI 0.20
        assert "fei_eligible" in candidate.score_breakdown
    
    def test_score_key_person(self, mock_airtable, mock_claude) -> None:
        """Test key person adds 15% to score."""
        from agents.selector import SelectorTargets, TargetCandidate
        
        candidate = TargetCandidate(
            business_unit_id="recBU001",
            business_unit_name="Test",
            company_id="recCo001",
            company_name="Test Corp",
            has_key_person=True,
        )
        
        agent = SelectorTargets()
        agent._calculate_fit_score(candidate, [], [])
        
        assert candidate.fit_score >= 0.65  # Base 0.50 + Key 0.15
        assert "key_person_identified" in candidate.score_breakdown
    
    def test_score_sector_match(self, mock_airtable, mock_claude) -> None:
        """Test sector match adds 15% to score."""
        from agents.selector import SelectorTargets, TargetCandidate
        
        candidate = TargetCandidate(
            business_unit_id="recBU001",
            business_unit_name="Test",
            company_id="recCo001",
            company_name="Test Corp",
            sector="Industrials",
        )
        
        agent = SelectorTargets()
        agent._calculate_fit_score(candidate, ["Industrials"], [])
        
        assert candidate.fit_score >= 0.65  # Base 0.50 + Sector 0.15
        assert "sector_match" in candidate.score_breakdown
    
    def test_score_max_capped(self, mock_airtable, mock_claude) -> None:
        """Test score is capped at 1.0."""
        from agents.selector import SelectorTargets, TargetCandidate
        
        # Candidate with all bonuses
        candidate = TargetCandidate(
            business_unit_id="recBU001",
            business_unit_name="Test",
            company_id="recCo001",
            company_name="Test Corp",
            fei_status="Eligible",
            has_key_person=True,
            sector="Industrials",
            country="ES",
            has_financials=True,
            previous_engagement="positive response last year",
        )
        
        agent = SelectorTargets()
        agent._calculate_fit_score(candidate, ["Industrials"], ["ES"])
        
        assert candidate.fit_score <= 1.0


class TestPrioritize:
    """Tests for _prioritize method."""
    
    def test_prioritize_by_score(self, mock_airtable, mock_claude) -> None:
        """Test candidates are sorted by fit score descending."""
        from agents.selector import SelectorTargets, TargetCandidate
        
        candidates = [
            TargetCandidate(
                business_unit_id="recBU001",
                business_unit_name="Low",
                company_id="recCo001",
                company_name="Low Corp",
                fit_score=0.60,
            ),
            TargetCandidate(
                business_unit_id="recBU002",
                business_unit_name="High",
                company_id="recCo002",
                company_name="High Corp",
                fit_score=0.95,
            ),
            TargetCandidate(
                business_unit_id="recBU003",
                business_unit_name="Medium",
                company_id="recCo003",
                company_name="Medium Corp",
                fit_score=0.75,
            ),
        ]
        
        agent = SelectorTargets()
        sorted_candidates = agent._prioritize(candidates)
        
        assert sorted_candidates[0].fit_score == 0.95
        assert sorted_candidates[1].fit_score == 0.75
        assert sorted_candidates[2].fit_score == 0.60


class TestDefaultJustification:
    """Tests for _default_justification method."""
    
    def test_default_justification_fei(self, mock_airtable, mock_claude) -> None:
        """Test default justification mentions FEI status."""
        from agents.selector import SelectorTargets, TargetCandidate
        
        candidate = TargetCandidate(
            business_unit_id="recBU001",
            business_unit_name="Test",
            company_id="recCo001",
            company_name="Test Corp",
            fei_status="Eligible",
            fit_score=0.75,
        )
        
        agent = SelectorTargets()
        justification = agent._default_justification(candidate)
        
        assert "FEI elegible" in justification
    
    def test_default_justification_key_person(self, mock_airtable, mock_claude) -> None:
        """Test default justification mentions key person."""
        from agents.selector import SelectorTargets, TargetCandidate
        
        candidate = TargetCandidate(
            business_unit_id="recBU001",
            business_unit_name="Test",
            company_id="recCo001",
            company_name="Test Corp",
            has_key_person=True,
            key_person_role="CEO",
            fit_score=0.70,
        )
        
        agent = SelectorTargets()
        justification = agent._default_justification(candidate)
        
        assert "contacto clave" in justification
        assert "CEO" in justification


class TestSaveTargets:
    """Tests for _save_targets method."""
    
    def test_save_creates_records(self, mock_airtable, mock_claude) -> None:
        """Test save creates CampaignTarget records."""
        from agents.selector import SelectorTargets, TargetCandidate
        
        candidates = [
            TargetCandidate(
                business_unit_id="recBU001",
                business_unit_name="Test",
                company_id="recCo001",
                company_name="Test Corp",
                fit_score=0.85,
                selection_justification="Test justification",
                contact_id="recContact001",
            ),
        ]
        
        mock_airtable.create_record.return_value = {"id": "recTarget001"}
        
        agent = SelectorTargets()
        agent._save_targets("recCamp001", candidates)
        
        mock_airtable.create_record.assert_called_once()
        call_args = mock_airtable.create_record.call_args
        assert call_args[0][0] == "campaign_targets"
        fields = call_args[0][1]
        assert fields["Campaign"] == ["recCamp001"]
        assert fields["Business_Unit"] == ["recBU001"]
        assert fields["Fit_Score"] == 0.85


class TestFactoryFunction:
    """Tests for get_selector factory function."""
    
    def test_get_selector_singleton(self, mock_airtable, mock_claude) -> None:
        """Test get_selector returns singleton."""
        # Reset singleton
        import agents.selector as module
        module._agent = None
        
        from agents.selector import get_selector
        
        agent1 = get_selector()
        agent2 = get_selector()
        
        assert agent1 is agent2

