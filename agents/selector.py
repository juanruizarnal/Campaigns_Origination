"""Agente Selector de Targets for Alter-5 Origination Engine.

This module implements the SelectorTargets agent (Agent 5) which selects
and prioritizes the best Business Units for origination campaigns.

The agent can:
- Filter BUs by sector, country, and active status
- Apply cooling-off period checks (90 days)
- Calculate fit scores based on multiple factors
- Generate selection justifications using Claude
- Limit targets to max 30 per campaign

Usage:
    from agents.selector import SelectorTargets
    
    agent = SelectorTargets()
    targets = agent.select(
        campaign_id="recXXX",
        affected_sectors=["Industrials", "Renewables"],
        affected_countries=["ES", "PT"],
    )
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Optional
import uuid

import structlog

from config.settings import get_settings
from config.airtable_schema import TABLES, COMPANY_FIELDS, BUSINESS_UNIT_FIELDS
from config.prompts import load_prompt
from core.airtable_client import AirtableClient, AirtableError, get_airtable_client
from core.models import BusinessUnit, Company, CampaignTarget
from integrations.claude import ClaudeClient, ClaudeError, get_claude_client

logger = structlog.get_logger()
settings = get_settings()


# ==============================================================================
# CONSTANTS (from settings)
# ==============================================================================

# Get values from settings
COOLING_OFF_DAYS = settings.COOLING_OFF_DAYS
MAX_TARGETS_PER_CAMPAIGN = settings.MAX_TARGETS_PER_CAMPAIGN
MIN_FIT_SCORE = settings.MIN_FIT_SCORE

# Fit score weights - Enhanced FEI prioritization per PRD requirements
SCORE_WEIGHTS = {
    "fei_eligible": 0.20,          # +20% if FEI eligible
    "fei_has_certificates": 0.10,  # +10% if has green certificates
    "key_person_identified": 0.15,  # +15% if key person exists
    "sector_match": 0.15,          # +15% if sector matches
    "country_match": 0.08,         # +8% if country matches
    "financials_complete": 0.08,   # +8% if financials available
    "positive_engagement": 0.10,   # +10% if positive previous engagement
    "linkedin_data": 0.07,         # +7% if LinkedIn data available
    "recent_activity": 0.05,       # +5% if recent company activity
    "base": 0.50,                  # Base score 50%
}


# ==============================================================================
# DATA CLASSES
# ==============================================================================

@dataclass
class TargetCandidate:
    """A candidate Business Unit for campaign targeting."""
    business_unit_id: str
    business_unit_name: str
    company_id: str
    company_name: str
    sector: Optional[str] = None
    country: Optional[str] = None
    fei_status: str = "Unknown"
    fei_criteria_met: list[str] = field(default_factory=list)
    fei_certificates: list[str] = field(default_factory=list)
    has_key_person: bool = False
    key_person_name: Optional[str] = None
    key_person_role: Optional[str] = None
    key_person_linkedin: Optional[str] = None
    contact_id: Optional[str] = None
    has_financials: bool = False
    has_linkedin_data: bool = False
    linkedin_company_url: Optional[str] = None
    recent_linkedin_posts: list[str] = field(default_factory=list)
    last_outreach_date: Optional[date] = None
    previous_engagement: Optional[str] = None
    company_description: Optional[str] = None
    fit_score: float = 0.0
    score_breakdown: dict = field(default_factory=dict)
    selection_justification: str = ""
    
    def is_in_cooling_off(self) -> bool:
        """Check if BU is in cooling-off period."""
        if self.last_outreach_date is None:
            return False
        days_since = (date.today() - self.last_outreach_date).days
        return days_since < COOLING_OFF_DAYS
    
    def days_since_outreach(self) -> Optional[int]:
        """Get days since last outreach."""
        if self.last_outreach_date is None:
            return None
        return (date.today() - self.last_outreach_date).days
    
    def has_green_certificates(self) -> bool:
        """Check if company has relevant green certificates for FEI."""
        green_certs = ["ISO 14001", "ISO 50001", "EMAS", "B Corp", "EcoLabel"]
        return any(
            cert.lower() in c.lower() 
            for c in self.fei_certificates 
            for cert in green_certs
        )


@dataclass
class SelectionResult:
    """Result of target selection process."""
    campaign_id: str
    targets: list[TargetCandidate] = field(default_factory=list)
    excluded_cooling_off: int = 0
    excluded_low_score: int = 0
    excluded_no_sector: int = 0
    total_candidates: int = 0
    processing_time_seconds: float = 0.0
    success: bool = False
    errors: list[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        if not self.success:
            return f"❌ Selection failed: {', '.join(self.errors)}"
        
        return (
            f"✅ Selection for campaign {self.campaign_id}\n"
            f"   Selected: {len(self.targets)}/{self.total_candidates} candidates\n"
            f"   Excluded (cooling-off): {self.excluded_cooling_off}\n"
            f"   Excluded (low score): {self.excluded_low_score}\n"
            f"   Avg fit score: {sum(t.fit_score for t in self.targets)/len(self.targets)*100:.0f}%" if self.targets else "N/A"
        )


# ==============================================================================
# SELECTOR TARGETS AGENT
# ==============================================================================

class SelectorTargets:
    """Agent for selecting and prioritizing campaign targets.
    
    Uses Claude for reasoning about selection justifications.
    Implements business rules:
    - 90-day cooling-off period
    - Max 30 targets per campaign
    - Min 60% fit score
    - FEI eligible companies prioritized
    
    Example:
        agent = SelectorTargets()
        result = agent.select(
            campaign_id="recCampaignXXX",
            affected_sectors=["Industrials", "Renewables"],
            affected_countries=["ES", "PT"],
        )
        
        for target in result.targets:
            print(f"{target.company_name}: {target.fit_score:.0%}")
    """
    
    def __init__(
        self,
        airtable_client: Optional[AirtableClient] = None,
        claude_client: Optional[ClaudeClient] = None,
    ):
        """Initialize the SelectorTargets agent.
        
        Args:
            airtable_client: Optional custom Airtable client
            claude_client: Optional custom Claude client
        """
        self._airtable = airtable_client or get_airtable_client()
        self._claude = claude_client or get_claude_client()
        self._system_prompt = load_prompt("selector")
        
        logger.info("selector_targets_initialized")
    
    def select(
        self,
        campaign_id: str,
        affected_sectors: list[str],
        affected_countries: list[str],
        market_context_summary: Optional[str] = None,
        max_targets: int = MAX_TARGETS_PER_CAMPAIGN,
        min_fit_score: float = MIN_FIT_SCORE,
        include_cooling_off: bool = False,
        prioritize_fei: bool = True,
        dry_run: bool = False,
    ) -> SelectionResult:
        """Select targets for a campaign.
        
        Args:
            campaign_id: The campaign record ID
            affected_sectors: List of sectors to target
            affected_countries: List of countries to target
            market_context_summary: Optional market context for justifications
            max_targets: Maximum number of targets (default 30)
            min_fit_score: Minimum fit score (default 0.6)
            include_cooling_off: If True, don't exclude cooling-off BUs
            dry_run: If True, don't create CampaignTarget records
            
        Returns:
            SelectionResult with selected targets
        """
        start_time = datetime.now()
        task_id = str(uuid.uuid4())[:8]
        
        # Enforce max 30 targets
        max_targets = min(max_targets, MAX_TARGETS_PER_CAMPAIGN)
        
        logger.info(
            "target_selection_started",
            task_id=task_id,
            campaign_id=campaign_id,
            sectors=affected_sectors,
            countries=affected_countries,
            max_targets=max_targets,
            min_fit_score=min_fit_score,
        )
        
        result = SelectionResult(campaign_id=campaign_id)
        
        try:
            # 1. Get candidate BUs matching criteria
            candidates = self._filter_by_criteria(
                affected_sectors=affected_sectors,
                affected_countries=affected_countries,
            )
            result.total_candidates = len(candidates)
            
            logger.info(
                "candidates_filtered",
                task_id=task_id,
                candidates_count=len(candidates),
            )
            
            if not candidates:
                result.errors.append("No candidates found matching criteria")
                return result
            
            # 2. Apply cooling-off filter
            if not include_cooling_off:
                filtered_candidates = []
                for candidate in candidates:
                    if candidate.is_in_cooling_off():
                        result.excluded_cooling_off += 1
                    else:
                        filtered_candidates.append(candidate)
                candidates = filtered_candidates
            
            logger.info(
                "cooling_off_applied",
                task_id=task_id,
                remaining=len(candidates),
                excluded=result.excluded_cooling_off,
            )
            
            if not candidates:
                result.errors.append("All candidates are in cooling-off period")
                return result
            
            # 3. Calculate fit scores
            for candidate in candidates:
                self._calculate_fit_score(
                    candidate=candidate,
                    affected_sectors=affected_sectors,
                    affected_countries=affected_countries,
                    prioritize_fei=prioritize_fei,
                )
            
            # 4. Filter by minimum score
            scored_candidates = []
            for candidate in candidates:
                if candidate.fit_score >= min_fit_score:
                    scored_candidates.append(candidate)
                else:
                    result.excluded_low_score += 1
            
            candidates = scored_candidates
            
            logger.info(
                "scores_calculated",
                task_id=task_id,
                remaining=len(candidates),
                excluded_low=result.excluded_low_score,
            )
            
            if not candidates:
                result.errors.append(f"No candidates meet minimum fit score ({min_fit_score:.0%})")
                return result
            
            # 5. Prioritize and limit
            candidates = self._prioritize(candidates)
            candidates = candidates[:max_targets]
            
            # 6. Generate justifications
            self._generate_justifications(
                candidates=candidates,
                market_context=market_context_summary,
            )
            
            # 7. Save as CampaignTargets
            if not dry_run:
                self._save_targets(
                    campaign_id=campaign_id,
                    candidates=candidates,
                )
            
            result.targets = candidates
            result.success = True
            
        except AirtableError as e:
            logger.error(
                "target_selection_airtable_error",
                task_id=task_id,
                error=str(e),
            )
            result.errors.append(f"Airtable error: {e}")
            
        except ClaudeError as e:
            logger.error(
                "target_selection_claude_error",
                task_id=task_id,
                error=str(e),
            )
            result.errors.append(f"Claude error: {e}")
            
        except Exception as e:
            logger.error(
                "target_selection_unexpected_error",
                task_id=task_id,
                error=str(e),
                exc_info=True,
            )
            result.errors.append(f"Unexpected error: {e}")
        
        result.processing_time_seconds = (datetime.now() - start_time).total_seconds()
        
        logger.info(
            "target_selection_completed",
            task_id=task_id,
            success=result.success,
            targets_selected=len(result.targets),
            processing_time=result.processing_time_seconds,
        )
        
        return result
    
    def _filter_by_criteria(
        self,
        affected_sectors: list[str],
        affected_countries: list[str],
    ) -> list[TargetCandidate]:
        """Filter Business Units by sector, country, and active status.
        
        Args:
            affected_sectors: List of target sectors
            affected_countries: List of target countries
            
        Returns:
            List of TargetCandidate objects
        """
        logger.debug(
            "filtering_by_criteria",
            sectors=affected_sectors,
            countries=affected_countries,
        )
        
        # Build Airtable formula
        # Filter: Record_Status = "Active" AND (Sector in list OR Country in list)
        sector_conditions = [f"{{Sector}}='{s}'" for s in affected_sectors]
        country_conditions = [f"{{Country}}='{c}'" for c in affected_countries]
        
        # Combine with OR for sectors and countries
        filter_parts = []
        if sector_conditions:
            filter_parts.append(f"OR({','.join(sector_conditions)})")
        if country_conditions:
            filter_parts.append(f"OR({','.join(country_conditions)})")
        
        if filter_parts:
            sector_country_filter = f"OR({','.join(filter_parts)})"
        else:
            sector_country_filter = "TRUE()"
        
        formula = f"AND({{Record_Status}}='Active',{sector_country_filter})"
        
        try:
            # Query Business Units
            bu_records = self._airtable.query_records(
                table_name="business_units",
                formula=formula,
                max_records=200,  # Get more than we need for filtering
            )
            
            candidates = []
            
            for bu_record in bu_records:
                bu_fields = bu_record.get("fields", {})
                bu_id = bu_record["id"]
                
                # Get company data
                company_ids = bu_fields.get("Company", [])
                if not company_ids:
                    continue
                
                company_id = company_ids[0]
                
                try:
                    company_record = self._airtable.get_record("companies", company_id)
                    company_fields = company_record.get("fields", {})
                except AirtableError:
                    continue
                
                # Get key person (contact)
                contact_ids = bu_fields.get("Contacts", [])
                key_person = None
                contact_id = None
                
                if contact_ids:
                    try:
                        contact_record = self._airtable.get_record("contacts", contact_ids[0])
                        contact_fields = contact_record.get("fields", {})
                        if contact_fields.get("Key Person") == "Yes":
                            key_person = {
                                "name": f"{contact_fields.get('First Name', '')} {contact_fields.get('Last Name', '')}".strip(),
                                "role": contact_fields.get("Role", ""),
                                "linkedin": contact_fields.get("LinkedIn_URL") or contact_fields.get("linkedin_url"),
                            }
                            contact_id = contact_ids[0]
                    except AirtableError:
                        pass
                
                # Parse last outreach date
                last_outreach = None
                last_outreach_str = bu_fields.get("Last_Outreach_Date")
                if last_outreach_str:
                    try:
                        last_outreach = date.fromisoformat(last_outreach_str.split("T")[0])
                    except ValueError:
                        pass
                
                # Check if has financials
                financials_ids = company_fields.get("Financials", [])
                has_financials = len(financials_ids) > 0
                
                # Check for LinkedIn data
                linkedin_url = company_fields.get("LinkedIn_URL") or company_fields.get("linkedin_url")
                has_linkedin = bool(linkedin_url) or bool(company_fields.get("LinkedIn_Data"))
                
                # Get certificates
                certificates = company_fields.get("Certificates", [])
                if not certificates:
                    # Try to get from Company_Certificates linked table
                    cert_ids = company_fields.get("Company_Certificates", [])
                    if cert_ids:
                        try:
                            for cert_id in cert_ids[:5]:  # Limit to 5 certs
                                cert_record = self._airtable.get_record("company_certificates", cert_id)
                                cert_name = cert_record.get("fields", {}).get("Certificate_Name")
                                if cert_name:
                                    certificates.append(cert_name)
                        except AirtableError:
                            pass
                
                # Get recent LinkedIn posts if available
                recent_posts = []
                linkedin_data_str = company_fields.get("LinkedIn_Data")
                if linkedin_data_str:
                    try:
                        import json
                        linkedin_data = json.loads(linkedin_data_str) if isinstance(linkedin_data_str, str) else linkedin_data_str
                        recent_posts = linkedin_data.get("recent_posts", [])[:3]
                    except (json.JSONDecodeError, TypeError):
                        pass
                
                candidate = TargetCandidate(
                    business_unit_id=bu_id,
                    business_unit_name=bu_fields.get("Business Unit Name", "Unknown"),
                    company_id=company_id,
                    company_name=company_fields.get("Company Name", "Unknown"),
                    sector=bu_fields.get("Sector") or company_fields.get("Sector"),
                    country=bu_fields.get("Country") or company_fields.get("Country"),
                    fei_status=company_fields.get("FEI_Status", "Unknown"),
                    fei_criteria_met=company_fields.get("FEI_Criteria_Met", []),
                    fei_certificates=certificates,
                    has_key_person=key_person is not None,
                    key_person_name=key_person["name"] if key_person else None,
                    key_person_role=key_person["role"] if key_person else None,
                    key_person_linkedin=key_person.get("linkedin") if key_person else None,
                    contact_id=contact_id,
                    has_financials=has_financials,
                    has_linkedin_data=has_linkedin,
                    linkedin_company_url=linkedin_url,
                    recent_linkedin_posts=recent_posts,
                    last_outreach_date=last_outreach,
                    previous_engagement=bu_fields.get("Previous_Engagement"),
                    company_description=company_fields.get("Description"),
                )
                
                candidates.append(candidate)
            
            return candidates
            
        except AirtableError as e:
            logger.error("filter_by_criteria_failed", error=str(e))
            return []
    
    def _apply_cooling_off(
        self,
        candidates: list[TargetCandidate],
    ) -> list[TargetCandidate]:
        """Filter out BUs in cooling-off period (90 days).
        
        Args:
            candidates: List of candidates to filter
            
        Returns:
            Filtered list excluding cooling-off BUs
        """
        return [c for c in candidates if not c.is_in_cooling_off()]
    
    def _calculate_fit_score(
        self,
        candidate: TargetCandidate,
        affected_sectors: list[str],
        affected_countries: list[str],
        prioritize_fei: bool = True,
    ) -> None:
        """Calculate fit score for a candidate.
        
        Score components (enhanced for FEI prioritization per PRD):
        - Base: 50%
        - FEI Eligible: +20% (strategic priority)
        - FEI Certificates: +10% (green certs boost)
        - Key Person: +15%
        - Sector Match: +15%
        - Country Match: +8%
        - Financials: +8%
        - Positive Engagement: +10%
        - LinkedIn Data: +7%
        - Recent Activity: +5%
        
        Max theoretical score: 145% (clamped to 100%)
        
        Args:
            candidate: The candidate to score
            affected_sectors: Target sectors
            affected_countries: Target countries
            prioritize_fei: If True, apply stronger FEI boost
        """
        score = SCORE_WEIGHTS["base"]
        breakdown = {"base": SCORE_WEIGHTS["base"]}
        
        # FEI eligibility (+25%) - Strategic priority per Alter-5 business model
        if candidate.fei_status == "Eligible":
            fei_weight = SCORE_WEIGHTS["fei_eligible"]
            if prioritize_fei:
                fei_weight *= 1.2  # Additional 20% boost when prioritizing FEI
            score += fei_weight
            breakdown["fei_eligible"] = fei_weight
        
        # FEI green certificates (+10%) - ISO 14001, EcoLabel, etc.
        if candidate.has_green_certificates():
            score += SCORE_WEIGHTS["fei_has_certificates"]
            breakdown["fei_has_certificates"] = SCORE_WEIGHTS["fei_has_certificates"]
        
        # Key person identified (+15%)
        if candidate.has_key_person:
            weight = SCORE_WEIGHTS["key_person_identified"]
            # Bonus if key person has LinkedIn profile
            if candidate.key_person_linkedin:
                weight *= 1.1
            score += weight
            breakdown["key_person_identified"] = weight
        
        # Sector match (+12%)
        if candidate.sector and candidate.sector in affected_sectors:
            score += SCORE_WEIGHTS["sector_match"]
            breakdown["sector_match"] = SCORE_WEIGHTS["sector_match"]
        
        # Country match (+8%)
        if candidate.country and candidate.country in affected_countries:
            score += SCORE_WEIGHTS["country_match"]
            breakdown["country_match"] = SCORE_WEIGHTS["country_match"]
        
        # Financials complete (+8%)
        if candidate.has_financials:
            score += SCORE_WEIGHTS["financials_complete"]
            breakdown["financials_complete"] = SCORE_WEIGHTS["financials_complete"]
        
        # Positive engagement (+10%)
        if candidate.previous_engagement:
            engagement_lower = candidate.previous_engagement.lower()
            if "positive" in engagement_lower or "interested" in engagement_lower:
                score += SCORE_WEIGHTS["positive_engagement"]
                breakdown["positive_engagement"] = SCORE_WEIGHTS["positive_engagement"]
        
        # LinkedIn data available (+7%)
        if candidate.has_linkedin_data:
            score += SCORE_WEIGHTS["linkedin_data"]
            breakdown["linkedin_data"] = SCORE_WEIGHTS["linkedin_data"]
        
        # Recent activity bonus (+5%) - LinkedIn posts in last 30 days
        if candidate.recent_linkedin_posts:
            score += SCORE_WEIGHTS["recent_activity"]
            breakdown["recent_activity"] = SCORE_WEIGHTS["recent_activity"]
        
        # Clamp to 0-1 range
        candidate.fit_score = min(1.0, max(0.0, score))
        candidate.score_breakdown = breakdown
    
    def _prioritize(
        self,
        candidates: list[TargetCandidate],
    ) -> list[TargetCandidate]:
        """Prioritize candidates by fit score.
        
        Secondary sort: FEI eligible first, then by company name.
        
        Args:
            candidates: List of scored candidates
            
        Returns:
            Sorted list (highest score first)
        """
        return sorted(
            candidates,
            key=lambda c: (
                c.fit_score,
                1 if c.fei_status == "Eligible" else 0,
                c.has_key_person,
            ),
            reverse=True,
        )
    
    def _generate_justifications(
        self,
        candidates: list[TargetCandidate],
        market_context: Optional[str] = None,
    ) -> None:
        """Generate selection justifications using Claude.
        
        Args:
            candidates: List of candidates to justify
            market_context: Optional market context for more relevant justifications
        """
        if not candidates:
            return
        
        logger.debug("generating_justifications", count=len(candidates))
        
        # Generate justifications in batches to reduce API calls
        batch_size = 10
        
        for i in range(0, len(candidates), batch_size):
            batch = candidates[i:i + batch_size]
            
            prompt = f"""
