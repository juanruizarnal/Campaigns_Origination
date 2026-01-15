"""Pydantic models for Alter-5 Origination Engine.

This module defines all data models used across the application:
- Core entities (Company, BusinessUnit, Contact)
- Campaign entities (Campaign, CampaignTarget, MarketContext)
- FEI evaluation models
- Supporting enums and types
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ==============================================================================
# ENUMS - FEI
# ==============================================================================

class FEIStatus(str, Enum):
    """Status of FEI eligibility evaluation.
    
    Values match exactly the Airtable Select options.
    """
    UNKNOWN = "Unknown"
    PENDING_REVIEW = "Pending_Review"
    ELIGIBLE = "Eligible"
    NOT_ELIGIBLE = "Not_Eligible"
    PARTIALLY_ELIGIBLE = "Partially_Eligible"
    EXPIRED = "Expired"


class FEICriteria(str, Enum):
    """FEI eligibility criteria codes.
    
    A company is eligible if it meets AT LEAST ONE of these criteria.
    """
    CLEANTECH_PRIZE = "1.1_Cleantech_Prize"
    CLEAN_ENERGY_PATENT = "1.2_Clean_Energy_Patent"
    ECO_LABEL = "1.3_Eco_Label"
    GREEN_BUSINESS_90 = "1.4_Green_Business_90"
    GREEN_BUSINESS_MODEL = "1.5_Green_Business_Model"
    ENVIRONMENTAL_CERTIFICATE = "1.6_Environmental_Certificate"


# ==============================================================================
# ENUMS - CAMPAIGNS
# ==============================================================================

class CampaignStatus(str, Enum):
    """Status of an origination campaign."""
    DRAFT = "Draft"
    PENDING_REVIEW = "Pending_Review"
    APPROVED = "Approved"
    SCHEDULED = "Scheduled"
    ACTIVE = "Active"
    PAUSED = "Paused"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class CampaignSize(str, Enum):
    """Size/type of campaign targeting."""
    MASSIVE = "Massive"
    MICRO_TARGETING = "Micro-Targeting"
    PERSONAL = "Personal"


class CampaignPriority(str, Enum):
    """Priority level of a campaign."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class ProductLine(str, Enum):
    """Alter-5 product lines."""
    CORPORATE_DEBT = "Corporate_Debt"
    PROJECT_FINANCE = "Project_Finance"
    MA_ADVISORY = "M&A_Advisory"
    FEI_GUARANTEE = "FEI_Guarantee"
    REFINANCING = "Refinancing"
    BRIDGE_LOAN = "Bridge_Loan"


# ==============================================================================
# ENUMS - CAMPAIGN TARGETS
# ==============================================================================

class TargetStatus(str, Enum):
    """Status of a campaign target."""
    PENDING_REVIEW = "Pending_Review"
    APPROVED = "Approved"
    SCHEDULED = "Scheduled"
    SENT = "Sent"
    DELIVERED = "Delivered"
    OPENED = "Opened"
    CLICKED = "Clicked"
    REPLIED = "Replied"
    MEETING_SCHEDULED = "Meeting_Scheduled"
    CONVERTED = "Converted"
    BOUNCED = "Bounced"
    UNSUBSCRIBED = "Unsubscribed"
    REJECTED = "Rejected"


# ==============================================================================
# ENUMS - MARKET CONTEXT
# ==============================================================================

class ContextType(str, Enum):
    """Type of market context/trigger."""
    NEWS_SECTORAL = "News_Sectoral"
    REGULATORY_CHANGE = "Regulatory_Change"
    MA_MOVEMENT = "M&A_Movement"
    EARNINGS_REPORT = "Earnings_Report"
    FUNDING_ROUND = "Funding_Round"
    LEADERSHIP_CHANGE = "Leadership_Change"
    MARKET_TREND = "Market_Trend"
    POLICY_ANNOUNCEMENT = "Policy_Announcement"
    INDUSTRY_EVENT = "Industry_Event"
    OTHER = "Other"


class ContextStatus(str, Enum):
    """Processing status of market context."""
    NEW = "New"
    ANALYZED = "Analyzed"
    CAMPAIGN_CREATED = "Campaign_Created"
    ARCHIVED = "Archived"
    DISCARDED = "Discarded"


