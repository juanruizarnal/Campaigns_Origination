"""Agente Evaluador FEI for Alter-5 Origination Engine.

This module implements the EvaluadorFEI agent (Agent 3) which evaluates
companies for FEI (Fondo Europeo de Inversiones) eligibility using:
- Scraped data from company websites (certifications)
- Claude for reasoning and analysis
- Gemini for web searches

A company is FEI eligible if it meets AT LEAST ONE of these 6 criteria:
1. 1.1_Cleantech_Prize - Has won a cleantech/sustainability prize (last 3 years)
2. 1.2_Clean_Energy_Patent - Owns clean energy patents (last 3 years)
3. 1.3_Eco_Label - Has EU/National/International eco-labels
4. 1.4_Green_Business_90 - ≥90% revenue from green activities
5. 1.5_Green_Business_Model - Inherently green business model with verifiable impact
6. 1.6_Environmental_Certificate - Has valid environmental certifications (ISO 14001, etc.)

Target: ≥90% precision in evaluation

Usage:
    from agents.evaluador_fei import EvaluadorFEI
    
    agent = EvaluadorFEI()
    result = agent.evaluate("recXXXXXX")
"""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Optional
import uuid

import structlog

from config.airtable_schema import (
    COMPANY_FIELDS,
    BUSINESS_UNIT_FIELDS,
    FEI_STATUS_OPTIONS,
    FEI_CRITERIA_OPTIONS,
)
from config.prompts import load_prompt
from core.airtable_client import AirtableClient, AirtableError, get_airtable_client
from core.async_utils import run_async
from core.models import FEIStatus, FEICriteria, FEIEvaluation, ScrapedCompanyData
from integrations.gemini import GeminiClient, GeminiError, get_gemini_client
from integrations.claude import ClaudeClient, ClaudeError, get_claude_client
from integrations.scraper import PlaywrightScraper, scrape_company, extract_certifications_from_text

logger = structlog.get_logger()


# ==============================================================================
# DATA CLASSES
# ==============================================================================

@dataclass
class CertificateEvidence:
    """Evidence of a certificate or eco-label."""
    certificate_type: str
    certificate_name: str
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    verification_url: Optional[str] = None
    fei_criteria: Optional[str] = None  # Which FEI criteria this satisfies


@dataclass
class PrizeEvidence:
    """Evidence of a cleantech prize or award."""
    prize_name: str
    year: Optional[int] = None
    awarding_organization: Optional[str] = None
    description: Optional[str] = None
    verification_url: Optional[str] = None


@dataclass
class GreenActivityEvidence:
    """Evidence of green business activity."""
    activity_name: str
    activity_type: str  # e.g., "Solar Generation", "Recycling"
    revenue_percentage: Optional[float] = None
    is_primary_activity: bool = False
    eu_taxonomy_aligned: bool = False


@dataclass
class CriterionResult:
    """Result of evaluating a single FEI criterion."""
    criterion: FEICriteria
    is_met: bool
    confidence: float  # 0-100
    evidence: list[str] = field(default_factory=list)
    reasoning: str = ""


@dataclass
class EvaluationResult:
    """Complete result of FEI evaluation."""
    company_id: str
    company_name: str
    status: FEIStatus
    criteria_met: list[FEICriteria]
    confidence: float  # 0-100
    reasoning: str
    criteria_results: list[CriterionResult] = field(default_factory=list)
    certificates_found: list[CertificateEvidence] = field(default_factory=list)
    prizes_found: list[PrizeEvidence] = field(default_factory=list)
    green_activities: list[GreenActivityEvidence] = field(default_factory=list)
    evaluation_date: date = field(default_factory=date.today)
    processing_time_seconds: float = 0.0
    errors: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    
    # NEW: Data sources used
    data_sources: list[str] = field(default_factory=list)
    scraped_data: Optional[ScrapedCompanyData] = None
    
    def is_eligible(self) -> bool:
        """Check if company is FEI eligible."""
        return self.status == FEIStatus.ELIGIBLE
    
    def needs_review(self) -> bool:
        """Check if evaluation needs human review."""
        return self.status == FEIStatus.PENDING_REVIEW or self.confidence < 70
    
    def get_primary_criterion(self) -> Optional[FEICriteria]:
        """Get the primary (highest confidence) criterion met."""
        if not self.criteria_met:
            return None
        # Return first one (usually highest confidence)
        return self.criteria_met[0]


# ==============================================================================
# EVALUADOR FEI AGENT
# ==============================================================================

