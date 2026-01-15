"""Tests for CampaignOrchestrator."""

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
    with patch("core.campaign_orchestrator.get_airtable_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_analizador():
    """Mock AnalizadorContexto."""
    with patch("core.campaign_orchestrator.get_analizador") as mock:
        agent = MagicMock()
        mock.return_value = agent
        yield agent


@pytest.fixture
def mock_selector():
    """Mock SelectorTargets."""
    with patch("core.campaign_orchestrator.get_selector") as mock:
        agent = MagicMock()
        mock.return_value = agent
        yield agent


@pytest.fixture
def mock_redactor():
    """Mock RedactorMensajes."""
    with patch("core.campaign_orchestrator.get_redactor") as mock:
        agent = MagicMock()
        mock.return_value = agent
        yield agent


class TestCampaignProposal:
    """Tests for CampaignProposal dataclass."""
    
    def test_proposal_creation(self) -> None:
        """Test CampaignProposal can be created."""
        from core.campaign_orchestrator import CampaignProposal
        
        proposal = CampaignProposal(
            campaign_id="recCamp001",
            trigger="BCE baja tipos 0.25%",
            status="Draft",
        )
        
        assert proposal.campaign_id == "recCamp001"
        assert proposal.status == "Draft"
    
    def test_proposal_summary(self) -> None:
        """Test CampaignProposal summary generation."""
        from core.campaign_orchestrator import CampaignProposal
        
        proposal = CampaignProposal(
            campaign_id="recCamp001",
            trigger="BCE baja tipos 0.25%",
            status="Pending_Approval",
        )
        
        summary = proposal.summary()
        assert "recCamp001" in summary
        assert "Pending_Approval" in summary


class TestCampaignResult:
    """Tests for CampaignResult dataclass."""
    
    def test_result_str_success(self) -> None:
        """Test CampaignResult string for success."""
        from core.campaign_orchestrator import CampaignResult
        
        result = CampaignResult(
            campaign_id="recCamp001",
            status="Ready",
            success=True,
            total_processing_time_seconds=10.5,
        )
        
        result_str = str(result)
        assert "✅" in result_str
        assert "Ready" in result_str
    
    def test_result_str_failure(self) -> None:
        """Test CampaignResult string for failure."""
        from core.campaign_orchestrator import CampaignResult
        
        result = CampaignResult(
            campaign_id="recCamp001",
            status="Failed",
            success=False,
            errors=["Analysis failed"],
        )
        
        result_str = str(result)
        assert "❌" in result_str
        assert "Analysis failed" in result_str


class TestCampaignOrchestrator:
    """Tests for CampaignOrchestrator."""
    
    def test_init(
        self, mock_airtable, mock_analizador, mock_selector, mock_redactor
    ) -> None:
        """Test CampaignOrchestrator initializes correctly."""
        from core.campaign_orchestrator import CampaignOrchestrator
        
        orchestrator = CampaignOrchestrator()
        
        assert orchestrator._airtable is not None
        assert orchestrator._analizador is not None
        assert orchestrator._selector is not None
        assert orchestrator._redactor is not None
    
    def test_create_proposal_success(
        self, mock_airtable, mock_analizador, mock_selector, mock_redactor
    ) -> None:
        """Test successful proposal creation."""
        from core.campaign_orchestrator import CampaignOrchestrator
        from agents.analizador import AnalysisResult, ImpactAnalysis, Urgency
        from agents.selector import SelectionResult, TargetCandidate
        
        # Mock analysis result
        mock_analysis = AnalysisResult(
            trigger="BCE baja tipos",
            success=True,
            impact=ImpactAnalysis(
                affected_sectors=["Industrials"],
                affected_countries=["ES"],
                urgency=Urgency.HIGH,
                campaign_potential=4,
            ),
            key_angles=["Angle 1", "Angle 2", "Angle 3"],
        )
        mock_analizador.analyze.return_value = mock_analysis
        
        # Mock selection result
        mock_selection = SelectionResult(
            campaign_id="recCamp001",
            success=True,
            targets=[
                TargetCandidate(
                    business_unit_id="recBU001",
                    business_unit_name="Unit 1",
                    company_id="recCo001",
                    company_name="Company 1",
                    fit_score=0.85,
                ),
            ],
            total_candidates=5,
        )
        mock_selector.select.return_value = mock_selection
        
        orchestrator = CampaignOrchestrator()
        proposal = orchestrator.create_proposal(
            trigger="BCE baja tipos 0.25%",
            sectors=["Industrials"],
            countries=["ES"],
            dry_run=True,
        )
        
        assert proposal.status == "Pending_Approval"
        assert proposal.analysis is not None
        assert proposal.selection is not None
        assert len(proposal.selection.targets) > 0
    
    def test_create_proposal_analysis_fails(
        self, mock_airtable, mock_analizador, mock_selector, mock_redactor
    ) -> None:
        """Test proposal when analysis fails."""
        from core.campaign_orchestrator import CampaignOrchestrator
        from agents.analizador import AnalysisResult
        
        mock_analysis = AnalysisResult(
            trigger="Bad trigger",
            success=False,
            errors=["Trigger too short"],
        )
        mock_analizador.analyze.return_value = mock_analysis
        
        orchestrator = CampaignOrchestrator()
        proposal = orchestrator.create_proposal(
            trigger="Bad",
            sectors=["Industrials"],
            countries=["ES"],
            dry_run=True,
        )
        
        assert proposal.status == "Failed"
    
    def test_create_proposal_no_targets(
        self, mock_airtable, mock_analizador, mock_selector, mock_redactor
    ) -> None:
        """Test proposal when no targets found."""
        from core.campaign_orchestrator import CampaignOrchestrator
        from agents.analizador import AnalysisResult, ImpactAnalysis
        from agents.selector import SelectionResult
        
        mock_analysis = AnalysisResult(
            trigger="Test",
            success=True,
            impact=ImpactAnalysis(affected_sectors=["Industrials"]),
        )
        mock_analizador.analyze.return_value = mock_analysis
        
        mock_selection = SelectionResult(
            campaign_id="recCamp001",
            success=False,
            errors=["No candidates found"],
        )
        mock_selector.select.return_value = mock_selection
        
        orchestrator = CampaignOrchestrator()
        proposal = orchestrator.create_proposal(
            trigger="Test trigger",
            sectors=["Industrials"],
            countries=["ES"],
            dry_run=True,
        )
        
        assert proposal.status == "No_Targets"
    
    def test_approve_campaign(
        self, mock_airtable, mock_analizador, mock_selector, mock_redactor
    ) -> None:
        """Test campaign approval."""
        from core.campaign_orchestrator import CampaignOrchestrator
        
        orchestrator = CampaignOrchestrator()
        result = orchestrator.approve_campaign("recCamp001", dry_run=True)
        
        assert result is True
    
    def test_complete_campaign_success(
        self, mock_airtable, mock_analizador, mock_selector, mock_redactor
    ) -> None:
        """Test successful campaign completion."""
        from core.campaign_orchestrator import CampaignOrchestrator
        from agents.redactor import BatchGenerationResult
        
        mock_batch = BatchGenerationResult(
            campaign_id="recCamp001",
            success_count=5,
            failure_count=0,
            total_processing_time_seconds=5.0,
        )
        mock_redactor.generate_batch.return_value = mock_batch
        
        orchestrator = CampaignOrchestrator()
        result = orchestrator.complete_campaign(
            campaign_id="recCamp001",
            dry_run=True,
        )
        
        assert result.success is True
        assert result.status == "Ready"
        assert result.messages.success_count == 5
    
    def test_complete_campaign_partial_failure(
        self, mock_airtable, mock_analizador, mock_selector, mock_redactor
    ) -> None:
        """Test campaign completion with some failures."""
        from core.campaign_orchestrator import CampaignOrchestrator
        from agents.redactor import BatchGenerationResult
        
        mock_batch = BatchGenerationResult(
            campaign_id="recCamp001",
            success_count=3,
            failure_count=2,
            total_processing_time_seconds=5.0,
        )
        mock_redactor.generate_batch.return_value = mock_batch
        
        orchestrator = CampaignOrchestrator()
        result = orchestrator.complete_campaign(
            campaign_id="recCamp001",
            dry_run=True,
        )
        
        assert result.success is True  # Still success if some messages generated
        assert "2 messages failed" in result.errors[0]


class TestCreateCampaignFull:
    """Tests for create_campaign_full method."""
    
    def test_full_campaign_auto_approve(
        self, mock_airtable, mock_analizador, mock_selector, mock_redactor
    ) -> None:
        """Test full campaign with auto-approve."""
        from core.campaign_orchestrator import CampaignOrchestrator
        from agents.analizador import AnalysisResult, ImpactAnalysis
        from agents.selector import SelectionResult, TargetCandidate
        from agents.redactor import BatchGenerationResult
        
        # Mock all agent responses
        mock_analizador.analyze.return_value = AnalysisResult(
            trigger="Test",
            success=True,
            impact=ImpactAnalysis(
                affected_sectors=["Industrials"],
                affected_countries=["ES"],
                campaign_potential=4,
            ),
            key_angles=["Angle 1"],
        )
        
        mock_selector.select.return_value = SelectionResult(
            campaign_id="recCamp001",
            success=True,
            targets=[
                TargetCandidate(
                    business_unit_id="recBU001",
                    business_unit_name="Unit 1",
                    company_id="recCo001",
                    company_name="Company 1",
                    fit_score=0.85,
                ),
            ],
        )
        
        mock_redactor.generate_batch.return_value = BatchGenerationResult(
            campaign_id="recCamp001",
            success_count=1,
            failure_count=0,
        )
        
        orchestrator = CampaignOrchestrator()
        result = orchestrator.create_campaign_full(
            trigger="BCE baja tipos 0.25%",
            sectors=["Industrials"],
            countries=["ES"],
            auto_approve=True,
            dry_run=True,
        )
        
        assert result.success is True
        assert result.status == "Ready"
    
    def test_full_campaign_with_callback(
        self, mock_airtable, mock_analizador, mock_selector, mock_redactor
    ) -> None:
        """Test full campaign with approval callback."""
        from core.campaign_orchestrator import CampaignOrchestrator
        from agents.analizador import AnalysisResult, ImpactAnalysis
        from agents.selector import SelectionResult, TargetCandidate
        from agents.redactor import BatchGenerationResult
        
        # Mock all agent responses
        mock_analizador.analyze.return_value = AnalysisResult(
            trigger="Test",
            success=True,
            impact=ImpactAnalysis(affected_sectors=["Industrials"]),
            key_angles=["Angle 1"],
        )
        
        mock_selector.select.return_value = SelectionResult(
            campaign_id="recCamp001",
            success=True,
            targets=[
                TargetCandidate(
                    business_unit_id="recBU001",
                    business_unit_name="Unit 1",
                    company_id="recCo001",
                    company_name="Company 1",
                    fit_score=0.85,
                ),
            ],
        )
        
        mock_redactor.generate_batch.return_value = BatchGenerationResult(
            campaign_id="recCamp001",
            success_count=1,
            failure_count=0,
        )
        
        # Custom approval callback
        def approve_callback(proposal):
            return True
        
        orchestrator = CampaignOrchestrator()
        result = orchestrator.create_campaign_full(
            trigger="Test trigger",
            sectors=["Industrials"],
            countries=["ES"],
            on_approval_callback=approve_callback,
            dry_run=True,
        )
        
        assert result.success is True
    
    def test_full_campaign_rejected(
        self, mock_airtable, mock_analizador, mock_selector, mock_redactor
    ) -> None:
        """Test full campaign when rejected by callback."""
        from core.campaign_orchestrator import CampaignOrchestrator
        from agents.analizador import AnalysisResult, ImpactAnalysis
        from agents.selector import SelectionResult, TargetCandidate
        
        mock_analizador.analyze.return_value = AnalysisResult(
            trigger="Test",
            success=True,
            impact=ImpactAnalysis(affected_sectors=["Industrials"]),
        )
        
        mock_selector.select.return_value = SelectionResult(
            campaign_id="recCamp001",
            success=True,
            targets=[
                TargetCandidate(
                    business_unit_id="recBU001",
                    business_unit_name="Unit 1",
                    company_id="recCo001",
                    company_name="Company 1",
                    fit_score=0.85,
                ),
            ],
        )
        
        # Rejection callback
        def reject_callback(proposal):
            return False
        
        orchestrator = CampaignOrchestrator()
        result = orchestrator.create_campaign_full(
            trigger="Test trigger",
            sectors=["Industrials"],
            countries=["ES"],
            on_approval_callback=reject_callback,
            dry_run=True,
        )
        
        assert result.status == "Rejected"
        assert "not approved" in result.errors[0]


class TestFactoryFunction:
    """Tests for get_orchestrator factory function."""
    
    def test_get_orchestrator_singleton(
        self, mock_airtable, mock_analizador, mock_selector, mock_redactor
    ) -> None:
        """Test get_orchestrator returns singleton."""
        # Reset singleton
        import core.campaign_orchestrator as module
        module._orchestrator = None
        
        from core.campaign_orchestrator import get_orchestrator
        
        orch1 = get_orchestrator()
        orch2 = get_orchestrator()
        
        assert orch1 is orch2