Generate brief selection justifications for these campaign targets:

{"Market Context: " + market_context if market_context else ""}

Targets to justify:
"""
            for j, c in enumerate(batch, 1):
                prompt += f"""
{j}. {c.company_name} ({c.business_unit_name})
   - Sector: {c.sector or 'N/A'}
   - Country: {c.country or 'N/A'}
   - FEI Status: {c.fei_status}
   - Key Person: {c.key_person_name or 'Not identified'} ({c.key_person_role or 'N/A'})
   - Fit Score: {c.fit_score:.0%}
   - Score factors: {', '.join(c.score_breakdown.keys())}
"""
            
            prompt += """

For EACH target, write a brief justification (1-2 sentences, max 50 words) in Spanish explaining why they are a good target. Include:
- Main reason for selection (FEI, sector fit, etc.)
- Specific opportunity angle

Return ONLY a JSON object:
{
    "justifications": [
        "Target prioritario: empresa FEI elegible con ISO 14001, sector industrial alineado con trigger.",
        "..."
    ]
}
"""
            
            try:
                result = self._claude.generate_structured(
                    prompt=prompt,
                    system_prompt=self._system_prompt,
                )
                
                justifications = result.get("justifications", [])
                
                for k, c in enumerate(batch):
                    if k < len(justifications):
                        c.selection_justification = justifications[k]
                    else:
                        # Default justification
                        c.selection_justification = self._default_justification(c)
                        
            except ClaudeError as e:
                logger.warning("justification_generation_failed", error=str(e))
                # Use default justifications
                for c in batch:
                    c.selection_justification = self._default_justification(c)
    
    def _default_justification(self, candidate: TargetCandidate) -> str:
        """Generate a default justification without Claude.
        
        Args:
            candidate: The candidate to justify
            
        Returns:
            Default justification string
        """
        reasons = []
        
        if candidate.fei_status == "Eligible":
            reasons.append("empresa FEI elegible")
        
        if candidate.has_key_person:
            reasons.append(f"contacto clave identificado ({candidate.key_person_role})")
        
        if candidate.sector:
            reasons.append(f"sector {candidate.sector} alineado")
        
        if not reasons:
            reasons.append("cumple criterios de campaña")
        
        return f"Target seleccionado: {', '.join(reasons)}. Fit score: {candidate.fit_score:.0%}."
    
    def _save_targets(
        self,
        campaign_id: str,
        candidates: list[TargetCandidate],
    ) -> None:
        """Save selected targets as CampaignTarget records.
        
        Args:
            campaign_id: The campaign record ID
            candidates: List of selected candidates
        """
        for candidate in candidates:
            fields = {
                "Campaign": [campaign_id],
                "Business_Unit": [candidate.business_unit_id],
                "Fit_Score": candidate.fit_score,
                "Selection_Justification": candidate.selection_justification,
                "Status": "Pending_Review",
            }
            
            if candidate.contact_id:
                fields["Contact"] = [candidate.contact_id]
            
            try:
                self._airtable.create_record("campaign_targets", fields)
                
                logger.debug(
                    "target_saved",
                    campaign_id=campaign_id,
                    bu_id=candidate.business_unit_id,
                    company=candidate.company_name,
                )
                
            except AirtableError as e:
                logger.error(
                    "target_save_failed",
                    campaign_id=campaign_id,
                    bu_id=candidate.business_unit_id,
                    error=str(e),
                )


# ==============================================================================
# FACTORY FUNCTIONS
# ==============================================================================

_agent: Optional[SelectorTargets] = None


def get_selector() -> SelectorTargets:
    """Get shared SelectorTargets instance.
    
    Returns:
        Singleton SelectorTargets instance
    """
    global _agent
    if _agent is None:
        _agent = SelectorTargets()
    return _agent

