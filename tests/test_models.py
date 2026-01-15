"""Tests for Pydantic models."""

from datetime import date, datetime

import pytest
from pydantic import ValidationError

from core.models import (
    # Enums
    FEIStatus,
    FEICriteria,
    CampaignStatus,
    CampaignSize,
    CampaignPriority,
    ProductLine,
    TargetStatus,
    ContextType,
    ContextStatus,
    RecordStatus,
    FocusRegion,
    KeyPerson,
    # Models
    Company,
    BusinessUnit,
    Contact,
    MarketContext,
    Campaign,
    CampaignTarget,
    FEIEvaluation,
    SearchCriteria,
    SelectionResult,
    EmailDraft,
)


class TestFEIEnums:
    """Test FEI-related enums."""
    
    def test_fei_status_values(self) -> None:
        """Test all FEI status values exist."""
        assert FEIStatus.UNKNOWN.value == "Unknown"
        assert FEIStatus.PENDING_REVIEW.value == "Pending_Review"
        assert FEIStatus.ELIGIBLE.value == "Eligible"
        assert FEIStatus.NOT_ELIGIBLE.value == "Not_Eligible"
        assert FEIStatus.PARTIALLY_ELIGIBLE.value == "Partially_Eligible"
        assert FEIStatus.EXPIRED.value == "Expired"
    
    def test_fei_criteria_values(self) -> None:
        """Test all FEI criteria values exist."""
        assert FEICriteria.CLEANTECH_PRIZE.value == "1.1_Cleantech_Prize"
        assert FEICriteria.CLEAN_ENERGY_PATENT.value == "1.2_Clean_Energy_Patent"
        assert FEICriteria.ECO_LABEL.value == "1.3_Eco_Label"
        assert FEICriteria.GREEN_BUSINESS_90.value == "1.4_Green_Business_90"
        assert FEICriteria.GREEN_BUSINESS_MODEL.value == "1.5_Green_Business_Model"
        assert FEICriteria.ENVIRONMENTAL_CERTIFICATE.value == "1.6_Environmental_Certificate"


class TestCampaignEnums:
    """Test campaign-related enums."""
    
    def test_campaign_status_values(self) -> None:
        """Test all campaign status values exist."""
        assert len(CampaignStatus) == 8
        assert CampaignStatus.DRAFT.value == "Draft"
        assert CampaignStatus.ACTIVE.value == "Active"
        assert CampaignStatus.COMPLETED.value == "Completed"
    
    def test_campaign_size_values(self) -> None:
        """Test campaign size values."""
        assert CampaignSize.MASSIVE.value == "Massive"
        assert CampaignSize.MICRO_TARGETING.value == "Micro-Targeting"
        assert CampaignSize.PERSONAL.value == "Personal"
    
    def test_campaign_priority_values(self) -> None:
        """Test campaign priority values."""
        assert CampaignPriority.CRITICAL.value == "Critical"
        assert CampaignPriority.HIGH.value == "High"
        assert CampaignPriority.MEDIUM.value == "Medium"
        assert CampaignPriority.LOW.value == "Low"
    
    def test_product_line_values(self) -> None:
        """Test product line values."""
        assert ProductLine.CORPORATE_DEBT.value == "Corporate_Debt"
        assert ProductLine.FEI_GUARANTEE.value == "FEI_Guarantee"
        assert ProductLine.MA_ADVISORY.value == "M&A_Advisory"


class TestTargetEnums:
    """Test target-related enums."""
    
    def test_target_status_values(self) -> None:
        """Test all target status values exist."""
        assert len(TargetStatus) == 13
        assert TargetStatus.PENDING_REVIEW.value == "Pending_Review"
        assert TargetStatus.SENT.value == "Sent"
        assert TargetStatus.CONVERTED.value == "Converted"
        assert TargetStatus.BOUNCED.value == "Bounced"