# ==============================================================================
# ENUMS - OTHER
# ==============================================================================

class RecordStatus(str, Enum):
    """Status of a business unit record."""
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class FocusRegion(str, Enum):
    """Geographic focus regions."""
    AMER = "AMER"
    EMEA = "EMEA"
    APAC = "APAC"


class KeyPerson(str, Enum):
    """Whether a contact is a key person."""
    YES = "Yes"
    NO = "No"


class CertificateType(str, Enum):
    """Type of certificate."""
    ISO = "ISO"
    ECO_LABEL = "Eco-label"
    PRIZE = "Prize"
    PI = "PI"


class CertificateStatus(str, Enum):
    """Status of a certificate."""
    ACTIVE = "Active"
    EXPIRED = "Expired"
    PENDING_RENEWAL = "Pending_Renewal"
    REVOKED = "Revoked"
    UNDER_REVIEW = "Under_Review"


# ==============================================================================
# BASE MODELS
# ==============================================================================

class AirtableRecord(BaseModel):
    """Base model for Airtable records."""
    id: str = Field(..., description="Airtable record ID (recXXX)")
    created_time: Optional[datetime] = Field(None, description="Record creation timestamp")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        populate_by_name = True


# ==============================================================================
# STAKEHOLDER MODELS
# ==============================================================================

class Company(BaseModel):
    """Company (Stakeholder) entity.
    
    Represents a company in the Airtable database with all relevant fields
    for origination and FEI evaluation.
    """
    id: str = Field(..., description="Airtable record ID")
    name: str = Field(..., description="Company name")
    home_url: Optional[str] = Field(None, description="Company website URL")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    description: Optional[str] = Field(None, description="Company description")
    num_employees: Optional[int] = Field(None, ge=0, description="Number of employees")
    
    # Location
    hq_country: Optional[str] = Field(None, description="HQ country (record ID or name)")
    hq_address: Optional[str] = Field(None, description="HQ address")
    tax_id: Optional[str] = Field(None, description="Tax identification number")
    
    # FEI Evaluation (CRITICAL)
    fei_status: FEIStatus = Field(FEIStatus.UNKNOWN, description="FEI eligibility status")
    fei_criteria_met: list[FEICriteria] = Field(
        default_factory=list,
        description="List of FEI criteria met",
    )
    fei_confidence: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Confidence score (0-100%)",
    )
    fei_last_check: Optional[date] = Field(None, description="Last FEI evaluation date")
    fei_notes: Optional[str] = Field(None, description="FEI evaluation notes")
    
    # Traceability
    source: Optional[list[str]] = Field(None, description="Data sources")
    
    @classmethod
    def from_airtable(cls, record: dict) -> "Company":
        """Create Company from Airtable record.
        
        Args:
            record: Raw Airtable record dict
            
        Returns:
            Company instance
        """
        fields = record.get("fields", {})
        
        # Parse FEI criteria
        fei_criteria = []
        raw_criteria = fields.get("FEI_Criteria_Met", [])
        for c in raw_criteria:
            try:
                fei_criteria.append(FEICriteria(c))
            except ValueError:
                pass  # Skip unknown criteria
        
        # Parse FEI status
        raw_status = fields.get("FEI_Status", "Unknown")
        try:
            fei_status = FEIStatus(raw_status)
        except ValueError:
            fei_status = FEIStatus.UNKNOWN
        
        return cls(
            id=record["id"],
            name=fields.get("Company Name", ""),
            home_url=fields.get("Home URL"),
            linkedin_url=fields.get("Linkedin URL"),
            description=fields.get("Description"),
            num_employees=fields.get("Num Employees"),
            hq_address=fields.get("HQ Address"),
            tax_id=fields.get("Tax ID"),
            fei_status=fei_status,
            fei_criteria_met=fei_criteria,
            fei_confidence=fields.get("FEI_Confidence"),
            fei_last_check=fields.get("FEI_Last_Check"),
            fei_notes=fields.get("FEI_Notes"),
            source=fields.get("Source"),
        )
    
    def to_airtable_fields(self) -> dict:
        """Convert to Airtable fields dict for update/create.
        
        Returns:
            Dict with field names and values
        """
        fields = {}
        
        if self.name:
            fields["Company Name"] = self.name
        if self.home_url:
            fields["Home URL"] = self.home_url
        if self.linkedin_url:
            fields["Linkedin URL"] = self.linkedin_url
        if self.description:
            fields["Description"] = self.description
        if self.num_employees is not None:
            fields["Num Employees"] = self.num_employees
        if self.hq_address:
            fields["HQ Address"] = self.hq_address
        if self.tax_id:
            fields["Tax ID"] = self.tax_id
        
        # FEI fields
        fields["FEI_Status"] = self.fei_status.value
        if self.fei_criteria_met:
            fields["FEI_Criteria_Met"] = [c.value for c in self.fei_criteria_met]
        if self.fei_confidence is not None:
            fields["FEI_Confidence"] = self.fei_confidence / 100  # Airtable percent
        if self.fei_last_check:
            fields["FEI_Last_Check"] = self.fei_last_check.isoformat()
        if self.fei_notes:
            fields["FEI_Notes"] = self.fei_notes
        
        return fields


