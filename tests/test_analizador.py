"""Tests for AnalizadorContexto agent."""

import os
from unittest.mock import MagicMock, patch
from datetime import date

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
    with patch("agents.analizador.get_airtable_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_gemini():
    """Mock GeminiClient."""
    with patch("agents.analizador.get_gemini_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_claude():
    """Mock ClaudeClient."""
    with patch("agents.analizador.get_claude_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


class TestNewsItem:
    """Tests for NewsItem dataclass."""
    
    def test_news_item_creation(self) -> None:
        """Test NewsItem can be created."""
        from agents.analizador import NewsItem
        
        item = NewsItem(
            title="BCE baja tipos de interés",
            source="Reuters",
            date=date.today(),
            summary="El BCE ha bajado los tipos...",
            relevance_score=0.95,
        )
        
        assert item.title == "BCE baja tipos de interés"
        assert item.source == "Reuters"
        assert item.relevance_score == 0.95


class TestImpactAnalysis:
    """Tests for ImpactAnalysis dataclass."""
    
    def test_impact_analysis_creation(self) -> None:
        """Test ImpactAnalysis can be created with defaults."""
        from agents.analizador import ImpactAnalysis, Urgency
        
        impact = ImpactAnalysis()
        
        assert impact.affected_sectors == []
        assert impact.affected_countries == []
        assert impact.urgency == Urgency.MEDIUM
        assert impact.campaign_potential == 3
    
    def test_impact_analysis_with_data(self) -> None:
        """Test ImpactAnalysis with full data."""
        from agents.analizador import ImpactAnalysis, Urgency
        
        impact = ImpactAnalysis(
            affected_sectors=["Industrials", "Real Estate"],
            affected_countries=["ES", "PT"],
            urgency=Urgency.HIGH,
            recommended_product="FEI_Guarantee",
            campaign_potential=5,
        )
        
        assert "Industrials" in impact.affected_sectors
        assert impact.urgency == Urgency.HIGH
        assert impact.campaign_potential == 5


class TestAnalysisResult:
    """Tests for AnalysisResult dataclass."""
    
    def test_should_create_campaign_high_potential(self) -> None:
        """Test should_create_campaign returns True for high potential."""
        from agents.analizador import AnalysisResult, ImpactAnalysis
        
        result = AnalysisResult(
            trigger="BCE baja tipos",
            success=True,
            impact=ImpactAnalysis(campaign_potential=5),
        )
        
        assert result.should_create_campaign() is True
    
    def test_should_create_campaign_low_potential(self) -> None:
        """Test should_create_campaign returns False for low potential."""
        from agents.analizador import AnalysisResult, ImpactAnalysis
        
        result = AnalysisResult(
            trigger="Minor news",
            success=True,
            impact=ImpactAnalysis(campaign_potential=2),
        )
        
        assert result.should_create_campaign() is False
    
    def test_should_create_campaign_no_impact(self) -> None:
        """Test should_create_campaign returns False without impact."""
        from agents.analizador import AnalysisResult
        
        result = AnalysisResult(trigger="Failed analysis", success=False)
        
        assert result.should_create_campaign() is False
    
    def test_get_summary_success(self) -> None:
        """Test get_summary for successful analysis."""
        from agents.analizador import AnalysisResult, ImpactAnalysis
        
        result = AnalysisResult(
            trigger="BCE baja tipos 0.25%",
            success=True,
            impact=ImpactAnalysis(
                affected_sectors=["Industrials", "Real Estate"],
                affected_countries=["ES", "PT"],
                campaign_potential=4,
            ),
            key_angles=["Angle 1", "Angle 2"],
        )
        
        summary = result.get_summary()
        assert "✅" in summary
        assert "Industrials" in summary
        assert "ES" in summary
    
    def test_get_summary_failure(self) -> None:
        """Test get_summary for failed analysis."""
        from agents.analizador import AnalysisResult
        
        result = AnalysisResult(
            trigger="Failed",
            success=False,
            errors=["API error"],
        )
        
        summary = result.get_summary()
        assert "❌" in summary
        assert "API error" in summary


class TestAnalizadorContexto:
    """Tests for AnalizadorContexto agent."""
    
    def test_init(self, mock_airtable, mock_gemini, mock_claude) -> None:
        """Test AnalizadorContexto initializes correctly."""
        from agents.analizador import AnalizadorContexto
        
        agent = AnalizadorContexto()
        
        assert agent._airtable is not None
        assert agent._gemini is not None
        assert agent._claude is not None
        assert agent._system_prompt is not None
    
    def test_analyze_success(self, mock_airtable, mock_gemini, mock_claude) -> None:
        """Test successful trigger analysis."""
        from agents.analizador import AnalizadorContexto
        
        # Mock Gemini news search
        mock_gemini.search_and_generate.return_value = {
            "response": "Found news about BCE"
        }
        mock_gemini.generate_json.return_value = {
            "news_items": [
                {
                    "title": "BCE baja tipos de interés",
                    "source": "Reuters",
                    "date": "2026-01-02",
                    "summary": "El BCE ha bajado los tipos...",
                    "relevance_score": 0.95,
                }
            ]
        }
        
        # Mock Claude impact analysis
        mock_claude.generate_structured.side_effect = [
            # Impact analysis
            {
                "affected_sectors": ["Industrials", "Real Estate"],
                "affected_countries": ["ES", "PT"],
                "urgency": "high",
                "recommended_product": "FEI_Guarantee",
                "campaign_potential": 5,
                "impact_summary": "Interest rate cut will benefit...",
                "opportunities": ["Refinance debt", "New projects"],
                "risks": ["Market volatility"],
            },
            # Key angles
            {
                "key_angles": [
                    "Oportunidad de refinanciar deuda variable",
                    "Momento ideal para nuevos proyectos",
                    "Accede a garantías FEI con tipos preferentes",
                ]
            },
        ]
        
        mock_airtable.create_record.return_value = {"id": "recTestContext"}
        
        agent = AnalizadorContexto()
        result = agent.analyze("BCE baja tipos 0.25%", dry_run=True)
        
        assert result.success is True
        assert len(result.news_found) > 0
        assert result.impact is not None
        assert result.impact.campaign_potential == 5
        assert len(result.key_angles) >= 3
    
    def test_analyze_short_trigger(self, mock_airtable, mock_gemini, mock_claude) -> None:
        """Test analysis fails for short trigger text."""
        from agents.analizador import AnalizadorContexto
        
        agent = AnalizadorContexto()
        result = agent.analyze("short")
        
        assert result.success is False
        assert "too short" in result.errors[0]
    
    def test_analyze_with_target_sectors(
        self, mock_airtable, mock_gemini, mock_claude
    ) -> None:
        """Test analysis with target sectors specified."""
        from agents.analizador import AnalizadorContexto
        
        mock_gemini.search_and_generate.return_value = {"response": "News"}
        mock_gemini.generate_json.return_value = {"news_items": []}
        mock_claude.generate_structured.side_effect = [
            {
                "affected_sectors": ["Renewables"],
                "affected_countries": ["ES"],
                "urgency": "medium",
                "recommended_product": "FEI_Guarantee",
                "campaign_potential": 4,
                "impact_summary": "Impact on renewables...",
                "opportunities": [],
                "risks": [],
            },
            {"key_angles": ["Angle 1", "Angle 2", "Angle 3"]},
        ]
        
        agent = AnalizadorContexto()
        result = agent.analyze(
            "Nuevo plan de energías renovables",
            target_sectors=["Renewables"],
            dry_run=True,
        )
        
        assert result.success is True
        assert "Renewables" in result.impact.affected_sectors


class TestSearchNews:
    """Tests for _search_news method."""
    
    def test_search_news_returns_items(
        self, mock_airtable, mock_gemini, mock_claude
    ) -> None:
        """Test _search_news returns news items."""
        from agents.analizador import AnalizadorContexto
        
        mock_gemini.search_and_generate.return_value = {
            "response": "News results"
        }
        mock_gemini.generate_json.return_value = {
            "news_items": [
                {"title": "News 1", "source": "Reuters", "relevance_score": 0.9},
                {"title": "News 2", "source": "Bloomberg", "relevance_score": 0.8},
            ]
        }
        
        agent = AnalizadorContexto()
        news = agent._search_news("BCE baja tipos")
        
        assert len(news) == 2
        assert news[0].title == "News 1"
        assert news[0].relevance_score > news[1].relevance_score
    
    def test_search_news_limits_to_10(
        self, mock_airtable, mock_gemini, mock_claude
    ) -> None:
        """Test _search_news returns max 10 items."""
        from agents.analizador import AnalizadorContexto
        
        mock_gemini.search_and_generate.return_value = {"response": "News"}
        mock_gemini.generate_json.return_value = {
            "news_items": [
                {"title": f"News {i}", "source": "Source", "relevance_score": 0.5}
                for i in range(15)
            ]
        }
        
        agent = AnalizadorContexto()
        news = agent._search_news("test trigger")
        
        assert len(news) == 10
    
    def test_search_news_handles_error(
        self, mock_airtable, mock_gemini, mock_claude
    ) -> None:
        """Test _search_news handles Gemini errors gracefully."""
        from agents.analizador import AnalizadorContexto
        from integrations.gemini import GeminiError
        
        mock_gemini.search_and_generate.side_effect = GeminiError("API error")
        
        agent = AnalizadorContexto()
        news = agent._search_news("test trigger")
        
        assert news == []


class TestAnalyzeImpact:
    """Tests for _analyze_impact method."""
    
    def test_analyze_impact_valid_response(
        self, mock_airtable, mock_gemini, mock_claude
    ) -> None:
        """Test _analyze_impact with valid Claude response."""
        from agents.analizador import AnalizadorContexto, Urgency
        
        mock_claude.generate_structured.return_value = {
            "affected_sectors": ["Industrials", "Technology"],
            "affected_countries": ["ES", "PT"],
            "urgency": "high",
            "recommended_product": "FEI_Guarantee",
            "campaign_potential": 4,
            "impact_summary": "High impact expected",
            "opportunities": ["Opportunity 1"],
            "risks": ["Risk 1"],
        }
        
        agent = AnalizadorContexto()
        impact = agent._analyze_impact("test trigger", [])
        
        assert "Industrials" in impact.affected_sectors
        assert "ES" in impact.affected_countries
        assert impact.urgency == Urgency.HIGH
        assert impact.campaign_potential == 4
    
    def test_analyze_impact_filters_invalid_sectors(
        self, mock_airtable, mock_gemini, mock_claude
    ) -> None:
        """Test _analyze_impact filters invalid sectors."""
        from agents.analizador import AnalizadorContexto
        
        mock_claude.generate_structured.return_value = {
            "affected_sectors": ["Industrials", "InvalidSector"],
            "affected_countries": ["ES"],
            "urgency": "medium",
            "recommended_product": "FEI_Guarantee",
            "campaign_potential": 3,
            "impact_summary": "",
            "opportunities": [],
            "risks": [],
        }
        
        agent = AnalizadorContexto()
        impact = agent._analyze_impact("test trigger", [])
        
        assert "Industrials" in impact.affected_sectors
        assert "InvalidSector" not in impact.affected_sectors
    
    def test_analyze_impact_clamps_campaign_potential(
        self, mock_airtable, mock_gemini, mock_claude
    ) -> None:
        """Test _analyze_impact clamps campaign_potential to 1-5."""
        from agents.analizador import AnalizadorContexto
        
        mock_claude.generate_structured.return_value = {
            "affected_sectors": ["Industrials"],
            "affected_countries": ["ES"],
            "urgency": "high",
            "recommended_product": "FEI_Guarantee",
            "campaign_potential": 10,  # Invalid, should be clamped
            "impact_summary": "",
            "opportunities": [],
            "risks": [],
        }
        
        agent = AnalizadorContexto()
        impact = agent._analyze_impact("test trigger", [])
        
        assert impact.campaign_potential == 5  # Clamped to max


class TestGenerateAngles:
    """Tests for _generate_angles method."""
    
    def test_generate_angles_returns_list(
        self, mock_airtable, mock_gemini, mock_claude
    ) -> None:
        """Test _generate_angles returns list of angles."""
        from agents.analizador import AnalizadorContexto, ImpactAnalysis
        
        mock_claude.generate_structured.return_value = {
            "key_angles": [
                "Oportunidad de refinanciar deuda variable",
                "Momento ideal para nuevos proyectos de inversión",
                "Accede a garantías FEI con tipos preferentes",
            ]
        }
        
        agent = AnalizadorContexto()
        impact = ImpactAnalysis(
            affected_sectors=["Industrials"],
            affected_countries=["ES"],
            opportunities=["Test opportunity"],
        )
        
        angles = agent._generate_angles("BCE baja tipos", impact, [])
        
        assert len(angles) >= 3
        assert all(len(angle) >= 20 for angle in angles)
    
    def test_generate_angles_ensures_minimum_3(
        self, mock_airtable, mock_gemini, mock_claude
    ) -> None:
        """Test _generate_angles ensures at least 3 angles."""
        from agents.analizador import AnalizadorContexto, ImpactAnalysis
        
        mock_claude.generate_structured.return_value = {
            "key_angles": ["Short angle"]  # Only 1 valid (but too short)
        }
        
        agent = AnalizadorContexto()
        impact = ImpactAnalysis()
        
        angles = agent._generate_angles("test trigger", impact, [])
        
        assert len(angles) >= 3


class TestSaveContext:
    """Tests for _save_context method."""
    
    def test_save_context_creates_record(
        self, mock_airtable, mock_gemini, mock_claude
    ) -> None:
        """Test _save_context creates Airtable record."""
        from agents.analizador import AnalizadorContexto, AnalysisResult, ImpactAnalysis
        
        mock_airtable.create_record.return_value = {"id": "recNewContext"}
        
        agent = AnalizadorContexto()
        result = AnalysisResult(
            trigger="BCE baja tipos 0.25%",
            success=True,
            impact=ImpactAnalysis(
                affected_sectors=["Industrials"],
                affected_countries=["ES"],
                campaign_potential=4,
            ),
            key_angles=["Angle 1", "Angle 2", "Angle 3"],
        )
        
        record_id = agent._save_context(result)
        
        assert record_id == "recNewContext"
        mock_airtable.create_record.assert_called_once()
        
        # Verify fields
        call_args = mock_airtable.create_record.call_args
        fields = call_args[0][1]
        assert fields["Trigger_Description"] == "BCE baja tipos 0.25%"
        assert "Industrials" in fields["Affected_Sectors"]


class TestFactoryFunction:
    """Tests for get_analizador factory function."""
    
    def test_get_analizador_singleton(
        self, mock_airtable, mock_gemini, mock_claude
    ) -> None:
        """Test get_analizador returns singleton."""
        # Reset singleton
        import agents.analizador as module
        module._agent = None
        
        from agents.analizador import get_analizador
        
        agent1 = get_analizador()
        agent2 = get_analizador()
        
        assert agent1 is agent2