class TestContextEnums:
    """Test context-related enums."""
    
    def test_context_type_values(self) -> None:
        """Test context type values."""
        assert len(ContextType) == 10
        assert ContextType.NEWS_SECTORAL.value == "News_Sectoral"
        assert ContextType.MA_MOVEMENT.value == "M&A_Movement"
        assert ContextType.REGULATORY_CHANGE.value == "Regulatory_Change"
    
    def test_context_status_values(self) -> None:
        """Test context status values."""
        assert len(ContextStatus) == 5
        assert ContextStatus.NEW.value == "New"
        assert ContextStatus.CAMPAIGN_CREATED.value == "Campaign_Created"


class TestCompanyModel:
    """Test Company model."""
    
    def test_company_minimal(self) -> None:
        """Test company with minimal fields."""
        company = Company(
            id="recTest123",
            name="Test Corp",
        )
        assert company.id == "recTest123"
        assert company.name == "Test Corp"
        assert company.fei_status == FEIStatus.UNKNOWN
        assert company.fei_criteria_met == []
    
    def test_company_full(self) -> None:
        """Test company with all fields."""
        company = Company(
            id="recTest123",
            name="Green Corp",
            home_url="https://greencorp.com",
            linkedin_url="https://linkedin.com/company/greencorp",
            description="A green company",
            num_employees=500,
            hq_country="Spain",
            hq_address="Madrid, Spain",
            tax_id="B12345678",
            fei_status=FEIStatus.ELIGIBLE,
            fei_criteria_met=[FEICriteria.ENVIRONMENTAL_CERTIFICATE, FEICriteria.ECO_LABEL],
            fei_confidence=85.0,
            fei_last_check=date(2024, 1, 15),
            fei_notes="ISO 14001 certified",
            source=["Research", "LinkedIn"],
        )
        assert company.fei_status == FEIStatus.ELIGIBLE
        assert len(company.fei_criteria_met) == 2
        assert company.fei_confidence == 85.0
    
    def test_company_fei_confidence_validation(self) -> None:
        """Test FEI confidence must be 0-100."""
        with pytest.raises(ValidationError):
            Company(
                id="rec123",
                name="Test",
                fei_confidence=150.0,  # Invalid
            )
    
    def test_company_from_airtable(self) -> None:
        """Test creating company from Airtable record."""
        record = {
            "id": "recAirtable123",
            "fields": {
                "Company Name": "Airtable Corp",
                "Home URL": "https://airtable.com",
                "FEI_Status": "Eligible",
                "FEI_Criteria_Met": ["1.1_Cleantech_Prize", "1.6_Environmental_Certificate"],
                "FEI_Confidence": 0.9,
                "Description": "A tech company",
            },
        }
        
        company = Company.from_airtable(record)
        
        assert company.id == "recAirtable123"
        assert company.name == "Airtable Corp"
        assert company.fei_status == FEIStatus.ELIGIBLE
        assert FEICriteria.CLEANTECH_PRIZE in company.fei_criteria_met
        assert FEICriteria.ENVIRONMENTAL_CERTIFICATE in company.fei_criteria_met
    
    def test_company_from_airtable_unknown_status(self) -> None:
        """Test handling unknown FEI status gracefully."""
        record = {
            "id": "rec123",
            "fields": {
                "Company Name": "Test Corp",
                "FEI_Status": "InvalidStatus",
            },
        }
        
        company = Company.from_airtable(record)
        assert company.fei_status == FEIStatus.UNKNOWN
    
    def test_company_to_airtable_fields(self) -> None:
        """Test converting company to Airtable fields."""
        company = Company(
            id="rec123",
            name="Test Corp",
            fei_status=FEIStatus.ELIGIBLE,
            fei_criteria_met=[FEICriteria.ECO_LABEL],
            fei_confidence=80.0,
            fei_last_check=date(2024, 1, 1),
            fei_notes="Test notes",
        )
        
        fields = company.to_airtable_fields()
        
        assert fields["Company Name"] == "Test Corp"
        assert fields["FEI_Status"] == "Eligible"
        assert fields["FEI_Criteria_Met"] == ["1.3_Eco_Label"]
        assert fields["FEI_Confidence"] == 0.8  # Converted to percent
        assert fields["FEI_Last_Check"] == "2024-01-01"
        assert fields["FEI_Notes"] == "Test notes"


