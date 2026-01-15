"""Tests for OriginationPipeline."""

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
def mock_buscador():
    """Mock BuscadorEmpresas."""
    with patch("core.origination_pipeline.get_buscador") as mock:
        agent = MagicMock()
        mock.return_value = agent
        yield agent


@pytest.fixture
def mock_enriquecedor():
    """Mock EnriquecedorDatos."""
    with patch("core.origination_pipeline.get_enriquecedor") as mock:
        agent = MagicMock()
        mock.return_value = agent
        yield agent


@pytest.fixture
def mock_evaluador():
    """Mock EvaluadorFEI."""
    with patch("core.origination_pipeline.get_evaluador_fei") as mock:
        agent = MagicMock()
        mock.return_value = agent
        yield agent


class TestCompanyOriginationResult:
    """Tests for CompanyOriginationResult dataclass."""
    
    def test_result_creation(self) -> None:
        """Test CompanyOriginationResult can be created."""
        from core.origination_pipeline import CompanyOriginationResult
        
        result = CompanyOriginationResult(
            company_id="recCo001",
            company_name="Test Company",
        )
        
        assert result.company_id == "recCo001"
        assert result.success is False
    
    def test_summary(self) -> None:
        """Test CompanyOriginationResult summary."""
        from core.origination_pipeline import CompanyOriginationResult
        
        result = CompanyOriginationResult(
            company_id="recCo001",
            company_name="Test Company",
            success=True,
        )
        
        summary = result.summary()
        assert "Test Company" in summary


class TestOriginationResult:
    """Tests for OriginationResult dataclass."""
    
    def test_result_str_success(self) -> None:
        """Test OriginationResult string for success."""
        from core.origination_pipeline import OriginationResult
        from agents.buscador import SearchCriteria
        
        result = OriginationResult(
            criteria=SearchCriteria(sector="renovables"),
            success=True,
            companies_found=10,
            companies_enriched=8,
            companies_fei_evaluated=8,
            companies_fei_eligible=3,
        )
        
        result_str = str(result)
        assert "✅" in result_str
        assert "10" in result_str
    
    def test_result_str_failure(self) -> None:
        """Test OriginationResult string for failure."""
        from core.origination_pipeline import OriginationResult
        from agents.buscador import SearchCriteria
        
        result = OriginationResult(
            criteria=SearchCriteria(sector="test"),
            success=False,
            errors=["Search failed"],
        )
        
        result_str = str(result)
        assert "❌" in result_str
        assert "Search failed" in result_str
    
    def test_get_eligible_companies(self) -> None:
        """Test get_eligible_companies filters correctly."""
        from core.origination_pipeline import (
            OriginationResult,
            CompanyOriginationResult,
        )
        from agents.buscador import SearchCriteria
        from agents.evaluador_fei import EvaluationResult
        from core.models import FEIStatus
        
        result = OriginationResult(
            criteria=SearchCriteria(sector="test"),
            company_results=[
                CompanyOriginationResult(
                    company_id="rec1",
                    company_name="Eligible Co",
                    fei_result=EvaluationResult(
                        company_id="rec1",
                        company_name="Eligible Co",
                        status=FEIStatus.ELIGIBLE,
                        criteria_met=[],
                        confidence=85.0,
                        reasoning="Eligible company",
                    ),
                ),
                CompanyOriginationResult(
                    company_id="rec2",
                    company_name="Not Eligible Co",
                    fei_result=EvaluationResult(
                        company_id="rec2",
                        company_name="Not Eligible Co",
                        status=FEIStatus.NOT_ELIGIBLE,
                        criteria_met=[],
                        confidence=90.0,
                        reasoning="Not eligible",
                    ),
                ),
            ],
        )
        
        eligible = result.get_eligible_companies()
        assert len(eligible) == 1
        assert eligible[0].company_name == "Eligible Co"