class EvaluadorFEI:
    """Agent for evaluating FEI eligibility of companies.
    
    Uses a two-phase approach:
    1. Gemini searches for certificates, prizes, and green activities
    2. Claude analyzes evidence and determines eligibility with reasoning
    
    Example:
        agent = EvaluadorFEI()
        result = agent.evaluate("recXXXXXX")
        
        if result.is_eligible():
            print(f"Company is FEI eligible!")
            print(f"Criteria met: {result.criteria_met}")
    """
    
    # Valid environmental certificates (Criterion 1.6)
    VALID_CERTIFICATES = [
        "ISO 14001",
        "ISO 50001",
        "ISO 14064",
        "EMAS",
        "B Corp",
        "EcoVadis Gold",
        "EcoVadis Platinum",
    ]
    
    # Valid eco-labels (Criterion 1.3)
    VALID_ECO_LABELS = [
        "EU Ecolabel",
        "Blue Angel",
        "Nordic Swan",
        "NF Environnement",
        "FSC",
        "PEFC",
        "LEED",
        "BREEAM",
        "Energy Star",
    ]
    
    # Eligible cleantech prizes (Criterion 1.1)
    ELIGIBLE_PRIZES = [
        "CDTI Neotec",
        "Horizon Europe",
        "EIT Climate-KIC",
        "EIT InnoEnergy",
        "LIFE Programme",
        "EU Innovation Fund",
        "Cleantech Open",
        "Global Cleantech 100",
    ]
    
    # Green activities for Criterion 1.4/1.5
    GREEN_ACTIVITIES = [
        "Solar energy generation",
        "Wind energy generation",
        "Hydroelectric power",
        "Biomass energy",
        "Geothermal energy",
        "Energy efficiency services",
        "Electric vehicle manufacturing",
        "Battery technology",
        "Recycling and waste management",
        "Water treatment",
        "Sustainable agriculture",
        "Green construction",
        "Carbon capture",
        "Hydrogen technology",
    ]
    
    def __init__(
        self,
        airtable_client: Optional[AirtableClient] = None,
        gemini_client: Optional[GeminiClient] = None,
        claude_client: Optional[ClaudeClient] = None,
        use_scraping: bool = True,
    ):
        """Initialize the EvaluadorFEI agent.
        
        Args:
            airtable_client: Optional custom Airtable client
            gemini_client: Optional custom Gemini client for searches
            claude_client: Optional custom Claude client for reasoning
            use_scraping: Whether to use Playwright scraping (recommended for accuracy)
        """
        self._airtable = airtable_client or get_airtable_client()
        self._gemini = gemini_client or get_gemini_client()
        self._claude = claude_client or get_claude_client()
        self._system_prompt = load_prompt("evaluador_fei")
        self._use_scraping = use_scraping
        
        logger.info("evaluador_fei_initialized", use_scraping=use_scraping)
    
    def evaluate(
        self,
        company_id: str,
        force: bool = False,
        dry_run: bool = False,
        use_scraped_data: Optional[ScrapedCompanyData] = None,
    ) -> EvaluationResult:
        """Evaluate a company's FEI eligibility (sync wrapper)."""
        return run_async(
            self._evaluate_async(
                company_id=company_id,
                force=force,
                dry_run=dry_run,
                use_scraped_data=use_scraped_data,
            )
        )

    async def _evaluate_async(
        self,
        company_id: str,
        force: bool = False,
        dry_run: bool = False,
        use_scraped_data: Optional[ScrapedCompanyData] = None,
    ) -> EvaluationResult:
        """Evaluate a company's FEI eligibility.
        
        Uses multiple data sources for ≥90% precision:
        1. Scraped data from company website (highest priority for certs)
        2. Existing Airtable data
        3. Gemini search for additional verification
        4. Claude for final reasoning and decision
        
        Args:
            company_id: Airtable record ID of the company
            force: Force re-evaluation even if recently evaluated
            dry_run: If True, don't save changes to Airtable
            use_scraped_data: Pre-scraped data (from Enriquecedor) to avoid re-scraping
            
        Returns:
            EvaluationResult with status, criteria met, and reasoning
        """
        start_time = datetime.now()
        task_id = str(uuid.uuid4())[:8]
        
        logger.info(
            "fei_evaluation_started",
            task_id=task_id,
            company_id=company_id,
            force=force,
            dry_run=dry_run,
            has_scraped_data=use_scraped_data is not None,
        )
        
        # Initialize result
        result = EvaluationResult(
            company_id=company_id,
            company_name="",
            status=FEIStatus.UNKNOWN,
            criteria_met=[],
            confidence=0,
            reasoning="",
        )
        
        try:
            # 1. Get company from Airtable
            company_record = self._airtable.get_record("companies", company_id)
            fields = company_record.get("fields", {})
            
            company_name = fields.get("Company Name", "")
            company_url = fields.get("Home URL", "")
            result.company_name = company_name
            
            if not company_name:
                result.errors.append("Company name is empty")
                result.status = FEIStatus.UNKNOWN
                return result
            
            # Check if recently evaluated (unless force=True)
            if not force:
                last_check = fields.get("FEI_Last_Check")
                if last_check:
                    last_check_date = datetime.fromisoformat(last_check.replace("Z", "+00:00")).date()
                    days_since = (date.today() - last_check_date).days
                    if days_since < 30:  # Evaluated within last 30 days
                        logger.info(
                            "fei_evaluation_skipped_recent",
                            company_id=company_id,
                            days_since=days_since,
                        )
                        result.status = FEIStatus(fields.get("FEI_Status", "Unknown"))
                        result.confidence = fields.get("FEI_Confidence", 0) * 100 if fields.get("FEI_Confidence") else 0
                        result.reasoning = f"Skipped: Last evaluated {days_since} days ago"
                        return result
            
            logger.info(
                "fei_evaluation_company_loaded",
                task_id=task_id,
                company_name=company_name,
                company_url=company_url,
            )
            
            # 2. NEW: Get certifications from scraped data FIRST (highest accuracy)
            scraped_certs = []
            if use_scraped_data and use_scraped_data.success:
                result.scraped_data = use_scraped_data
                result.data_sources.append("web_scraping")
                scraped_certs = use_scraped_data.certifications
                if use_scraped_data.url:
                    result.sources.append(use_scraped_data.url)
                
                # Convert scraped certs to CertificateEvidence
                for cert_name in scraped_certs:
                    cert_evidence = CertificateEvidence(
                        certificate_type=self._determine_cert_type(cert_name),
                        certificate_name=cert_name,
                        fei_criteria=self._determine_fei_criteria(cert_name),
                        verification_url=use_scraped_data.url,
                    )
                    result.certificates_found.append(cert_evidence)
                
                logger.info(
                    "scraped_certs_processed",
                    task_id=task_id,
                    count=len(scraped_certs),
                    certs=scraped_certs,
                )
            
            # 3. If no scraped data and scraping enabled, scrape now
            elif self._use_scraping and company_url:
                try:
                    scraped_data = await scrape_company(company_url)
                    result.scraped_data = scraped_data
                    result.data_sources.append("web_scraping")
                    if scraped_data.url:
                        result.sources.append(scraped_data.url)
                    
                    if scraped_data.success:
                        scraped_certs = scraped_data.certifications
                        for cert_name in scraped_certs:
                            cert_evidence = CertificateEvidence(
                                certificate_type=self._determine_cert_type(cert_name),
                                certificate_name=cert_name,
                                fei_criteria=self._determine_fei_criteria(cert_name),
                                verification_url=company_url,
                            )
                            result.certificates_found.append(cert_evidence)
                except Exception as e:
                    logger.warning("scraping_failed", task_id=task_id, error=str(e))
            
            # 4. Check existing Airtable data for certificates
            existing_scraped = fields.get("Scraped_Content")
            if existing_scraped:
                try:
                    scraped_json = json.loads(existing_scraped)
                    airtable_certs = scraped_json.get("certifications", [])
                    result.data_sources.append("airtable_cache")
                    
                    for cert_name in airtable_certs:
                        if not any(c.certificate_name == cert_name for c in result.certificates_found):
                            result.certificates_found.append(CertificateEvidence(
                                certificate_type=self._determine_cert_type(cert_name),
                                certificate_name=cert_name,
                                fei_criteria=self._determine_fei_criteria(cert_name),
                            ))
                except (json.JSONDecodeError, TypeError):
                    pass
            
            # 5. Search for additional certificates with Gemini (verification/complement)
            if not result.certificates_found:  # Only if we haven't found any yet
                result.data_sources.append("gemini_search")
                gemini_certs, cert_sources = self._search_certificates(company_name, company_url)
                result.certificates_found.extend(gemini_certs)
                result.sources.extend(cert_sources)
                
                gemini_eco_labels, eco_sources = self._search_eco_labels(company_name, company_url)
                result.certificates_found.extend(gemini_eco_labels)
                result.sources.extend(eco_sources)
            
            # 6. Search for cleantech prizes (Criterion 1.1) - always search
            prizes, prize_sources = self._search_prizes(company_name, company_url)
            result.prizes_found = prizes
            result.sources.extend(prize_sources)
            
            # 7. Check green business activity (Criteria 1.4 and 1.5)
            green_activities, green_sources = self._check_green_activity(
                company_name, company_url, company_record
            )
            result.green_activities = green_activities
            result.sources.extend(green_sources)
            
            # Also use scraped green indicators
            if result.scraped_data and result.scraped_data.green_indicators:
                for indicator in result.scraped_data.green_indicators[:5]:
                    result.green_activities.append(GreenActivityEvidence(
                        activity_name=indicator,
                        activity_type="Green Indicator",
                        is_primary_activity=False,
                    ))
            
            # 8. Evaluate with Claude for complex cases and calibrated confidence
            evaluation = self._evaluate_with_reasoning(
                company_name=company_name,
                company_url=company_url,
                certificates=result.certificates_found,
                prizes=result.prizes_found,
                green_activities=result.green_activities,
                company_description=fields.get("Description", ""),
            )

            result.status = evaluation["status"]
            result.criteria_met = evaluation["criteria_met"]
            result.confidence = evaluation["confidence"]
            result.reasoning = evaluation["reasoning"]
            result.criteria_results = evaluation.get("criteria_results", [])
            
            # Append sources to reasoning (literal URLs)
            if result.sources:
                unique_sources = list(dict.fromkeys(result.sources))
                sources_text = "\n".join(f"- {s}" for s in unique_sources[:10])
                result.reasoning = f"{result.reasoning}\n\nFuentes:\n{sources_text}"
            
            # 10. Save evaluation to Airtable
            if not dry_run:
                self._save_evaluation(company_id, result)
            
        except AirtableError as e:
            logger.error(
                "fei_evaluation_airtable_error",
                task_id=task_id,
                company_id=company_id,
                error=str(e),
            )
            result.errors.append(f"Airtable error: {e}")
            result.status = FEIStatus.UNKNOWN
            
        except (GeminiError, ClaudeError) as e:
            logger.error(
                "fei_evaluation_llm_error",
                task_id=task_id,
                company_id=company_id,
                error=str(e),
            )
            result.errors.append(f"LLM error: {e}")
            result.status = FEIStatus.PENDING_REVIEW
            result.confidence = 0
            
        except Exception as e:
            logger.error(
                "fei_evaluation_unexpected_error",
                task_id=task_id,
                company_id=company_id,
                error=str(e),
                exc_info=True,
            )
            result.errors.append(f"Unexpected error: {e}")
            result.status = FEIStatus.UNKNOWN
        
        # Calculate processing time
        result.processing_time_seconds = (datetime.now() - start_time).total_seconds()

        # Deduplicate sources
        if result.sources:
            result.sources = list(dict.fromkeys(result.sources))
        
        logger.info(
            "fei_evaluation_completed",
            task_id=task_id,
            company_id=company_id,
            status=result.status.value,
            criteria_met=[c.value for c in result.criteria_met],
            confidence=result.confidence,
            data_sources=result.data_sources,
            processing_time=result.processing_time_seconds,
        )
        
        return result
    
    def _determine_cert_type(self, cert_name: str) -> str:
        """Determine certificate type from name."""
        if "ISO" in cert_name.upper():
            return "ISO"
        elif "B Corp" in cert_name or "EMAS" in cert_name:
            return "Eco-label"
        elif any(x in cert_name for x in ["FSC", "PEFC", "LEED", "BREEAM"]):
            return "Eco-label"
        return "Environmental"
    
    def _determine_fei_criteria(self, cert_name: str) -> str:
        """Determine which FEI criteria a certificate satisfies."""
        # Criterion 1.6: Environmental Management Certificates
        if any(x in cert_name.upper() for x in ["ISO 14001", "ISO 50001", "ISO 14064", "EMAS"]):
            return "1.6_Environmental_Certificate"
        
        # Criterion 1.3: Eco-labels
        if any(x in cert_name for x in ["B Corp", "FSC", "PEFC", "LEED", "BREEAM", "Ecolabel"]):
            return "1.3_Eco_Label"
        
        return "1.6_Environmental_Certificate"  # Default
    
    def _is_fei_valid_cert(self, cert_name: str) -> bool:
        """Check if certificate is valid for FEI eligibility (Criterion 1.6)."""
        valid_certs = [
            "ISO 14001", "ISO 50001", "ISO 14064",
            "EMAS", "B Corp",
        ]
        return any(valid in cert_name for valid in valid_certs)
    
    def _search_certificates(
        self,
        company_name: str,
        company_url: Optional[str],
    ) -> tuple[list[CertificateEvidence], list[str]]:
        """Search for environmental certificates (Criterion 1.6).
        
        Looks for:
        - ISO 14001 (Environmental Management)
        - ISO 50001 (Energy Management)
        - ISO 14064 (GHG Verification)
        - EMAS (EU Eco-Management)
        
        Args:
            company_name: Name of the company
            company_url: Company website URL
            
        Returns:
            List of certificate evidence found
        """
        logger.debug("searching_certificates", company_name=company_name)
        
        query = f"""
Search for environmental certifications held by "{company_name}".
{f'Website: {company_url}' if company_url else ''}

Look for these specific certifications:
- ISO 14001 (Environmental Management System)
- ISO 50001 (Energy Management System)
- ISO 14064 (Greenhouse Gas Verification)
- EMAS (EU Eco-Management and Audit Scheme)

Search the company website, certification body registries, and press releases.

Return ONLY a JSON object with this structure:
{{
    "certificates": [
        {{
            "certificate_type": "ISO 14001",
            "certificate_name": "ISO 14001:2015 Environmental Management",
            "issuer": "Bureau Veritas",
            "issue_date": "2022-01-15",
            "expiry_date": "2025-01-15",
            "verification_url": "https://..."
        }}
    ]
}}

Only include certificates you can verify. If none found, return empty list.
"""
        
        try:
            response = self._gemini.search_and_generate(
                query=query,
                system_prompt="You are an expert at finding corporate certifications. Be thorough but only report verified information.",
            )
            
            result = self._gemini.generate_json(
                prompt=f"Extract certificate information as JSON:\n\n{response['response']}",
            )
            
            certificates = []
            for cert_data in result.get("certificates", []):
                if cert_data.get("certificate_type"):
                    certificates.append(CertificateEvidence(
                        certificate_type=cert_data["certificate_type"],
                        certificate_name=cert_data.get("certificate_name", cert_data["certificate_type"]),
                        issuer=cert_data.get("issuer"),
                        issue_date=cert_data.get("issue_date"),
                        expiry_date=cert_data.get("expiry_date"),
                        verification_url=cert_data.get("verification_url"),
                        fei_criteria="1.6_Environmental_Certificate",
                    ))
            
            sources = response.get("sources", []) if isinstance(response, dict) else []
            return certificates, sources
            
        except (GeminiError, KeyError, TypeError) as e:
            logger.warning("certificate_search_failed", company_name=company_name, error=str(e))
            return [], []
    
    def _search_eco_labels(
        self,
        company_name: str,
        company_url: Optional[str],
    ) -> tuple[list[CertificateEvidence], list[str]]:
        """Search for eco-labels (Criterion 1.3).
        
        Looks for:
        - EU Ecolabel
        - Blue Angel, Nordic Swan
        - FSC, PEFC (forestry)
        - LEED, BREEAM (buildings)
        
        Args:
            company_name: Name of the company
            company_url: Company website URL
            
        Returns:
            List of eco-label evidence found
        """
        logger.debug("searching_eco_labels", company_name=company_name)
        
        query = f"""
Search for eco-labels and environmental product certifications held by "{company_name}" or their products.
{f'Website: {company_url}' if company_url else ''}

Look for:
- EU Ecolabel
- Blue Angel (Der Blaue Engel)
- Nordic Swan (Svanen)
- NF Environnement
- FSC (Forest Stewardship Council)
- PEFC
- LEED certification
- BREEAM certification
- B Corp certification
- Energy Star

Return ONLY a JSON object:
{{
    "eco_labels": [
        {{
            "label_name": "EU Ecolabel",
            "products_certified": "Office paper products",
            "verification_url": "https://..."
        }}
    ]
}}

Only include verified eco-labels. If none found, return empty list.
"""
        
        try:
            response = self._gemini.search_and_generate(
                query=query,
                system_prompt="You are an expert at finding eco-labels and environmental certifications.",
            )
            
            result = self._gemini.generate_json(
                prompt=f"Extract eco-label information as JSON:\n\n{response['response']}",
            )
            
            eco_labels = []
            for label_data in result.get("eco_labels", []):
                if label_data.get("label_name"):
                    eco_labels.append(CertificateEvidence(
                        certificate_type="Eco-label",
                        certificate_name=label_data["label_name"],
                        verification_url=label_data.get("verification_url"),
                        fei_criteria="1.3_Eco_Label",
                    ))
            
            sources = response.get("sources", []) if isinstance(response, dict) else []
            return eco_labels, sources
            
        except (GeminiError, KeyError, TypeError) as e:
            logger.warning("eco_label_search_failed", company_name=company_name, error=str(e))
            return [], []
    
    def _search_prizes(
        self,
        company_name: str,
        company_url: Optional[str],
    ) -> tuple[list[PrizeEvidence], list[str]]:
        """Search for cleantech prizes (Criterion 1.1).
        
        Looks for:
        - CDTI Neotec
        - Horizon Europe grants
        - EIT Climate-KIC awards
        - EIT InnoEnergy
        - LIFE Programme
        
        Args:
            company_name: Name of the company
            company_url: Company website URL
            
        Returns:
            List of prize evidence found
        """
        logger.debug("searching_prizes", company_name=company_name)
        
        current_year = date.today().year
        min_year = current_year - 3  # Last 3 years
        
        query = f"""
Search for cleantech, sustainability, or environmental prizes and awards won by "{company_name}" since {min_year}.
{f'Website: {company_url}' if company_url else ''}

Look specifically for:
- CDTI Neotec awards
- Horizon Europe / H2020 grants
- EIT Climate-KIC programs
- EIT InnoEnergy awards
- EU LIFE Programme projects
- EU Innovation Fund awards
- Global Cleantech 100 recognition
- National cleantech/sustainability awards

Return ONLY a JSON object:
{{
    "prizes": [
        {{
            "prize_name": "Horizon Europe Grant",
            "year": 2023,
            "awarding_organization": "European Commission",
            "description": "Grant for renewable energy project",
            "verification_url": "https://..."
        }}
    ]
}}

Only include prizes from {min_year} onwards. If none found, return empty list.
"""
        
        try:
            response = self._gemini.search_and_generate(
                query=query,
                system_prompt="You are an expert at finding cleantech awards and EU funding programs.",
            )
            
            result = self._gemini.generate_json(
                prompt=f"Extract prize information as JSON:\n\n{response['response']}",
            )
            
            prizes = []
            for prize_data in result.get("prizes", []):
                if prize_data.get("prize_name"):
                    year = prize_data.get("year")
                    # Validate year is recent
                    if year and (year < min_year or year > current_year):
                        continue
                    
                    prizes.append(PrizeEvidence(
                        prize_name=prize_data["prize_name"],
                        year=year,
                        awarding_organization=prize_data.get("awarding_organization"),
                        description=prize_data.get("description"),
                        verification_url=prize_data.get("verification_url"),
                    ))
            
            sources = response.get("sources", []) if isinstance(response, dict) else []
            return prizes, sources
            
        except (GeminiError, KeyError, TypeError) as e:
            logger.warning("prize_search_failed", company_name=company_name, error=str(e))
            return [], []
    
    def _check_green_activity(
        self,
        company_name: str,
        company_url: Optional[str],
        company_record: dict,
    ) -> tuple[list[GreenActivityEvidence], list[str]]:
        """Check for green business activity (Criteria 1.4 and 1.5).
        
        Criterion 1.4: >90% of revenue from green activities
        Criterion 1.5: Inherently green business model
        
        Args:
            company_name: Name of the company
            company_url: Company website URL
            company_record: Company record from Airtable
            
        Returns:
            List of green activity evidence
        """
        logger.debug("checking_green_activity", company_name=company_name)
        
        # First, check if we have Business Units with revenue percentages in Airtable
        try:
            fields = company_record.get("fields", {})
            business_unit_ids = fields.get("Business Units", [])
            
            airtable_activities = []
            for bu_id in business_unit_ids[:5]:  # Max 5 BUs
                try:
                    bu_record = self._airtable.get_record("business_units", bu_id)
                    bu_fields = bu_record.get("fields", {})
                    
                    revenue_pct = bu_fields.get("Revenue_Percentage")
                    activities = bu_fields.get("Activities_Names", [])
                    
                    if revenue_pct and activities:
                        for activity in activities:
                            airtable_activities.append(GreenActivityEvidence(
                                activity_name=activity,
                                activity_type="Business Unit Activity",
                                revenue_percentage=revenue_pct * 100 if revenue_pct else None,
                                is_primary_activity=revenue_pct and revenue_pct > 0.5,
                            ))
                except AirtableError:
                    pass
            
            if airtable_activities:
                return airtable_activities, []
                
        except Exception as e:
            logger.warning("airtable_activity_check_failed", error=str(e))
        
        # Fall back to web search for green activities
        query = f"""
Analyze the business model and activities of "{company_name}".
{f'Website: {company_url}' if company_url else ''}

Determine if this company is primarily engaged in green/sustainable activities:
- Renewable energy (solar, wind, hydro, geothermal)
- Energy efficiency
- Electric vehicles / clean transportation
- Recycling / circular economy
- Sustainable agriculture
- Water treatment
- Green construction / LEED buildings

For each green activity found, estimate the percentage of company revenue it represents.

Return ONLY a JSON object:
{{
    "green_activities": [
        {{
            "activity_name": "Solar panel installation",
            "activity_type": "Solar energy generation",
            "estimated_revenue_percentage": 80,
            "is_primary_activity": true,
            "eu_taxonomy_aligned": true
        }}
    ],
    "total_green_revenue_percentage": 80,
    "is_inherently_green": true
}}

Be conservative in estimates. If unsure, use lower percentages.
"""
        
        try:
            response = self._gemini.search_and_generate(
                query=query,
                system_prompt="You are an expert at analyzing business models for environmental sustainability.",
            )
            
            result = self._gemini.generate_json(
                prompt=f"Extract green activity analysis as JSON:\n\n{response['response']}",
            )
            
            activities = []
            for activity_data in result.get("green_activities", []):
                if activity_data.get("activity_name"):
                    activities.append(GreenActivityEvidence(
                        activity_name=activity_data["activity_name"],
                        activity_type=activity_data.get("activity_type", "Unknown"),
                        revenue_percentage=activity_data.get("estimated_revenue_percentage"),
                        is_primary_activity=activity_data.get("is_primary_activity", False),
                        eu_taxonomy_aligned=activity_data.get("eu_taxonomy_aligned", False),
                    ))
            
            sources = response.get("sources", []) if isinstance(response, dict) else []
            return activities, sources
            
        except (GeminiError, KeyError, TypeError) as e:
            logger.warning("green_activity_check_failed", company_name=company_name, error=str(e))
            return [], []
    
    def _evaluate_with_reasoning(
        self,
        company_name: str,
        company_url: Optional[str],
        certificates: list[CertificateEvidence],
        prizes: list[PrizeEvidence],
        green_activities: list[GreenActivityEvidence],
        company_description: str,
    ) -> dict[str, Any]:
        """Use Claude to evaluate evidence and determine FEI eligibility.
        
        Args:
            company_name: Name of the company
            company_url: Company website
            certificates: List of certificates/eco-labels found
            prizes: List of cleantech prizes found
            green_activities: List of green activities found
            company_description: Company description from Airtable
            
        Returns:
            Dict with status, criteria_met, confidence, reasoning
        """
        logger.debug("evaluating_with_reasoning", company_name=company_name)
        
        # Compile evidence summary
        evidence_text = self._compile_evidence_summary(
            certificates, prizes, green_activities
        )
        
        prompt = f"""
Evaluate the FEI eligibility of this company:

**Company Name**: {company_name}
**Website**: {company_url or 'Not provided'}
**Description**: {company_description or 'Not provided'}

**Evidence Found**:
{evidence_text}

**FEI Eligibility Criteria** (company must meet AT LEAST ONE):

1. **1.1_Cleantech_Prize**: Won a recognized cleantech or sustainability prize
2. **1.2_Clean_Energy_Patent**: Owns patents in clean energy technology
3. **1.3_Eco_Label**: Has EU eco-labels on products/services
4. **1.4_Green_Business_90**: >90% of revenue from green activities
5. **1.5_Green_Business_Model**: Business model is inherently green/sustainable
6. **1.6_Environmental_Certificate**: Has environmental certifications (ISO 14001, EMAS, etc.)

**Your Task**:
1. Evaluate each criterion based on the evidence
2. Determine if ANY criterion is clearly met
3. Assign an overall status and confidence

Return a JSON object with this EXACT structure:
{{
    "status": "Eligible|Not_Eligible|Partially_Eligible|Pending_Review|Unknown",
    "criteria_met": ["1.6_Environmental_Certificate"],
    "confidence": 85,
    "reasoning": "Detailed explanation of the evaluation...",
    "criteria_evaluation": {{
        "1.1_Cleantech_Prize": {{"met": false, "evidence": "", "confidence": 0}},
        "1.2_Clean_Energy_Patent": {{"met": false, "evidence": "", "confidence": 0}},
        "1.3_Eco_Label": {{"met": false, "evidence": "", "confidence": 0}},
        "1.4_Green_Business_90": {{"met": false, "evidence": "", "confidence": 0}},
        "1.5_Green_Business_Model": {{"met": false, "evidence": "", "confidence": 0}},
        "1.6_Environmental_Certificate": {{"met": true, "evidence": "ISO 14001 verified", "confidence": 90}}
    }}
}}

**Guidelines**:
- Set status="Eligible" ONLY if at least one criterion is clearly met with >70% confidence
- Set status="Partially_Eligible" if evidence suggests possible eligibility but needs verification
- Set status="Pending_Review" if evidence is ambiguous or conflicting
- Set status="Not_Eligible" if no criteria appear to be met
- Set status="Unknown" if insufficient information
- Be conservative: when in doubt, use lower confidence
"""
        
        try:
            result = self._claude.generate_structured(
                prompt=prompt,
                system_prompt=self._system_prompt,
            )
            
            # Parse status
            status_str = result.get("status", "Unknown")
            try:
                status = FEIStatus(status_str)
            except ValueError:
                status = FEIStatus.UNKNOWN
            
            # Parse criteria met
            criteria_met = []
            for c in result.get("criteria_met", []):
                try:
                    criteria_met.append(FEICriteria(c))
                except ValueError:
                    pass
            
            # Build criteria results
            criteria_results = []
            for criterion_name, criterion_data in result.get("criteria_evaluation", {}).items():
                try:
                    criteria_results.append(CriterionResult(
                        criterion=FEICriteria(criterion_name),
                        is_met=criterion_data.get("met", False),
                        confidence=criterion_data.get("confidence", 0),
                        evidence=[criterion_data.get("evidence", "")] if criterion_data.get("evidence") else [],
                        reasoning=criterion_data.get("evidence", ""),
                    ))
                except ValueError:
                    pass
            
            return {
                "status": status,
                "criteria_met": criteria_met,
                "confidence": result.get("confidence", 0),
                "reasoning": result.get("reasoning", ""),
                "criteria_results": criteria_results,
            }
            
        except (ClaudeError, KeyError, TypeError) as e:
            logger.error("evaluation_reasoning_failed", company_name=company_name, error=str(e))
            return {
                "status": FEIStatus.PENDING_REVIEW,
                "criteria_met": [],
                "confidence": 0,
                "reasoning": f"Evaluation failed: {e}",
                "criteria_results": [],
            }
    
    def _compile_evidence_summary(
        self,
        certificates: list[CertificateEvidence],
        prizes: list[PrizeEvidence],
        green_activities: list[GreenActivityEvidence],
    ) -> str:
        """Compile evidence into a summary for Claude."""
        sections = []
        
        if certificates:
            cert_lines = []
            for c in certificates:
                cert_lines.append(f"- {c.certificate_name} (Issuer: {c.issuer or 'Unknown'})")
            sections.append("**Certificates/Eco-labels Found**:\n" + "\n".join(cert_lines))
        else:
            sections.append("**Certificates/Eco-labels Found**: None")
        
        if prizes:
            prize_lines = []
            for p in prizes:
                prize_lines.append(f"- {p.prize_name} ({p.year or 'Unknown year'}) from {p.awarding_organization or 'Unknown'}")
            sections.append("**Cleantech Prizes Found**:\n" + "\n".join(prize_lines))
        else:
            sections.append("**Cleantech Prizes Found**: None")
        
        if green_activities:
            activity_lines = []
            for a in green_activities:
                pct = f"{a.revenue_percentage:.0f}%" if a.revenue_percentage else "Unknown %"
                activity_lines.append(f"- {a.activity_name} ({a.activity_type}): {pct} of revenue")
            sections.append("**Green Activities Found**:\n" + "\n".join(activity_lines))
            
            # Calculate total green revenue
            total_green = sum(a.revenue_percentage or 0 for a in green_activities)
            sections.append(f"**Total Estimated Green Revenue**: {total_green:.0f}%")
        else:
            sections.append("**Green Activities Found**: None")
        
        return "\n\n".join(sections)
    
    def _save_evaluation(self, company_id: str, result: EvaluationResult) -> None:
        """Save FEI evaluation results to Airtable.
        
        Args:
            company_id: Company record ID
            result: Evaluation result to save
        """
        try:
            update_fields = {
                "FEI_Status": result.status.value,
                "FEI_Confidence": result.confidence / 100,  # Convert to 0-1 for percent field
                "FEI_Last_Check": result.evaluation_date.isoformat(),
                "FEI_Notes": result.reasoning[:1000] if result.reasoning else "",  # Truncate if too long
            }
            
            if result.criteria_met:
                update_fields["FEI_Criteria_Met"] = [c.value for c in result.criteria_met]
            
            self._airtable.update_record("companies", company_id, update_fields)
            
            logger.info(
                "fei_evaluation_saved",
                company_id=company_id,
                status=result.status.value,
                criteria_count=len(result.criteria_met),
            )
            
        except AirtableError as e:
            logger.error(
                "fei_evaluation_save_failed",
                company_id=company_id,
                error=str(e),
            )
            result.errors.append(f"Failed to save evaluation: {e}")
    
    def evaluate_batch(
        self,
        company_ids: list[str],
        force: bool = False,
        dry_run: bool = False,
        on_progress: Optional[callable] = None,
        max_concurrent: int = 3,
    ) -> list[EvaluationResult]:
        """Evaluate FEI eligibility for multiple companies (sync wrapper)."""
        return run_async(
            self._evaluate_batch_async(
                company_ids=company_ids,
                force=force,
                dry_run=dry_run,
                on_progress=on_progress,
                max_concurrent=max_concurrent,
            )
        )

    async def _evaluate_batch_async(
        self,
        company_ids: list[str],
        force: bool = False,
        dry_run: bool = False,
        on_progress: Optional[callable] = None,
        max_concurrent: int = 3,
    ) -> list[EvaluationResult]:
        """Evaluate FEI eligibility for multiple companies with concurrency.
        
        Args:
            company_ids: List of company record IDs
            force: Force re-evaluation
            dry_run: Don't save changes
            on_progress: Optional callback(current, total, result)
            max_concurrent: Maximum concurrent evaluations
            
        Returns:
            List of EvaluationResult for each company
        """
        total = len(company_ids)
        semaphore = asyncio.Semaphore(max_concurrent)
        
        logger.info(
            "batch_fei_evaluation_started",
            total_companies=total,
            force=force,
            dry_run=dry_run,
            max_concurrent=max_concurrent,
        )
        
        async def evaluate_with_semaphore(company_id: str, index: int) -> EvaluationResult:
            async with semaphore:
                result = await self._evaluate_async(
                    company_id=company_id,
                    force=force,
                    dry_run=dry_run,
                )
                if on_progress:
                    on_progress(index, total, result)
                return result
        
        tasks = [
            evaluate_with_semaphore(company_id, i + 1)
            for i, company_id in enumerate(company_ids)
        ]
        results = await asyncio.gather(*tasks)
        
        # Log summary
        eligible = sum(1 for r in results if r.status == FEIStatus.ELIGIBLE)
        not_eligible = sum(1 for r in results if r.status == FEIStatus.NOT_ELIGIBLE)
        pending = sum(1 for r in results if r.status == FEIStatus.PENDING_REVIEW)
        avg_confidence = sum(r.confidence for r in results) / len(results) if results else 0
        
        # Calculate precision metrics
        high_confidence = sum(1 for r in results if r.confidence >= 80)
        
        logger.info(
            "batch_fei_evaluation_completed",
            total=total,
            eligible=eligible,
            not_eligible=not_eligible,
            pending_review=pending,
            average_confidence=avg_confidence,
            high_confidence_count=high_confidence,
            precision_estimate=f"{high_confidence/total*100:.1f}%" if total > 0 else "N/A",
        )
        
        return results


# ==============================================================================
# FACTORY FUNCTIONS
# ==============================================================================

_agent: Optional[EvaluadorFEI] = None


def get_evaluador_fei() -> EvaluadorFEI:
    """Get shared EvaluadorFEI instance.
    
    Returns:
        Singleton EvaluadorFEI instance
    """
    global _agent
    if _agent is None:
        _agent = EvaluadorFEI()
    return _agent