class TestBusinessUnitModel:
    """Test BusinessUnit model."""
    
    def test_business_unit_minimal(self) -> None:
        """Test business unit with minimal fields."""
        bu = BusinessUnit(
            id="recBU123",
            name="Sales Division",
            company_id="recCompany123",
        )
        assert bu.id == "recBU123"
        assert bu.name == "Sales Division"
        assert bu.is_in_cooling_off is False
        assert bu.record_status == RecordStatus.ACTIVE
    
    def test_business_unit_cooling_off(self) -> None:
        """Test business unit with cooling-off fields."""
        bu = BusinessUnit(
            id="recBU123",
            name="Sales Division",
            company_id="recCompany123",
            last_outreach_date=date(2024, 1, 1),
            is_in_cooling_off=True,
            revenue_percentage=95.0,
        )
        assert bu.is_in_cooling_off is True
        assert bu.revenue_percentage == 95.0
    
    def test_business_unit_from_airtable(self) -> None:
        """Test creating business unit from Airtable record."""
        record = {
            "id": "recBU123",
            "fields": {
                "Business Unit Name": "Tech Division",
                "Company": ["recCompany123"],
                "Focus Region": ["EMEA", "AMER"],
                "Record Status": "Active",
                "Is_In_Cooling_Off": True,
            },
        }
        
        bu = BusinessUnit.from_airtable(record)
        
        assert bu.id == "recBU123"
        assert bu.name == "Tech Division"
        assert bu.company_id == "recCompany123"
        assert FocusRegion.EMEA in bu.focus_regions
        assert FocusRegion.AMER in bu.focus_regions
        assert bu.is_in_cooling_off is True


class TestContactModel:
    """Test Contact model."""
    
    def test_contact_minimal(self) -> None:
        """Test contact with minimal fields."""
        contact = Contact(
            id="recContact123",
        )
        assert contact.id == "recContact123"
        assert contact.key_person == KeyPerson.NO
    
    def test_contact_full(self) -> None:
        """Test contact with all fields."""
        contact = Contact(
            id="recContact123",
            first_name="John",
            last_name="Doe",
            full_name="John Doe",
            email="john.doe@company.com",
            phone_number="+34123456789",
            linkedin_url="https://linkedin.com/in/johndoe",
            role="CFO",
            key_person=KeyPerson.YES,
            business_unit_ids=["recBU1", "recBU2"],
        )
        assert contact.full_name == "John Doe"
        assert contact.key_person == KeyPerson.YES
        assert len(contact.business_unit_ids) == 2


class TestMarketContextModel:
    """Test MarketContext model."""
    
    def test_market_context_minimal(self) -> None:
        """Test market context with minimal fields."""
        ctx = MarketContext(context_title="New Regulation")
        assert ctx.context_title == "New Regulation"
        assert ctx.context_type == ContextType.OTHER
        assert ctx.status == ContextStatus.NEW
    
    def test_market_context_full(self) -> None:
        """Test market context with all fields."""
        ctx = MarketContext(
            id="recContext123",
            context_title="EU Green Deal Update",
            context_type=ContextType.REGULATORY_CHANGE,
            source_url="https://ec.europa.eu/greendeal",
            source_name="European Commission",
            publication_date=date(2024, 1, 15),
            summary="New sustainability requirements",
            key_implications="Companies must adapt",
            campaign_potential=5,
            status=ContextStatus.ANALYZED,
            tags=["ESG", "Renewables"],
            affected_sector_ids=["recSector1"],
            affected_country_ids=["recSpain", "recFrance"],
            ai_generated=True,
        )
        assert ctx.campaign_potential == 5
        assert ctx.ai_generated is True
    
    def test_market_context_campaign_potential_validation(self) -> None:
        """Test campaign potential must be 1-5."""
        with pytest.raises(ValidationError):
            MarketContext(
                context_title="Test",
                campaign_potential=10,  # Invalid
            )