class BusinessUnit(BaseModel):
    """Business Unit entity.
    
    Business Units are the actual targets for campaigns.
    They represent a specific division/team within a company.
    """
    id: str = Field(..., description="Airtable record ID")
    name: str = Field(..., description="Business unit name")
    company_id: str = Field(..., description="Parent company record ID")
    
    # Classification
    sector: Optional[str] = Field(None, description="Sector")
    record_status: RecordStatus = Field(RecordStatus.ACTIVE, description="Active/Inactive")
    focus_regions: list[FocusRegion] = Field(default_factory=list, description="Focus regions")
    
    # Cooling-off (CRITICAL for campaign targeting)
    last_outreach_date: Optional[date] = Field(None, description="Last campaign contact date")
    is_in_cooling_off: bool = Field(False, description="True if <90 days since last contact")
    revenue_percentage: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="% of company revenue (for FEI 1.4 criterion)",
    )
    
    @classmethod
    def from_airtable(cls, record: dict) -> "BusinessUnit":
        """Create BusinessUnit from Airtable record."""
        fields = record.get("fields", {})
        
        # Parse focus regions
        regions = []
        for r in fields.get("Focus Region", []):
            try:
                regions.append(FocusRegion(r))
            except ValueError:
                pass
        
        # Parse status
        try:
            status = RecordStatus(fields.get("Record Status", "Active"))
        except ValueError:
            status = RecordStatus.ACTIVE
        
        # Get company ID from link field
        company_links = fields.get("Company", [])
        company_id = company_links[0] if company_links else ""
        
        return cls(
            id=record["id"],
            name=fields.get("Business Unit Name", ""),
            company_id=company_id,
            sector=fields.get("Sector_Names"),
            record_status=status,
            focus_regions=regions,
            last_outreach_date=fields.get("Last_Outreach_Date"),
            is_in_cooling_off=fields.get("Is_In_Cooling_Off", False),
            revenue_percentage=fields.get("Revenue_Percentage"),
        )


class Contact(BaseModel):
    """Contact (person) entity.
    
    Contacts are the actual recipients of campaign emails.
    """
    id: str = Field(..., description="Airtable record ID")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    full_name: Optional[str] = Field(None, description="Full name (computed)")
    email: Optional[str] = Field(None, description="Email address")
    phone_number: Optional[str] = Field(None, description="Phone number")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn URL")
    role: Optional[str] = Field(None, description="Job role/title")
    key_person: KeyPerson = Field(KeyPerson.NO, description="Is key decision maker")
    
    # Relations
    business_unit_ids: list[str] = Field(
        default_factory=list,
        description="Business unit record IDs",
    )
    
    @classmethod
    def from_airtable(cls, record: dict) -> "Contact":
        """Create Contact from Airtable record."""
        fields = record.get("fields", {})
        
        # Parse key person
        try:
            key_person = KeyPerson(fields.get("Key Person", "No"))
        except ValueError:
            key_person = KeyPerson.NO
        
        return cls(
            id=record["id"],
            first_name=fields.get("First Name"),
            last_name=fields.get("Last Name"),
            full_name=fields.get("Full Name"),
            email=fields.get("Email"),
            phone_number=fields.get("Phoner Number"),  # Note: typo in Airtable
            linkedin_url=fields.get("Linkedin URL"),
            role=fields.get("Role"),
            key_person=key_person,
            business_unit_ids=fields.get("Business Unit", []),
        )


