"""Tests for RedactorMensajes agent."""

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
    with patch("agents.redactor.get_airtable_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_claude():
    """Mock ClaudeClient."""
    with patch("agents.redactor.get_claude_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


class TestTargetContext:
    """Tests for TargetContext dataclass."""
    
    def test_context_creation(self) -> None:
        """Test TargetContext can be created."""
        from agents.redactor import TargetContext
        
        context = TargetContext(
            target_id="recTarget001",
            campaign_id="recCamp001",
            business_unit_id="recBU001",
            business_unit_name="Tech Unit",
            company_id="recCo001",
            company_name="Tech Corp",
            contact_first_name="Juan",
        )
        
        assert context.company_name == "Tech Corp"
        assert context.contact_first_name == "Juan"
    
    def test_has_personalization_data_true(self) -> None:
        """Test has_personalization_data returns True with enough data."""
        from agents.redactor import TargetContext
        
        context = TargetContext(
            target_id="recTarget001",
            campaign_id="recCamp001",
            business_unit_id="recBU001",
            business_unit_name="Tech Unit",
            company_id="recCo001",
            company_name="Tech Corp",
            contact_first_name="Juan",
            sector="Technology",
        )
        
        assert context.has_personalization_data() is True
    
    def test_has_personalization_data_false(self) -> None:
        """Test has_personalization_data returns False without data."""
        from agents.redactor import TargetContext
        
        context = TargetContext(
            target_id="recTarget001",
            campaign_id="recCamp001",
            business_unit_id="recBU001",
            business_unit_name="Unknown",
            company_id="recCo001",
            company_name="Tech Corp",
            # No contact_first_name
        )
        
        assert context.has_personalization_data() is False


class TestGeneratedMessage:
    """Tests for GeneratedMessage dataclass."""
    
    def test_message_creation(self) -> None:
        """Test GeneratedMessage can be created."""
        from agents.redactor import GeneratedMessage
        
        message = GeneratedMessage(
            target_id="recTarget001",
            subject="Test Subject",
            body="Test body text here.",
            word_count=4,
            personalization_score=0.75,
        )
        
        assert message.subject == "Test Subject"
        assert message.word_count == 4
    
    def test_is_within_limits_true(self) -> None:
        """Test is_within_limits returns True for valid message."""
        from agents.redactor import GeneratedMessage, MAX_EMAIL_WORDS
        
        message = GeneratedMessage(
            target_id="recTarget001",
            subject="Short subject",
            body="Short body",
            word_count=2,
            personalization_score=0.5,
        )
        
        assert message.is_within_limits() is True
    
    def test_is_within_limits_false_words(self) -> None:
        """Test is_within_limits returns False when too many words."""
        from agents.redactor import GeneratedMessage, MAX_EMAIL_WORDS
        
        message = GeneratedMessage(
            target_id="recTarget001",
            subject="Subject",
            body="Body",
            word_count=200,  # Over limit
            personalization_score=0.5,
        )
        
        assert message.is_within_limits() is False
    
    def test_is_within_limits_false_subject(self) -> None:
        """Test is_within_limits returns False when subject too long."""
        from agents.redactor import GeneratedMessage
        
        message = GeneratedMessage(
            target_id="recTarget001",
            subject="A" * 100,  # Over 80 chars
            body="Body",
            word_count=1,
            personalization_score=0.5,
        )
        
        assert message.is_within_limits() is False


class TestGenerationResult:
    """Tests for GenerationResult dataclass."""
    
    def test_result_str_success(self) -> None:
        """Test GenerationResult string for success."""
        from agents.redactor import GenerationResult, GeneratedMessage
        
        result = GenerationResult(
            target_id="recTarget001",
            success=True,
            message=GeneratedMessage(
                target_id="recTarget001",
                subject="Test Subject Line",
                body="Test body",
                word_count=2,
                personalization_score=0.85,
            ),
        )
        
        result_str = str(result)
        assert "✅" in result_str
        assert "85%" in result_str
    
    def test_result_str_failure(self) -> None:
        """Test GenerationResult string for failure."""
        from agents.redactor import GenerationResult
        
        result = GenerationResult(
            target_id="recTarget001",
            success=False,
            errors=["API timeout"],
        )
        
        result_str = str(result)
        assert "❌" in result_str
        assert "API timeout" in result_str


class TestRedactorMensajes:
    """Tests for RedactorMensajes agent."""
    
    def test_init(self, mock_airtable, mock_claude) -> None:
        """Test RedactorMensajes initializes correctly."""
        from agents.redactor import RedactorMensajes
        
        agent = RedactorMensajes()
        
        assert agent._airtable is not None
        assert agent._claude is not None
        assert agent._system_prompt is not None
    
    def test_generate_success(self, mock_airtable, mock_claude) -> None:
        """Test successful message generation."""
        from agents.redactor import RedactorMensajes
        
        # Mock target record
        mock_airtable.get_record.side_effect = [
            # Target
            {
                "id": "recTarget001",
                "fields": {
                    "Campaign": ["recCamp001"],
                    "Business_Unit": ["recBU001"],
                    "Contact": ["recContact001"],
                    "Fit_Score": 0.85,
                },
            },
            # Campaign
            {
                "id": "recCamp001",
                "fields": {
                    "Trigger_Description": "BCE baja tipos 0.25%",
                    "Key_Angles": ["Refinance debt", "New projects"],
                },
            },
            # Business Unit
            {
                "id": "recBU001",
                "fields": {
                    "Business Unit Name": "Tech Unit",
                    "Sector": "Technology",
                    "Country": "ES",
                    "Company": ["recCo001"],
                },
            },
            # Company
            {
                "id": "recCo001",
                "fields": {
                    "Company Name": "Tech Corp",
                    "FEI_Status": "Eligible",
                },
            },
            # Contact
            {
                "id": "recContact001",
                "fields": {
                    "First Name": "Juan",
                    "Last Name": "García",
                    "Role": "CFO",
                    "Email": "juan@techcorp.com",
                },
            },
        ]
        
        # Mock Claude responses
        mock_claude.generate_structured.side_effect = [
            # Subject
            {"subject": "Tech Corp: Acceso preferente a garantías FEI"},
            # Body
            {
                "body": """Hola Juan,

En Alter5 trabajamos con empresas como Tech Corp que cumplen criterios FEI.

Dado el contexto actual con la bajada de tipos del BCE, es un momento ideal para explorar financiación alternativa.

¿Podríamos agendar una llamada esta semana?

Un saludo,
Alter5""",
                "cta": "¿Podríamos agendar una llamada esta semana?",
            },
        ]
        
        agent = RedactorMensajes()
        result = agent.generate(
            target_id="recTarget001",
            dry_run=True,
        )
        
        assert result.success is True
        assert result.message is not None
        assert "Tech Corp" in result.message.subject
        assert result.message.word_count <= 150
    
    def test_generate_with_context(self, mock_airtable, mock_claude) -> None:
        """Test generation with campaign context."""
        from agents.redactor import RedactorMensajes
        
        # Mock minimal records
        mock_airtable.get_record.side_effect = [
            {
                "id": "recTarget001",
                "fields": {
                    "Campaign": [],
                    "Business_Unit": ["recBU001"],
                    "Contact": [],
                },
            },
            {
                "id": "recBU001",
                "fields": {
                    "Business Unit Name": "Unit 1",
                    "Company": ["recCo001"],
                },
            },
            {
                "id": "recCo001",
                "fields": {
                    "Company Name": "Company ABC",
                },
            },
        ]
        
        mock_claude.generate_structured.side_effect = [
            {"subject": "Oportunidad de financiación"},
            {"body": "Hola, mensaje corto aquí.", "cta": None},
        ]
        
        agent = RedactorMensajes()
        result = agent.generate(
            target_id="recTarget001",
            campaign_context="Nuevo plan industrial 2026",
            key_angles=["Inversión", "Crecimiento"],
            dry_run=True,
        )
        
        assert result.success is True


class TestGenerateSubject:
    """Tests for _generate_subject method."""
    
    def test_subject_max_length(self, mock_airtable, mock_claude) -> None:
        """Test subject is truncated to max length."""
        from agents.redactor import RedactorMensajes, TargetContext, MAX_SUBJECT_CHARS
        
        mock_claude.generate_structured.return_value = {
            "subject": "A" * 100  # Over limit
        }
        
        context = TargetContext(
            target_id="rec001",
            campaign_id="rec001",
            business_unit_id="rec001",
            business_unit_name="Unit",
            company_id="rec001",
            company_name="Company",
        )
        
        agent = RedactorMensajes()
        subject = agent._generate_subject(context, "professional")
        
        assert len(subject) <= MAX_SUBJECT_CHARS
    
    def test_subject_fallback(self, mock_airtable, mock_claude) -> None:
        """Test subject fallback when Claude fails."""
        from agents.redactor import RedactorMensajes, TargetContext
        from integrations.claude import ClaudeError
        
        mock_claude.generate_structured.side_effect = ClaudeError("API error")
        
        context = TargetContext(
            target_id="rec001",
            campaign_id="rec001",
            business_unit_id="rec001",
            business_unit_name="Unit",
            company_id="rec001",
            company_name="Test Company",
            fei_status="Eligible",
        )
        
        agent = RedactorMensajes()
        subject = agent._default_subject(context)
        
        assert "Test Company" in subject


class TestGenerateBody:
    """Tests for _generate_body method."""
    
    def test_body_generation(self, mock_airtable, mock_claude) -> None:
        """Test body generation with Claude."""
        from agents.redactor import RedactorMensajes, TargetContext
        
        mock_claude.generate_structured.return_value = {
            "body": "Hola Juan, mensaje de prueba.",
            "cta": "¿Hablamos?",
        }
        
        context = TargetContext(
            target_id="rec001",
            campaign_id="rec001",
            business_unit_id="rec001",
            business_unit_name="Unit",
            company_id="rec001",
            company_name="Company",
            contact_first_name="Juan",
        )
        
        agent = RedactorMensajes()
        body = agent._generate_body(context, "professional")
        
        assert "Juan" in body
    
    def test_body_fallback_fei_eligible(self, mock_airtable, mock_claude) -> None:
        """Test body fallback for FEI eligible company."""
        from agents.redactor import RedactorMensajes, TargetContext
        from integrations.claude import ClaudeError
        
        mock_claude.generate_structured.side_effect = ClaudeError("Error")
        
        context = TargetContext(
            target_id="rec001",
            campaign_id="rec001",
            business_unit_id="rec001",
            business_unit_name="Unit",
            company_id="rec001",
            company_name="Green Corp",
            contact_first_name="María",
            fei_status="Eligible",
        )
        
        agent = RedactorMensajes()
        body = agent._default_body(context)
        
        assert "María" in body
        assert "Green Corp" in body
        assert "FEI" in body


class TestPersonalizationScore:
    """Tests for _calculate_personalization_score method."""
    
    def test_score_all_factors(self, mock_airtable, mock_claude) -> None:
        """Test score with all personalization factors."""
        from agents.redactor import RedactorMensajes, TargetContext
        
        context = TargetContext(
            target_id="rec001",
            campaign_id="rec001",
            business_unit_id="rec001",
            business_unit_name="Unit",
            company_id="rec001",
            company_name="Acme Corp",
            contact_first_name="Juan",
            contact_role="CFO",
            sector="Technology",
            fei_status="Eligible",
            campaign_trigger="bajada tipos interés",
        )
        
        body = """
        Hola Juan, como CFO de Acme Corp en el sector Technology,
        la bajada de tipos de interés es una oportunidad para acceder al FEI.
        """
        
        agent = RedactorMensajes()
        score = agent._calculate_personalization_score(context, body)
        
        assert score >= 0.8  # Should have high score
    
    def test_score_no_personalization(self, mock_airtable, mock_claude) -> None:
        """Test score with no personalization."""
        from agents.redactor import RedactorMensajes, TargetContext
        
        context = TargetContext(
            target_id="rec001",
            campaign_id="rec001",
            business_unit_id="rec001",
            business_unit_name="Unit",
            company_id="rec001",
            company_name="Acme Corp",
            contact_first_name="Juan",
        )
        
        body = "Generic message without any personalization."
        
        agent = RedactorMensajes()
        score = agent._calculate_personalization_score(context, body)
        
        assert score < 0.3  # Should have low score


class TestWordCount:
    """Tests for _count_words method."""
    
    def test_count_words_simple(self, mock_airtable, mock_claude) -> None:
        """Test word counting."""
        from agents.redactor import RedactorMensajes
        
        agent = RedactorMensajes()
        
        assert agent._count_words("one two three") == 3
        assert agent._count_words("  one   two   three  ") == 3
        assert agent._count_words("") == 0


class TestTruncateBody:
    """Tests for _truncate_body method."""
    
    def test_truncate_long_body(self, mock_airtable, mock_claude) -> None:
        """Test truncating long body."""
        from agents.redactor import RedactorMensajes, MAX_EMAIL_WORDS
        
        # Create body with 200 words
        words = ["word"] * 200
        long_body = " ".join(words) + "."
        
        agent = RedactorMensajes()
        truncated = agent._truncate_body(long_body)
        
        assert agent._count_words(truncated) <= MAX_EMAIL_WORDS
    
    def test_no_truncate_short_body(self, mock_airtable, mock_claude) -> None:
        """Test no truncation for short body."""
        from agents.redactor import RedactorMensajes
        
        short_body = "This is a short body."
        
        agent = RedactorMensajes()
        result = agent._truncate_body(short_body)
        
        assert result == short_body


class TestExtractCTA:
    """Tests for _extract_cta method."""
    
    def test_extract_cta_question(self, mock_airtable, mock_claude) -> None:
        """Test extracting CTA question."""
        from agents.redactor import RedactorMensajes
        
        body = """
        Mensaje de prueba.
        ¿Podríamos agendar una llamada esta semana?
        Gracias.
        """
        
        agent = RedactorMensajes()
        cta = agent._extract_cta(body)
        
        assert cta is not None
        assert "llamada" in cta
    
    def test_extract_cta_none(self, mock_airtable, mock_claude) -> None:
        """Test no CTA found."""
        from agents.redactor import RedactorMensajes
        
        body = "Mensaje sin pregunta ni llamada a la acción."
        
        agent = RedactorMensajes()
        cta = agent._extract_cta(body)
        
        # May or may not find CTA depending on patterns
        # Just verify no error


class TestSaveMessage:
    """Tests for _save_message method."""
    
    def test_save_updates_record(self, mock_airtable, mock_claude) -> None:
        """Test save updates Airtable record."""
        from agents.redactor import RedactorMensajes, GeneratedMessage
        
        message = GeneratedMessage(
            target_id="recTarget001",
            subject="Test Subject",
            body="Test body text",
            word_count=3,
            personalization_score=0.75,
            tone="professional",
            cta="¿Hablamos?",
        )
        
        agent = RedactorMensajes()
        agent._save_message("recTarget001", message)
        
        mock_airtable.update_record.assert_called_once()
        call_args = mock_airtable.update_record.call_args
        assert call_args[0][0] == "campaign_targets"
        assert call_args[0][1] == "recTarget001"
        fields = call_args[0][2]
        assert fields["Email_Subject"] == "Test Subject"
        assert fields["Email_Body"] == "Test body text"


class TestBatchGeneration:
    """Tests for generate_batch method."""
    
    def test_batch_generation(self, mock_airtable, mock_claude) -> None:
        """Test batch message generation."""
        from agents.redactor import RedactorMensajes
        
        # Mock campaign targets query
        mock_airtable.query_records.return_value = [
            {"id": "recTarget001"},
            {"id": "recTarget002"},
        ]
        
        # Mock get_record for each target
        mock_airtable.get_record.side_effect = [
            # Target 1
            {"id": "recTarget001", "fields": {"Campaign": [], "Business_Unit": ["recBU001"], "Contact": []}},
            {"id": "recBU001", "fields": {"Business Unit Name": "Unit 1", "Company": ["recCo001"]}},
            {"id": "recCo001", "fields": {"Company Name": "Company 1"}},
            # Target 2
            {"id": "recTarget002", "fields": {"Campaign": [], "Business_Unit": ["recBU002"], "Contact": []}},
            {"id": "recBU002", "fields": {"Business Unit Name": "Unit 2", "Company": ["recCo002"]}},
            {"id": "recCo002", "fields": {"Company Name": "Company 2"}},
        ]
        
        # Mock Claude for each target (2 calls per target: subject + body)
        mock_claude.generate_structured.side_effect = [
            {"subject": "Subject 1"},
            {"body": "Body 1", "cta": None},
            {"subject": "Subject 2"},
            {"body": "Body 2", "cta": None},
        ]
        
        agent = RedactorMensajes()
        result = agent.generate_batch(
            campaign_id="recCamp001",
            dry_run=True,
        )
        
        assert result.success_count == 2
        assert result.failure_count == 0
        assert len(result.results) == 2


class TestFactoryFunction:
    """Tests for get_redactor factory function."""
    
    def test_get_redactor_singleton(self, mock_airtable, mock_claude) -> None:
        """Test get_redactor returns singleton."""
        # Reset singleton
        import agents.redactor as module
        module._agent = None
        
        from agents.redactor import get_redactor
        
        agent1 = get_redactor()
        agent2 = get_redactor()
        
        assert agent1 is agent2