class TestCampaignModel:
    """Test Campaign model."""
    
    def test_campaign_minimal(self) -> None:
        """Test campaign with minimal fields."""
        campaign = Campaign(campaign_name="Q1 Outreach")
        assert campaign.campaign_name == "Q1 Outreach"
        assert campaign.status == CampaignStatus.DRAFT
        assert campaign.campaign_size == CampaignSize.MICRO_TARGETING
        assert campaign.priority == CampaignPriority.MEDIUM
    
    def test_campaign_full(self) -> None:
        """Test campaign with all fields."""
        campaign = Campaign(
            id="recCampaign123",
            campaign_name="Green Finance Q1",
            description="Target green companies",
            campaign_size=CampaignSize.MASSIVE,
            status=CampaignStatus.APPROVED,
            product_lines=[ProductLine.FEI_GUARANTEE, ProductLine.PROJECT_FINANCE],
            priority=CampaignPriority.HIGH,
            scheduled_start_date=date(2024, 2, 1),
            scheduled_end_date=date(2024, 3, 31),
            campaign_rationale="Focus on FEI-eligible companies",
            email_subject_template_es="Oportunidad de financiación verde",
            email_body_template_es="Estimado {nombre}, ...",
            target_ticket_min=1_000_000,
            target_ticket_max=10_000_000,
            ai_generated=True,
        )
        assert campaign.status == CampaignStatus.APPROVED
        assert ProductLine.FEI_GUARANTEE in campaign.product_lines
        assert campaign.target_ticket_min == 1_000_000


class TestCampaignTargetModel:
    """Test CampaignTarget model."""
    
    def test_campaign_target_minimal(self) -> None:
        """Test campaign target with minimal fields."""
        target = CampaignTarget(
            campaign_id="recCampaign123",
            business_unit_id="recBU123",
        )
        assert target.campaign_id == "recCampaign123"
        assert target.status == TargetStatus.PENDING_REVIEW
        assert target.follow_up_required is False
        assert target.manual_override is False
    
    def test_campaign_target_full(self) -> None:
        """Test campaign target with all fields."""
        target = CampaignTarget(
            id="recTarget123",
            target_name="Green Corp - Sales",
            campaign_id="recCampaign123",
            business_unit_id="recBU123",
            contact_id="recContact123",
            selection_justification="FEI eligible, matching sector",
            personalization_context="Recent funding round",
            personalized_email_subject="Opportunity for Green Corp",
            personalized_email_body="Dear John, we noticed your recent expansion...",
            fit_score=85.0,
            ai_confidence=90.0,
            status=TargetStatus.APPROVED,
        )
        assert target.fit_score == 85.0
        assert target.ai_confidence == 90.0
    
    def test_campaign_target_email_body_validation(self) -> None:
        """Test email body max 150 words."""
        # 151 words should fail
        long_body = " ".join(["word"] * 151)
        
        with pytest.raises(ValidationError) as exc_info:
            CampaignTarget(
                campaign_id="rec123",
                business_unit_id="recBU123",
                personalized_email_body=long_body,
            )
        
        assert "150 words" in str(exc_info.value)
    
    def test_campaign_target_email_body_valid(self) -> None:
        """Test email body at exactly 150 words passes."""
        body_150 = " ".join(["word"] * 150)
        
        target = CampaignTarget(
            campaign_id="rec123",
            business_unit_id="recBU123",
            personalized_email_body=body_150,
        )
        
        assert target.personalized_email_body == body_150