class TestOriginationPipeline:
    """Tests for OriginationPipeline."""
    
    def test_init(self, mock_buscador, mock_enriquecedor, mock_evaluador) -> None:
        """Test OriginationPipeline initializes correctly."""
        from core.origination_pipeline import OriginationPipeline
        
        pipeline = OriginationPipeline()
        
        assert pipeline._buscador is not None
        assert pipeline._enriquecedor is not None
        assert pipeline._evaluador is not None
    
    def test_originate_search_only(
        self, mock_buscador, mock_enriquecedor, mock_evaluador
    ) -> None:
        """Test originate with search only (no enrich/FEI)."""
        from core.origination_pipeline import OriginationPipeline
        from agents.buscador import SearchResult, SearchCriteria, CompanyCandidate
        
        # Mock search result
        mock_buscador.search.return_value = SearchResult(
            criteria=SearchCriteria(sector="renovables"),
            success=True,
            candidates_found=[
                CompanyCandidate(name="Company 1", url_verified=True),
                CompanyCandidate(name="Company 2", url_verified=True),
            ],
            companies_created=["recCo001", "recCo002"],
        )
        
        pipeline = OriginationPipeline()
        result = pipeline.originate(
            sector="renovables",
            country="ES",
            limit=10,
            enrich=False,
            evaluate_fei=False,
            dry_run=True,
        )
        
        assert result.success is True
        assert result.companies_found >= 0  # Dry run, no actual creation
        mock_buscador.search.assert_called_once()
    
    def test_originate_full_pipeline(
        self, mock_buscador, mock_enriquecedor, mock_evaluador
    ) -> None:
        """Test full origination pipeline."""
        from core.origination_pipeline import OriginationPipeline
        from agents.buscador import SearchResult, SearchCriteria, CompanyCandidate
        from agents.enriquecedor import EnrichmentResult
        from agents.evaluador_fei import EvaluationResult
        from core.models import FEIStatus
        
        # Mock search
        mock_buscador.search.return_value = SearchResult(
            criteria=SearchCriteria(sector="renovables"),
            success=True,
            candidates_found=[
                CompanyCandidate(name="Solar Tech", url_verified=True),
            ],
            companies_created=["recCo001"],
        )
        
        # Mock enrichment
        mock_enriquecedor.enrich.return_value = EnrichmentResult(
            company_id="recCo001",
            success=True,
        )
        
        # Mock FEI evaluation
        mock_evaluador.evaluate.return_value = EvaluationResult(
            company_id="recCo001",
            company_name="Solar Tech",
            status=FEIStatus.ELIGIBLE,
            criteria_met=[],
            confidence=85.0,
            reasoning="Eligible",
        )
        
        pipeline = OriginationPipeline()
        result = pipeline.originate(
            sector="renovables",
            country="ES",
            limit=10,
            enrich=True,
            evaluate_fei=True,
            dry_run=False,
        )
        
        assert result.success is True
        assert result.companies_found == 1
        mock_buscador.search.assert_called_once()
        mock_enriquecedor.enrich.assert_called_once()
        mock_evaluador.evaluate.assert_called_once()
    
    def test_originate_search_fails(
        self, mock_buscador, mock_enriquecedor, mock_evaluador
    ) -> None:
        """Test originate when search fails."""
        from core.origination_pipeline import OriginationPipeline
        from agents.buscador import SearchResult, SearchCriteria
        
        mock_buscador.search.return_value = SearchResult(
            criteria=SearchCriteria(sector="test"),
            success=False,
            errors=["No companies found"],
        )
        
        pipeline = OriginationPipeline()
        result = pipeline.originate(
            sector="test",
            country="ES",
            dry_run=True,
        )
        
        assert result.success is False
        assert "No companies found" in result.errors
    
    def test_originate_with_progress_callback(
        self, mock_buscador, mock_enriquecedor, mock_evaluador
    ) -> None:
        """Test originate with progress callback."""
        from core.origination_pipeline import OriginationPipeline
        from agents.buscador import SearchResult, SearchCriteria
        
        mock_buscador.search.return_value = SearchResult(
            criteria=SearchCriteria(sector="test"),
            success=True,
            candidates_found=[],
            companies_created=[],
        )
        
        progress_calls = []
        
        def on_progress(step: int, total: int, message: str) -> None:
            progress_calls.append((step, total, message))
        
        pipeline = OriginationPipeline()
        pipeline.originate(
            sector="test",
            country="ES",
            on_progress=on_progress,
            dry_run=True,
        )
        
        assert len(progress_calls) >= 1


class TestFactoryFunction:
    """Tests for get_origination_pipeline factory function."""
    
    def test_get_pipeline_singleton(
        self, mock_buscador, mock_enriquecedor, mock_evaluador
    ) -> None:
        """Test get_origination_pipeline returns singleton."""
        # Reset singleton
        import core.origination_pipeline as module
        module._pipeline = None
        
        from core.origination_pipeline import get_origination_pipeline
        
        pipeline1 = get_origination_pipeline()
        pipeline2 = get_origination_pipeline()
        
        assert pipeline1 is pipeline2

