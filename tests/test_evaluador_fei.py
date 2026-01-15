"""Tests for EvaluadorFEI agent."""

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
    with patch("agents.evaluador_fei.get_airtable_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_gemini():
    """Mock GeminiClient."""
    with patch("agents.evaluador_fei.get_gemini_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_claude():
    """Mock ClaudeClient."""
    with patch("agents.evaluador_fei.get_claude_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


class TestCertificateEvidence:
    """Tests for CertificateEvidence dataclass."""
    
    def test_certificate_evidence_creation(self) -> None:
        """Test CertificateEvidence can be created."""
        from agents.evaluador_fei import CertificateEvidence
        
        cert = CertificateEvidence(
            certificate_type="ISO 14001",
            certificate_name="ISO 14001:2015",
            issuer="Bureau Veritas",
            fei_criteria="1.6_Environmental_Certificate",
        )
        
        assert cert.certificate_type == "ISO 14001"
        assert cert.issuer == "Bureau Veritas"
        assert cert.fei_criteria == "1.6_Environmental_Certificate"


class TestPrizeEvidence:
    """Tests for PrizeEvidence dataclass."""
    
    def test_prize_evidence_creation(self) -> None:
        """Test PrizeEvidence can be created."""
        from agents.evaluador_fei import PrizeEvidence
        
        prize = PrizeEvidence(
            prize_name="Horizon Europe Grant",
            year=2024,
            awarding_organization="European Commission",
        )
        
        assert prize.prize_name == "Horizon Europe Grant"
        assert prize.year == 2024


class TestEvaluationResult:
    """Tests for EvaluationResult dataclass."""
    
    def test_is_eligible_true(self) -> None:
        """Test is_eligible returns True for eligible status."""
        from agents.evaluador_fei import EvaluationResult
        from core.models import FEIStatus, FEICriteria
        
        result = EvaluationResult(
            company_id="recTest",
            company_name="Test Corp",
            status=FEIStatus.ELIGIBLE,
            criteria_met=[FEICriteria.ENVIRONMENTAL_CERTIFICATE],
            confidence=90,
            reasoning="Has ISO 14001",
        )
        
        assert result.is_eligible() is True
    
    def test_is_eligible_false(self) -> None:
        """Test is_eligible returns False for non-eligible status."""
        from agents.evaluador_fei import EvaluationResult
        from core.models import FEIStatus
        
        result = EvaluationResult(
            company_id="recTest",
            company_name="Test Corp",
            status=FEIStatus.NOT_ELIGIBLE,
            criteria_met=[],
            confidence=85,
            reasoning="No criteria met",
        )
        
        assert result.is_eligible() is False
    
    def test_needs_review_low_confidence(self) -> None:
        """Test needs_review returns True for low confidence."""
        from agents.evaluador_fei import EvaluationResult
        from core.models import FEIStatus
        
        result = EvaluationResult(
            company_id="recTest",
            company_name="Test Corp",
            status=FEIStatus.ELIGIBLE,
            criteria_met=[],
            confidence=60,  # Below 70%
            reasoning="Low confidence evaluation",
        )
        
        assert result.needs_review() is True
    
    def test_needs_review_pending_status(self) -> None:
        """Test needs_review returns True for pending review status."""
        from agents.evaluador_fei import EvaluationResult
        from core.models import FEIStatus
        
        result = EvaluationResult(
            company_id="recTest",
            company_name="Test Corp",
            status=FEIStatus.PENDING_REVIEW,
            criteria_met=[],
            confidence=80,
            reasoning="Needs manual verification",
        )
        
        assert result.needs_review() is True


class TestEvaluadorFEI:
    """Tests for EvaluadorFEI agent."""
    
    def test_init(self, mock_airtable, mock_gemini, mock_claude) -> None:
        """Test EvaluadorFEI initializes correctly."""
        from agents.evaluador_fei import EvaluadorFEI
        
        agent = EvaluadorFEI()
        
        assert agent._airtable is not None
        assert agent._gemini is not None
        assert agent._claude is not None
        assert agent._system_prompt is not None
    
    def test_evaluate_eligible_with_certificate(
        self, mock_airtable, mock_gemini, mock_claude
    ) -> None:
        """Test evaluation returns Eligible for company with ISO 14001."""
        from agents.evaluador_fei import EvaluadorFEI
        from core.models import FEIStatus, FEICriteria
        
        # Setup mocks
        mock_airtable.get_record.return_value = {
            "id": "recTestCompany",
            "fields": {
                "Company Name": "Green Corp",
                "Home URL": "https://greencorp.com",
                "Description": "Sustainable manufacturing company",
            }
        }
        
        # Mock Gemini search for certificates
        mock_gemini.search_and_generate.return_value = {
            "response": "Found ISO 14001 certificate"
        }
        mock_gemini.generate_json.side_effect = [
            # Certificates search
            {"certificates": [{"certificate_type": "ISO 14001", "certificate_name": "ISO 14001:2015", "issuer": "Bureau Veritas"}]},
            # Eco-labels search
            {"eco_labels": []},
            # Prizes search
            {"prizes": []},
            # Green activities search
            {"green_activities": [], "total_green_revenue_percentage": 30},
        ]
        
        # Mock Claude evaluation
        mock_claude.generate_structured.return_value = {
            "status": "Eligible",
            "criteria_met": ["1.6_Environmental_Certificate"],
            "confidence": 90,
            "reasoning": "Company has valid ISO 14001 certification from Bureau Veritas",
            "criteria_evaluation": {
                "1.6_Environmental_Certificate": {"met": True, "evidence": "ISO 14001:2015", "confidence": 90}
            }
        }
        
        agent = EvaluadorFEI()
        result = agent.evaluate("recTestCompany", dry_run=True)
        
        assert result.status == FEIStatus.ELIGIBLE
        assert FEICriteria.ENVIRONMENTAL_CERTIFICATE in result.criteria_met
        assert result.confidence == 90
        assert len(result.certificates_found) > 0
    
    def test_evaluate_not_eligible(
        self, mock_airtable, mock_gemini, mock_claude
    ) -> None:
        """Test evaluation returns Not_Eligible when no criteria met."""
        from agents.evaluador_fei import EvaluadorFEI
        from core.models import FEIStatus
        
        # Setup mocks
        mock_airtable.get_record.return_value = {
            "id": "recTestCompany",
            "fields": {
                "Company Name": "Regular Corp",
                "Home URL": "https://regularcorp.com",
            }
        }
        
        # Mock Gemini - no evidence found
        mock_gemini.search_and_generate.return_value = {"response": "No evidence found"}
        mock_gemini.generate_json.side_effect = [
            {"certificates": []},
            {"eco_labels": []},
            {"prizes": []},
            {"green_activities": [], "total_green_revenue_percentage": 10},
        ]
        
        # Mock Claude evaluation
        mock_claude.generate_structured.return_value = {
            "status": "Not_Eligible",
            "criteria_met": [],
            "confidence": 85,
            "reasoning": "No FEI criteria met - company does not have relevant certifications or green activities",
            "criteria_evaluation": {}
        }
        
        agent = EvaluadorFEI()
        result = agent.evaluate("recTestCompany", dry_run=True)
        
        assert result.status == FEIStatus.NOT_ELIGIBLE
        assert len(result.criteria_met) == 0
    
    def test_evaluate_green_business_90(
        self, mock_airtable, mock_gemini, mock_claude
    ) -> None:
        """Test evaluation returns Eligible for 90%+ green revenue (Criterion 1.4)."""
        from agents.evaluador_fei import EvaluadorFEI
        from core.models import FEIStatus, FEICriteria
        
        # Setup mocks
        mock_airtable.get_record.return_value = {
            "id": "recSolarCompany",
            "fields": {
                "Company Name": "Solar Tech",
                "Home URL": "https://solartech.com",
                "Description": "100% solar energy company",
                "Business Units": [],
            }
        }
        
        # Mock Gemini - found green activities
        mock_gemini.search_and_generate.return_value = {"response": "Solar company"}
        mock_gemini.generate_json.side_effect = [
            {"certificates": []},
            {"eco_labels": []},
            {"prizes": []},
            {
                "green_activities": [
                    {"activity_name": "Solar panel installation", "activity_type": "Solar energy", "estimated_revenue_percentage": 95, "is_primary_activity": True}
                ],
                "total_green_revenue_percentage": 95,
                "is_inherently_green": True
            },
        ]
        
        # Mock Claude evaluation
        mock_claude.generate_structured.return_value = {
            "status": "Eligible",
            "criteria_met": ["1.4_Green_Business_90", "1.5_Green_Business_Model"],
            "confidence": 88,
            "reasoning": "Company derives 95% of revenue from solar energy, qualifying for criterion 1.4",
            "criteria_evaluation": {
                "1.4_Green_Business_90": {"met": True, "evidence": "95% solar revenue", "confidence": 90},
                "1.5_Green_Business_Model": {"met": True, "evidence": "Inherently green solar business", "confidence": 85}
            }
        }
        
        agent = EvaluadorFEI()
        result = agent.evaluate("recSolarCompany", dry_run=True)
        
        assert result.status == FEIStatus.ELIGIBLE
        assert FEICriteria.GREEN_BUSINESS_90 in result.criteria_met
    
    def test_evaluate_with_prize(
        self, mock_airtable, mock_gemini, mock_claude
    ) -> None:
        """Test evaluation recognizes cleantech prize (Criterion 1.1)."""
        from agents.evaluador_fei import EvaluadorFEI
        from core.models import FEIStatus, FEICriteria
        
        # Setup mocks
        mock_airtable.get_record.return_value = {
            "id": "recInnovCompany",
            "fields": {
                "Company Name": "CleanTech Innovators",
                "Home URL": "https://cleantech.com",
            }
        }
        
        # Mock Gemini - found prize
        mock_gemini.search_and_generate.return_value = {"response": "Prize winner"}
        mock_gemini.generate_json.side_effect = [
            {"certificates": []},
            {"eco_labels": []},
            {"prizes": [{"prize_name": "EIT Climate-KIC", "year": 2024, "awarding_organization": "EIT"}]},
            {"green_activities": []},
        ]
        
        # Mock Claude evaluation
        mock_claude.generate_structured.return_value = {
            "status": "Eligible",
            "criteria_met": ["1.1_Cleantech_Prize"],
            "confidence": 85,
            "reasoning": "Company won EIT Climate-KIC award in 2024",
            "criteria_evaluation": {
                "1.1_Cleantech_Prize": {"met": True, "evidence": "EIT Climate-KIC 2024", "confidence": 85}
            }
        }
        
        agent = EvaluadorFEI()
        result = agent.evaluate("recInnovCompany", dry_run=True)
        
        assert result.status == FEIStatus.ELIGIBLE
        assert FEICriteria.CLEANTECH_PRIZE in result.criteria_met
        assert len(result.prizes_found) > 0
    
    def test_evaluate_pending_review_low_confidence(
        self, mock_airtable, mock_gemini, mock_claude
    ) -> None:
        """Test evaluation returns Pending_Review for ambiguous cases."""
        from agents.evaluador_fei import EvaluadorFEI
        from core.models import FEIStatus
        
        # Setup mocks
        mock_airtable.get_record.return_value = {
            "id": "recAmbiguousCompany",
            "fields": {
                "Company Name": "Maybe Green Corp",
                "Home URL": "https://maybegreen.com",
            }
        }
        
        # Mock Gemini - unclear evidence
        mock_gemini.search_and_generate.return_value = {"response": "Unclear evidence"}
        mock_gemini.generate_json.side_effect = [
            {"certificates": []},
            {"eco_labels": []},
            {"prizes": []},
            {"green_activities": [{"activity_name": "Consulting", "activity_type": "Services", "estimated_revenue_percentage": 50}]},
        ]
        
        # Mock Claude evaluation
        mock_claude.generate_structured.return_value = {
            "status": "Pending_Review",
            "criteria_met": [],
            "confidence": 45,
            "reasoning": "Evidence is inconclusive - company may have green activities but cannot verify percentage",
            "criteria_evaluation": {}
        }
        
        agent = EvaluadorFEI()
        result = agent.evaluate("recAmbiguousCompany", dry_run=True)
        
        assert result.status == FEIStatus.PENDING_REVIEW
        assert result.confidence < 70
        assert result.needs_review() is True
    
    def test_evaluate_skips_recent(self, mock_airtable, mock_gemini, mock_claude) -> None:
        """Test evaluation skips companies evaluated recently."""
        from agents.evaluador_fei import EvaluadorFEI
        from core.models import FEIStatus
        from datetime import date, timedelta
        
        recent_date = (date.today() - timedelta(days=15)).isoformat()
        
        mock_airtable.get_record.return_value = {
            "id": "recRecentCompany",
            "fields": {
                "Company Name": "Recent Corp",
                "FEI_Status": "Eligible",
                "FEI_Confidence": 0.85,
                "FEI_Last_Check": recent_date,
            }
        }
        
        agent = EvaluadorFEI()
        result = agent.evaluate("recRecentCompany", force=False, dry_run=True)
        
        # Should skip because evaluated 15 days ago
        assert "Skipped" in result.reasoning
        # Gemini shouldn't be called for search
        assert mock_gemini.search_and_generate.call_count == 0
    
    def test_evaluate_force_reeval(self, mock_airtable, mock_gemini, mock_claude) -> None:
        """Test force=True forces re-evaluation."""
        from agents.evaluador_fei import EvaluadorFEI
        from datetime import date, timedelta
        
        recent_date = (date.today() - timedelta(days=15)).isoformat()
        
        mock_airtable.get_record.return_value = {
            "id": "recForceCompany",
            "fields": {
                "Company Name": "Force Corp",
                "FEI_Status": "Eligible",
                "FEI_Confidence": 0.85,
                "FEI_Last_Check": recent_date,
            }
        }
        
        mock_gemini.search_and_generate.return_value = {"response": ""}
        mock_gemini.generate_json.side_effect = [
            {"certificates": []},
            {"eco_labels": []},
            {"prizes": []},
            {"green_activities": []},
        ]
        mock_claude.generate_structured.return_value = {
            "status": "Not_Eligible",
            "criteria_met": [],
            "confidence": 80,
            "reasoning": "Re-evaluated",
            "criteria_evaluation": {}
        }
        
        agent = EvaluadorFEI()
        result = agent.evaluate("recForceCompany", force=True, dry_run=True)
        
        # Should NOT skip because force=True
        assert "Skipped" not in result.reasoning
        # Gemini should be called
        assert mock_gemini.search_and_generate.call_count > 0
    
    def test_search_certificates(self, mock_airtable, mock_gemini, mock_claude) -> None:
        """Test _search_certificates finds ISO certificates."""
        from agents.evaluador_fei import EvaluadorFEI
        
        mock_gemini.search_and_generate.return_value = {
            "response": "Found ISO 14001"
        }
        mock_gemini.generate_json.return_value = {
            "certificates": [
                {
                    "certificate_type": "ISO 14001",
                    "certificate_name": "ISO 14001:2015",
                    "issuer": "TÜV",
                    "expiry_date": "2026-01-01"
                }
            ]
        }
        
        agent = EvaluadorFEI()
        certs = agent._search_certificates("Test Corp", "https://test.com")
        
        assert len(certs) == 1
        assert certs[0].certificate_type == "ISO 14001"
        assert certs[0].fei_criteria == "1.6_Environmental_Certificate"
    
    def test_search_eco_labels(self, mock_airtable, mock_gemini, mock_claude) -> None:
        """Test _search_eco_labels finds eco-labels."""
        from agents.evaluador_fei import EvaluadorFEI
        
        mock_gemini.search_and_generate.return_value = {
            "response": "Found EU Ecolabel"
        }
        mock_gemini.generate_json.return_value = {
            "eco_labels": [
                {"label_name": "EU Ecolabel", "products_certified": "Paper products"}
            ]
        }
        
        agent = EvaluadorFEI()
        labels = agent._search_eco_labels("Test Corp", "https://test.com")
        
        assert len(labels) == 1
        assert labels[0].certificate_name == "EU Ecolabel"
        assert labels[0].fei_criteria == "1.3_Eco_Label"
    
    def test_save_evaluation(self, mock_airtable, mock_gemini, mock_claude) -> None:
        """Test _save_evaluation updates Airtable correctly."""
        from agents.evaluador_fei import EvaluadorFEI, EvaluationResult
        from core.models import FEIStatus, FEICriteria
        
        mock_airtable.update_record.return_value = {"id": "recTest"}
        
        agent = EvaluadorFEI()
        result = EvaluationResult(
            company_id="recTest",
            company_name="Test Corp",
            status=FEIStatus.ELIGIBLE,
            criteria_met=[FEICriteria.ENVIRONMENTAL_CERTIFICATE],
            confidence=90,
            reasoning="Has ISO 14001",
        )
        
        agent._save_evaluation("recTest", result)
        
        mock_airtable.update_record.assert_called_once()
        call_args = mock_airtable.update_record.call_args
        assert call_args[0][0] == "companies"
        assert call_args[0][1] == "recTest"
        fields = call_args[0][2]
        assert fields["FEI_Status"] == "Eligible"
        assert fields["FEI_Confidence"] == 0.9  # Converted to 0-1
        assert "1.6_Environmental_Certificate" in fields["FEI_Criteria_Met"]


class TestBatchEvaluation:
    """Tests for batch FEI evaluation."""
    
    def test_evaluate_batch(self, mock_airtable, mock_gemini, mock_claude) -> None:
        """Test evaluate_batch processes multiple companies."""
        from agents.evaluador_fei import EvaluadorFEI
        from core.models import FEIStatus
        
        # Setup mocks for multiple companies
        mock_airtable.get_record.return_value = {
            "id": "recTest",
            "fields": {"Company Name": "Test Corp"}
        }
        
        mock_gemini.search_and_generate.return_value = {"response": ""}
        mock_gemini.generate_json.side_effect = [
            {"certificates": []}, {"eco_labels": []}, {"prizes": []}, {"green_activities": []},
            {"certificates": []}, {"eco_labels": []}, {"prizes": []}, {"green_activities": []},
        ]
        mock_claude.generate_structured.return_value = {
            "status": "Not_Eligible",
            "criteria_met": [],
            "confidence": 80,
            "reasoning": "No criteria met",
            "criteria_evaluation": {}
        }
        
        agent = EvaluadorFEI()
        results = agent.evaluate_batch(
            company_ids=["rec1", "rec2"],
            dry_run=True,
        )
        
        assert len(results) == 2
        assert all(r.status == FEIStatus.NOT_ELIGIBLE for r in results)


class TestFactoryFunction:
    """Tests for get_evaluador_fei factory function."""
    
    def test_get_evaluador_fei_singleton(self, mock_airtable, mock_gemini, mock_claude) -> None:
        """Test get_evaluador_fei returns singleton."""
        # Reset singleton
        import agents.evaluador_fei as module
        module._agent = None
        
        from agents.evaluador_fei import get_evaluador_fei
        
        agent1 = get_evaluador_fei()
        agent2 = get_evaluador_fei()
        
        assert agent1 is agent2