# ==============================================================================
# CAMPAIGN MODELS
# ==============================================================================

class MarketContext(BaseModel):
    """Market context (trigger) for campaigns.
    
    Represents market events, news, or triggers that can
    be used to create targeted campaigns.
    """
    id: Optional[str] = Field(None, description="Airtable record ID")
    context_title: str = Field(..., description="Title of the context/trigger")
    context_type: ContextType = Field(ContextType.OTHER, description="Type of context")
    source_url: Optional[str] = Field(None, description="Source URL")
    source_name: Optional[str] = Field(None, description="Source name")
    publication_date: Optional[date] = Field(None, description="Publication date")
    
    # Content
    summary: Optional[str] = Field(None, description="Executive summary")
    key_implications: Optional[str] = Field(None, description="Key implications")
    
    # Assessment
    campaign_potential: Optional[int] = Field(
        None,
        ge=1,
        le=5,
        description="Campaign potential rating (1-5)",
    )
    status: ContextStatus = Field(ContextStatus.NEW, description="Processing status")
    tags: list[str] = Field(default_factory=list, description="Tags for filtering")
    
    # Relations
    affected_sector_ids: list[str] = Field(
        default_factory=list,
        description="Affected sector record IDs",
    )
    affected_country_ids: list[str] = Field(
        default_factory=list,
        description="Affected country record IDs",
    )
    
    # Metadata
    ai_generated: bool = Field(False, description="Generated by AI agent")


class Campaign(BaseModel):
    """Origination campaign entity.
    
    Represents a marketing campaign targeting multiple Business Units.
    """
    id: Optional[str] = Field(None, description="Airtable record ID")
    campaign_name: str = Field(..., description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    campaign_size: CampaignSize = Field(CampaignSize.MICRO_TARGETING)
    status: CampaignStatus = Field(CampaignStatus.DRAFT)
    product_lines: list[ProductLine] = Field(default_factory=list)
    priority: CampaignPriority = Field(CampaignPriority.MEDIUM)
    
    # Scheduling
    scheduled_start_date: Optional[date] = Field(None)
    scheduled_end_date: Optional[date] = Field(None)
    
    # Content
    campaign_rationale: Optional[str] = Field(None, description="Why this campaign")
    email_subject_template_es: Optional[str] = Field(None)
    email_body_template_es: Optional[str] = Field(None)
    
    # Targeting
    target_ticket_min: Optional[float] = Field(None, ge=0)
    target_ticket_max: Optional[float] = Field(None, ge=0)
    
    # Relations
    market_context_ids: list[str] = Field(default_factory=list)
    target_sector_ids: list[str] = Field(default_factory=list)
    target_country_ids: list[str] = Field(default_factory=list)
    
    # Metadata
    ai_generated: bool = Field(False)
    notes: Optional[str] = Field(None)


class CampaignTarget(BaseModel):
    """Campaign target entity.
    
    Represents a specific Business Unit selected for a campaign,
    including the personalized message.
    """
    id: Optional[str] = Field(None, description="Airtable record ID")
    target_name: Optional[str] = Field(None, description="Target identifier")
    
    # Selection
    selection_justification: Optional[str] = Field(
        None,
        description="Why this target was selected",
    )
    personalization_context: Optional[str] = Field(
        None,
        description="Context used for personalization",
    )
    
    # Email content (CRITICAL)
    personalized_email_subject: Optional[str] = Field(None, description="Email subject")
    personalized_email_body: Optional[str] = Field(None, description="Email body (≤150 words)")
    
    # Scoring
    fit_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Fit score (0-100%)",
    )
    ai_confidence: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="AI confidence (0-100%)",
    )
    
    # Status
    status: TargetStatus = Field(TargetStatus.PENDING_REVIEW)
    sent_date: Optional[datetime] = Field(None)
    last_interaction_date: Optional[datetime] = Field(None)
    response_summary: Optional[str] = Field(None)
    
    # Follow-up
    follow_up_required: bool = Field(False)
    follow_up_notes: Optional[str] = Field(None)
    
    # Override
    manual_override: bool = Field(False, description="Modified by human")
    override_notes: Optional[str] = Field(None)
    
    # Relations
    campaign_id: str = Field(..., description="Parent campaign record ID")
    business_unit_id: str = Field(..., description="Target business unit record ID")
    contact_id: Optional[str] = Field(None, description="Contact record ID")
    
    @field_validator("personalized_email_body")
    @classmethod
    def validate_email_length(cls, v: Optional[str]) -> Optional[str]:
        """Validate email body length (max 150 words)."""
        if v is not None:
            word_count = len(v.split())
            if word_count > 150:
                raise ValueError(f"Email body exceeds 150 words (has {word_count})")
        return v