class TestFEIEvaluationModel:
    """Test FEIEvaluation model."""
    
    def test_fei_evaluation_eligible(self) -> None:
        """Test FEI evaluation for eligible company."""
        eval_result = FEIEvaluation(
            company_id="recCompany123",
            status=FEIStatus.ELIGIBLE,
            criteria_met=[FEICriteria.ENVIRONMENTAL_CERTIFICATE],
            confidence=95.0,
            reasoning="ISO 14001 certification verified",
            certificates_found=["ISO 14001:2015"],
            evidence_urls=["https://company.com/certificates"],
        )
        
        assert eval_result.is_eligible() is True
        assert eval_result.needs_review() is False
    
    def test_fei_evaluation_pending_review(self) -> None:
        """Test FEI evaluation needing review."""
        eval_result = FEIEvaluation(
            company_id="recCompany123",
            status=FEIStatus.PENDING_REVIEW,
            confidence=60.0,
            reasoning="Possible eco-label found, needs verification",
        )
        
        assert eval_result.is_eligible() is False
        assert eval_result.needs_review() is True
    
    def test_fei_evaluation_low_confidence_needs_review(self) -> None:
        """Test that low confidence triggers review even if eligible."""
        eval_result = FEIEvaluation(
            company_id="recCompany123",
            status=FEIStatus.ELIGIBLE,
            criteria_met=[FEICriteria.GREEN_BUSINESS_MODEL],
            confidence=50.0,  # Below 70% threshold
            reasoning="Business model appears green but uncertain",
        )
        
        assert eval_result.is_eligible() is True
        assert eval_result.needs_review() is True  # Due to low confidence


class TestSearchCriteriaModel:
    """Test SearchCriteria model."""
    
    def test_search_criteria_defaults(self) -> None:
        """Test search criteria with defaults."""
        criteria = SearchCriteria()
        assert criteria.limit == 25
        assert criteria.keywords == []
    
    def test_search_criteria_full(self) -> None:
        """Test search criteria with all fields."""
        criteria = SearchCriteria(
            sector="Renewable Energy",
            country="Spain",
            region="EMEA",
            min_employees=50,
            max_employees=500,
            keywords=["solar", "wind"],
            limit=50,
        )
        assert criteria.sector == "Renewable Energy"
        assert criteria.limit == 50
    
    def test_search_criteria_limit_validation(self) -> None:
        """Test limit must be 1-100."""
        with pytest.raises(ValidationError):
            SearchCriteria(limit=150)


class TestSelectionResultModel:
    """Test SelectionResult model."""
    
    def test_selection_result(self) -> None:
        """Test selection result model."""
        result = SelectionResult(
            business_unit_id="recBU123",
            company_name="Green Corp",
            fit_score=87.5,
            selection_justification="Perfect match for FEI campaign",
            fei_eligible=True,
            has_key_person=True,
            sector_match=True,
            country_match=True,
            has_financials=True,
        )
        
        assert result.fit_score == 87.5
        assert result.fei_eligible is True
    
    def test_selection_result_fit_score_validation(self) -> None:
        """Test fit score must be 0-100."""
        with pytest.raises(ValidationError):
            SelectionResult(
                business_unit_id="rec123",
                company_name="Test",
                fit_score=150.0,  # Invalid
                selection_justification="Test",
            )


class TestEmailDraftModel:
    """Test EmailDraft model."""
    
    def test_email_draft_valid(self) -> None:
        """Test valid email draft."""
        draft = EmailDraft(
            target_id="recTarget123",
            subject="Financing opportunity",
            body="Dear John, we are reaching out about a unique opportunity...",
            word_count=12,
            mentions_company=True,
            has_cta=True,
            mentions_fei=True,
        )
        
        assert draft.subject == "Financing opportunity"
        assert draft.has_cta is True
    
    def test_email_draft_body_validation(self) -> None:
        """Test email body max 150 words."""
        long_body = " ".join(["word"] * 151)
        
        with pytest.raises(ValidationError) as exc_info:
            EmailDraft(
                target_id="rec123",
                subject="Test",
                body=long_body,
                word_count=151,
                mentions_company=True,
                has_cta=True,
            )
        
        assert "150 words" in str(exc_info.value)