# ==============================================================================
# FEI EVALUATION MODELS
# ==============================================================================

class FEIEvaluation(BaseModel):
    """Result of FEI eligibility evaluation.
    
    Used by the EvaluadorFEI agent to return evaluation results.
    """
    company_id: str = Field(..., description="Company record ID")
    status: FEIStatus = Field(..., description="Determined FEI status")
    criteria_met: list[FEICriteria] = Field(
        default_factory=list,
        description="List of criteria met",
    )
    confidence: float = Field(
        ...,
        ge=0,
        le=100,
        description="Confidence score (0-100%)",
    )
    reasoning: str = Field(..., description="Explanation of evaluation")
    certificates_found: list[str] = Field(
        default_factory=list,
        description="Certificates/certifications found",
    )
    evidence_urls: list[str] = Field(
        default_factory=list,
        description="URLs of evidence found",
    )
    evaluation_date: date = Field(
        default_factory=date.today,
        description="Date of evaluation",
    )
    
    def is_eligible(self) -> bool:
        """Check if company is FEI eligible."""
        return self.status == FEIStatus.ELIGIBLE
    
    def needs_review(self) -> bool:
        """Check if evaluation needs human review."""
        return self.status == FEIStatus.PENDING_REVIEW or self.confidence < 70


# ==============================================================================
# SEARCH AND SELECTION MODELS
# ==============================================================================

class SearchCriteria(BaseModel):
    """Criteria for company search (Agente 1: Buscador)."""
    sector: Optional[str] = Field(None, description="Target sector")
    country: Optional[str] = Field(None, description="Target country")
    region: Optional[str] = Field(None, description="Target region")
    min_employees: Optional[int] = Field(None, ge=1)
    max_employees: Optional[int] = Field(None, ge=1)
    keywords: list[str] = Field(default_factory=list)
    limit: int = Field(25, ge=1, le=100, description="Max results")


class SelectionResult(BaseModel):
    """Result of target selection (Agente 5: Selector)."""
    business_unit_id: str
    company_name: str
    fit_score: float = Field(ge=0, le=100)
    selection_justification: str
    fei_eligible: bool = False
    has_key_person: bool = False
    sector_match: bool = False
    country_match: bool = False
    has_financials: bool = False


# ==============================================================================
# EMAIL GENERATION MODELS
# ==============================================================================

class EmailDraft(BaseModel):
    """Draft email generated by Agente 6: Redactor."""
    target_id: str = Field(..., description="CampaignTarget record ID")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body")
    word_count: int = Field(..., ge=0)
    mentions_company: bool = Field(..., description="Body mentions company name")
    has_cta: bool = Field(..., description="Body has call-to-action")
    mentions_fei: bool = Field(False, description="Mentions FEI guarantee if eligible")
    
    @field_validator("body")
    @classmethod
    def validate_body_length(cls, v: str) -> str:
        """Ensure body is ≤150 words."""
        word_count = len(v.split())
        if word_count > 150:
            raise ValueError(f"Email body exceeds 150 words (has {word_count})")
        return v

