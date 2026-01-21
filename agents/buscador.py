"""Agente Buscador de Empresas for Alter-5 Origination Engine.

This module implements the BuscadorEmpresas agent (Agent 1) which searches
for new companies matching specified criteria using Gemini's search grounding.

The agent can:
- Search for companies by sector, country, region, and keywords
- Verify that found URLs are real and accessible
- Deduplicate against existing companies in the database
- Create Company + Business Unit "Default" records

Usage:
    from agents.buscador import BuscadorEmpresas
    
    agent = BuscadorEmpresas()
    result = agent.search(
        sector="renovables",
        country="ES",
        region="Andalucía",
        min_employees=50,
        limit=25,
    )
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from urllib.parse import urlparse
from difflib import SequenceMatcher
import uuid
import re
import asyncio

import httpx
import structlog

from config.settings import get_settings
from config.airtable_schema import TABLES, COMPANY_FIELDS, BUSINESS_UNIT_FIELDS
from config.prompts import load_prompt
from core.airtable_client import AirtableClient, AirtableError, get_airtable_client
from core.models import Company
from integrations.gemini import GeminiClient, GeminiError, get_gemini_client

logger = structlog.get_logger()
settings = get_settings()


# ==============================================================================
# CONSTANTS
# ==============================================================================

# URL verification timeout
URL_TIMEOUT_SECONDS = 5

# Similarity threshold for deduplication
SIMILARITY_THRESHOLD = 0.90

# Default source for AI-found companies (aligned with tests and Airtable options)
# Valid options: Research, Internal Referral, AI_Scraping, Web Scraping, Web Form,
# Partner Referral, LinkedIn Outreach, Event, CRM Migration, Phone Call, Other
DEFAULT_SOURCE = "AI_Scraping"

# Default business unit name
DEFAULT_BU_NAME = "Default"

# Maximum results per search
MAX_SEARCH_RESULTS = 50


# ==============================================================================
# DATA CLASSES
# ==============================================================================

@dataclass
class SearchCriteria:
    """Criteria for searching companies."""
    sector: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    keywords: list[str] = field(default_factory=list)
    min_employees: Optional[int] = None
    max_employees: Optional[int] = None
    limit: int = 25
    
    def to_query(self) -> str:
        """Convert criteria to search query string."""
        parts = []
        
        if self.sector:
            parts.append(f"empresas de {self.sector}")
        
        if self.region and self.country:
            parts.append(f"en {self.region}, {self.country}")
        elif self.country:
            parts.append(f"en {self.country}")
        elif self.region:
            parts.append(f"en {self.region}")
        
        if self.min_employees:
            parts.append(f"con más de {self.min_employees} empleados")
        
        if self.keywords:
            parts.append(f"relacionadas con {', '.join(self.keywords)}")
        
        return " ".join(parts)
    
    def is_valid(self) -> bool:
        """Check if criteria has minimum required fields."""
        return self.sector is not None or len(self.keywords) > 0


@dataclass
class CompanyCandidate:
    """A candidate company found during search."""
    name: str
    home_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    description: Optional[str] = None
    sector: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    estimated_employees: Optional[int] = None
    url_verified: bool = False
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None
    created_company_id: Optional[str] = None
    created_bu_id: Optional[str] = None
    
    def get_domain(self) -> Optional[str]:
        """Extract domain from home_url."""
        if not self.home_url:
            return None
        try:
            parsed = urlparse(self.home_url)
            domain = parsed.netloc.lower()
            # Remove www. prefix
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception:
            return None


@dataclass
class SearchResult:
    """Result of a company search."""
    criteria: SearchCriteria
    candidates_found: list[CompanyCandidate] = field(default_factory=list)
    candidates_verified: int = 0
    candidates_deduplicated: int = 0
    candidates_created: int = 0
    duplicates_found: int = 0
    companies_created: list[str] = field(default_factory=list)
    bus_created: list[str] = field(default_factory=list)
    success: bool = False
    errors: list[str] = field(default_factory=list)
    processing_time_seconds: float = 0.0
    
    def __str__(self) -> str:
        if not self.success:
            return f"❌ Search failed: {', '.join(self.errors)}"
        
        return (
            f"✅ Search completed\n"
            f"   Criteria: {self.criteria.to_query()[:50]}...\n"
            f"   Found: {len(self.candidates_found)} candidates\n"
            f"   Verified URLs: {self.candidates_verified}\n"
            f"   Duplicates: {self.duplicates_found}\n"
            f"   Created: {self.candidates_created} companies"
        )
    
    def get_new_candidates(self) -> list[CompanyCandidate]:
        """Get candidates that are not duplicates and have verified URLs."""
        return [
            c for c in self.candidates_found
            if c.url_verified and not c.is_duplicate
        ]


# ==============================================================================
# BUSCADOR EMPRESAS AGENT
# ==============================================================================

class BuscadorEmpresas:
    """Agent for searching and creating new companies.
    
    Uses Gemini's search grounding to find real companies
    matching specified criteria, verifies URLs, deduplicates
    against existing database, and creates new records.
    
    Example:
        agent = BuscadorEmpresas()
        result = agent.search(
            sector="energía solar",
            country="ES",
            region="Andalucía",
            min_employees=50,
            limit=25,
        )
        
        for company_id in result.companies_created:
            print(f"Created: {company_id}")
    """
    
    def __init__(
        self,
        airtable_client: Optional[AirtableClient] = None,
        gemini_client: Optional[GeminiClient] = None,
    ):
        """Initialize the BuscadorEmpresas agent.
        
        Args:
            airtable_client: Optional custom Airtable client
            gemini_client: Optional custom Gemini client
        """
        self._airtable = airtable_client or get_airtable_client()
        self._gemini = gemini_client or get_gemini_client()
        self._system_prompt = load_prompt("buscador")
        
        logger.info("buscador_empresas_initialized")
    
    def search(
        self,
        sector: Optional[str] = None,
        country: Optional[str] = None,
        region: Optional[str] = None,
        keywords: Optional[list[str]] = None,
        min_employees: Optional[int] = None,
        max_employees: Optional[int] = None,
        limit: int = 25,
        verify_urls: bool = True,
        deduplicate: bool = True,
        create_records: bool = True,
        dry_run: bool = False,
    ) -> SearchResult:
        """Search for companies matching criteria.
        
        Args:
            sector: Target sector (e.g., "renovables", "tecnología")
            country: Target country code (e.g., "ES", "PT")
            region: Target region (e.g., "Andalucía", "Cataluña")
            keywords: Additional search keywords
            min_employees: Minimum employee count
            max_employees: Maximum employee count
            limit: Maximum companies to find
            verify_urls: If True, verify URLs are accessible
            deduplicate: If True, check against existing companies
            create_records: If True, create records in Airtable
            dry_run: If True, don't create records even if create_records=True
            
        Returns:
            SearchResult with found and created companies
        """
        start_time = datetime.now()
        task_id = str(uuid.uuid4())[:8]
        
        # Build criteria
        criteria = SearchCriteria(
            sector=sector,
            country=country,
            region=region,
            keywords=keywords or [],
            min_employees=min_employees,
            max_employees=max_employees,
            limit=min(limit, MAX_SEARCH_RESULTS),
        )
        
        logger.info(
            "company_search_started",
            task_id=task_id,
            query=criteria.to_query(),
            limit=criteria.limit,
        )
        
        result = SearchResult(criteria=criteria)
        
        try:
            # Validate criteria
            if not criteria.is_valid():
                result.errors.append("Invalid criteria: must specify sector or keywords")
                return result
            
            # Step 1: Search with Gemini
            query = self._build_search_query(criteria)
            
            logger.debug(
                "search_query_built",
                task_id=task_id,
                query=query,
            )
            
            candidates = self._search_companies(query, criteria.limit)
            result.candidates_found = candidates
            
            logger.info(
                "search_completed",
                task_id=task_id,
                candidates_found=len(candidates),
            )
            
            if not candidates:
                result.errors.append("No companies found matching criteria")
                return result
            
            # Step 2: Verify URLs and refine data
            if verify_urls:
                self._verify_urls(candidates)
                self._refine_candidates(candidates, criteria)
                result.candidates_verified = sum(1 for c in candidates if c.url_verified)
                
                logger.info(
                    "urls_verified",
                    task_id=task_id,
                    verified=result.candidates_verified,
                )
            else:
                # Mark all as verified if skipping
                for c in candidates:
                    c.url_verified = True
                result.candidates_verified = len(candidates)
            
            # Step 3: Deduplicate
            if deduplicate:
                self._deduplicate(candidates)
                result.duplicates_found = sum(1 for c in candidates if c.is_duplicate)
                result.candidates_deduplicated = len(candidates) - result.duplicates_found
                
                logger.info(
                    "deduplication_completed",
                    task_id=task_id,
                    duplicates=result.duplicates_found,
                )
            else:
                result.candidates_deduplicated = len(candidates)
            
            # Step 4: Create records
            if create_records and not dry_run:
                new_candidates = result.get_new_candidates()
                
                for candidate in new_candidates:
                    try:
                        company_id, bu_id = self._create_records(candidate)
                        candidate.created_company_id = company_id
                        candidate.created_bu_id = bu_id
                        result.companies_created.append(company_id)
                        result.bus_created.append(bu_id)
                        result.candidates_created += 1
                    except AirtableError as e:
                        logger.error(
                            "record_creation_failed",
                            task_id=task_id,
                            company=candidate.name,
                            error=str(e),
                        )
                
                logger.info(
                    "records_created",
                    task_id=task_id,
                    companies=result.candidates_created,
                )
            
            result.success = True
            
        except GeminiError as e:
            logger.error(
                "search_gemini_error",
                task_id=task_id,
                error=str(e),
            )
            result.errors.append(f"Gemini error: {e}")
            
        except Exception as e:
            logger.error(
                "search_unexpected_error",
                task_id=task_id,
                error=str(e),
                exc_info=True,
            )
            result.errors.append(f"Unexpected error: {e}")
        
        result.processing_time_seconds = (datetime.now() - start_time).total_seconds()
        
        logger.info(
            "company_search_completed",
            task_id=task_id,
            success=result.success,
            candidates_found=len(result.candidates_found),
            companies_created=result.candidates_created,
            processing_time=result.processing_time_seconds,
        )
        
        return result
    
    def _build_search_query(self, criteria: SearchCriteria) -> str:
        """Build a search query optimized for Gemini.
        
        Args:
            criteria: Search criteria
            
        Returns:
            Formatted search query string
        """
        # Get country name
        country_name = self._get_country_name(criteria.country) if criteria.country else None
        
        # Build main query - be very explicit about country
        if criteria.sector and country_name:
            query = f"Busca {criteria.limit} empresas del sector {criteria.sector} que estén ubicadas en {country_name}"
        elif criteria.sector:
            query = f"Busca {criteria.limit} empresas del sector {criteria.sector}"
        elif country_name:
            query = f"Busca {criteria.limit} empresas ubicadas en {country_name}"
        else:
            query = f"Busca {criteria.limit} empresas"
        
        # Add region if specified
        if criteria.region:
            query += f", específicamente en la región de {criteria.region}"
        
        # Add size filter
        if criteria.min_employees:
            query += f", con más de {criteria.min_employees} empleados"
        
        # Add keywords
        if criteria.keywords:
            query += f", especializadas en {', '.join(criteria.keywords)}"
        
        # Emphasize country requirement
        if country_name:
            query += f". IMPORTANTE: Solo empresas con sede en {country_name} (código de país: {criteria.country})"
        
        query += ". Solo empresas reales con sitio web verificable."
        
        return query
    
    def _get_country_name(self, country_code: str) -> str:
        """Convert country code to full name.
        
        Args:
            country_code: ISO country code (e.g., "ES")
            
        Returns:
            Full country name in Spanish
        """
        country_names = {
            "ES": "España",
            "PT": "Portugal",
            "FR": "Francia",
            "DE": "Alemania",
            "IT": "Italia",
            "UK": "Reino Unido",
            "GB": "Reino Unido",
            "IE": "Irlanda",
            "NL": "Países Bajos",
            "BE": "Bélgica",
            "CH": "Suiza",
            "AT": "Austria",
            "PL": "Polonia",
            "SE": "Suecia",
            "NO": "Noruega",
            "DK": "Dinamarca",
            "FI": "Finlandia",
            "US": "Estados Unidos",
            "CA": "Canadá",
            "MX": "México",
            "BR": "Brasil",
            "AR": "Argentina",
            "CL": "Chile",
            "CO": "Colombia",
            "PE": "Perú",
        }
        return country_names.get(country_code.upper(), country_code)
    
    def _search_companies(
        self,
        query: str,
        limit: int,
    ) -> list[CompanyCandidate]:
        """Search for companies using Gemini.
        
        Args:
            query: Search query string
            limit: Maximum results to return
            
        Returns:
            List of CompanyCandidate objects
        """
        prompt = f"""
{query}

REQUISITOS ESTRICTOS:
1. Encuentra EXACTAMENTE {limit} empresas diferentes (o todas las que existan si hay menos)
2. TODAS las empresas DEBEN estar ubicadas en el país especificado en la búsqueda
3. NO incluir empresas de otros países

Para cada empresa encontrada, proporciona la información en formato JSON:
{{
            "companies": [
        {{
            "name": "Nombre exacto de la empresa",
            "home_url": "https://www.ejemplo.com",
            "linkedin_url": "https://www.linkedin.com/company/...",
            "description": "Breve descripción de la actividad",
            "sector": "Sector de actividad",
            "country": "Código de país ISO (ES, IE, PT, DE, etc.)",
            "region": "Región o ciudad",
            "estimated_employees": 100
        }}
    ]
}}

REGLAS:
- Solo empresas REALES con sitio web verificable
- La URL debe ser la página principal de la empresa
- NO inventar empresas ni URLs
- Incluir las {limit} empresas más relevantes del sector
- El código de país DEBE coincidir con el país solicitado
"""
        
        try:
            # Use search grounding to find real companies
            search_result = self._gemini.search_and_generate(
                query=prompt,
                system_prompt=self._system_prompt,
            )
            
            # Parse response as JSON
            response_text = search_result.get("response", "")
            
            # Try to extract JSON from response
            json_data = self._gemini.generate_json(
                prompt=f"""
Extract the company information from this text and return as JSON:

{response_text}

Return ONLY valid JSON in this exact format:
{{
            "companies": [
        {{
            "name": "Company Name",
            "home_url": "https://...",
            "linkedin_url": "https://www.linkedin.com/company/...",
            "description": "...",
            "sector": "...",
            "country": "ES",
            "region": "...",
            "estimated_employees": 50
        }}
    ]
}}
""",
            )
            
            companies = json_data.get("companies", [])
            
            candidates = []
            for company_data in companies[:limit]:
                candidate = CompanyCandidate(
                    name=company_data.get("name", "Unknown"),
                    home_url=company_data.get("home_url"),
                    linkedin_url=company_data.get("linkedin_url"),
                    description=company_data.get("description"),
                    sector=company_data.get("sector"),
                    country=company_data.get("country"),
                    region=company_data.get("region"),
                    estimated_employees=company_data.get("estimated_employees"),
                )
                candidates.append(candidate)
            
            return candidates
            
        except GeminiError:
            raise
        except Exception as e:
            logger.error("search_parsing_error", error=str(e))
            return []
    
    def _verify_urls(self, candidates: list[CompanyCandidate]) -> None:
        """Verify that company URLs are accessible.
        
        Makes HEAD requests to verify URLs exist.
        Updates url_verified field on each candidate.
        
        Args:
            candidates: List of candidates to verify
        """
        for candidate in candidates:
            verified, final_url = self._verify_single_url(candidate.home_url)
            candidate.url_verified = verified
            if final_url:
                candidate.home_url = final_url

    def _normalize_url(self, url: Optional[str]) -> Optional[str]:
        """Normalize URL for verification."""
        if not url:
            return None
        cleaned = url.strip()
        if not cleaned:
            return None
        if not cleaned.startswith(("http://", "https://")):
            cleaned = f"https://{cleaned}"
        return cleaned.rstrip("/")

    def _verify_single_url(self, url: Optional[str]) -> tuple[bool, Optional[str]]:
        """Verify a single URL and return (is_valid, final_url)."""
        normalized = self._normalize_url(url)
        if not normalized:
            return False, None
        try:
            with httpx.Client(timeout=URL_TIMEOUT_SECONDS, follow_redirects=True) as client:
                response = client.head(normalized)
                if response.status_code >= 400:
                    response = client.get(normalized)
                is_valid = response.status_code < 400
                final_url = str(response.url) if is_valid else normalized
                return is_valid, final_url
        except Exception as e:
            logger.debug(
                "url_verification_failed",
                url=normalized,
                error=str(e),
            )
            return False, normalized

    def _is_probable_official_url(self, company_name: str, url: Optional[str]) -> bool:
        """Check whether a URL likely belongs to the company."""
        if not url or not company_name:
            return False
        domain = self._extract_domain(url) or ""
        if not domain:
            return False
        name = re.sub(r"[^\w\s]", " ", company_name.lower())
        name = re.sub(r"\b(s\.l\.|sl|s\.a\.|sa|ltd|inc|gmbh|bv|srl|plc|llc)\b", "", name)
        tokens = [t for t in name.split() if len(t) >= 3]
        if not tokens:
            return True
        return any(token in domain for token in tokens)

    def _resolve_official_url(
        self,
        company_name: str,
        country: Optional[str],
        region: Optional[str],
    ) -> dict[str, Any]:
        """Find official website and key metadata for a company."""
        country_name = self._get_country_name(country) if country else None
        region_text = f" en {region}" if region else ""
        location_hint = f"{country_name}{region_text}" if country_name else ""

        prompt = f"""
Encuentra el sitio web OFICIAL de la empresa "{company_name}" {f"({location_hint})" if location_hint else ""}.
Devuelve SOLO un JSON con esta estructura:
{{
  "website": "https://www.ejemplo.com",
  "linkedin_url": "https://www.linkedin.com/company/...",
  "description": "Descripción breve",
  "sector": "Sector",
  "country": "{country or ''}",
  "region": "{region or ''}",
  "estimated_employees": 100
}}

REGLAS:
- Usa SOLO el sitio web oficial (dominio propio).
- Si hay dudas, devuelve el candidato más probable.
"""
        response = self._gemini.search_and_generate(
            query=prompt,
            system_prompt=self._system_prompt,
        )
        result = self._gemini.generate_json(
            prompt=f"Extrae y devuelve SOLO el JSON:\n\n{response.get('response', '')}",
        )
        return result if isinstance(result, dict) else {}

    def _refine_candidates(
        self,
        candidates: list[CompanyCandidate],
        criteria: SearchCriteria,
    ) -> None:
        """Improve URLs and metadata using additional verification/search."""
        for candidate in candidates:
            needs_url = not candidate.home_url or not candidate.url_verified
            plausible_url = self._is_probable_official_url(candidate.name, candidate.home_url)
            needs_profile = not candidate.description or not candidate.sector or not candidate.estimated_employees
            needs_linkedin = not candidate.linkedin_url

            if not needs_url and plausible_url and not needs_profile and not needs_linkedin:
                continue

            try:
                profile = self._resolve_official_url(
                    company_name=candidate.name,
                    country=criteria.country,
                    region=criteria.region,
                )
            except Exception as e:
                logger.debug("url_resolution_failed", company=candidate.name, error=str(e))
                continue

            website = profile.get("website")
            linkedin_url = profile.get("linkedin_url")
            description = profile.get("description")
            sector = profile.get("sector")
            region = profile.get("region")
            employees = profile.get("estimated_employees")

            if website:
                verified, final_url = self._verify_single_url(website)
                candidate.url_verified = verified
                if final_url:
                    candidate.home_url = final_url

            if linkedin_url and not candidate.linkedin_url:
                candidate.linkedin_url = linkedin_url
            if description and not candidate.description:
                candidate.description = description
            if sector and not candidate.sector:
                candidate.sector = sector
            if region and not candidate.region:
                candidate.region = region
            if employees and not candidate.estimated_employees:
                candidate.estimated_employees = employees
    
    def _deduplicate(self, candidates: list[CompanyCandidate]) -> None:
        """Check candidates against existing companies in database.
        
        Updates is_duplicate and duplicate_of fields on candidates.
        
        Deduplication criteria:
        - Exact name match (case insensitive)
        - Same domain
        - Name similarity > 90%
        
        Args:
            candidates: List of candidates to deduplicate
        """
        # Get existing companies for comparison
        try:
            existing_companies = self._airtable.query_records(
                table_name="companies",
                max_records=1000,
            )
        except AirtableError as e:
            logger.error("dedupe_query_failed", error=str(e))
            return
        
        # Build lookup structures
        existing_names = {}
        existing_domains = {}
        
        for record in existing_companies:
            fields = record.get("fields", {})
            company_id = record["id"]
            
            # Name lookup (lowercase)
            name = fields.get("Company Name", "").lower().strip()
            if name:
                existing_names[name] = company_id
            
            # Domain lookup
            home_url = fields.get("Home URL") or fields.get("Home_URL", "")
            if home_url:
                domain = self._extract_domain(home_url)
                if domain:
                    existing_domains[domain] = company_id
        
        # Check each candidate
        for candidate in candidates:
            # Skip if already marked
            if candidate.is_duplicate:
                continue
            
            candidate_name = candidate.name.lower().strip()
            candidate_domain = candidate.get_domain()
            
            # Check exact name match
            if candidate_name in existing_names:
                candidate.is_duplicate = True
                candidate.duplicate_of = existing_names[candidate_name]
                continue
            
            # Check domain match
            if candidate_domain and candidate_domain in existing_domains:
                candidate.is_duplicate = True
                candidate.duplicate_of = existing_domains[candidate_domain]
                continue
            
            # Check name similarity
            for existing_name, company_id in existing_names.items():
                similarity = SequenceMatcher(None, candidate_name, existing_name).ratio()
                if similarity >= SIMILARITY_THRESHOLD:
                    candidate.is_duplicate = True
                    candidate.duplicate_of = company_id
                    break
    
    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL.
        
        Args:
            url: URL string
            
        Returns:
            Domain without www prefix, or None
        """
        try:
            parsed = urlparse(url if url.startswith(("http://", "https://")) else f"https://{url}")
            domain = parsed.netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            return domain if domain else None
        except Exception:
            return None
    
    def _create_records(self, candidate: CompanyCandidate) -> tuple[str, str]:
        """Create Company and Business Unit records.
        
        Args:
            candidate: Verified, non-duplicate candidate
            
        Returns:
            Tuple of (company_id, bu_id)
        """
        # Create Company record
        # NOTE: Only use writable fields from Stakeholders_Companies table
        # - Sector is a Rollup (read-only, populated from Business Units)
        # - HQ Country is a Link (would need record ID)
        company_fields = {
            "Company Name": candidate.name,
            "Source": DEFAULT_SOURCE,
        }
        
        if candidate.home_url:
            company_fields["Home URL"] = candidate.home_url
        
        if candidate.description:
            company_fields["Description"] = candidate.description
        
        # Num Employees is a Number field (with space, not underscore)
        if candidate.estimated_employees:
            company_fields["Num Employees"] = candidate.estimated_employees
        
        company_record = self._airtable.create_record("companies", company_fields)
        company_id = company_record["id"]
        
        # Create default Business Unit
        # NOTE: Sector and Focus Countries are Link fields (would need record IDs)
        # For now, just create with basic fields
        bu_fields = {
            "Business Unit Name": DEFAULT_BU_NAME,
            "Company": [company_id],
        }
        
        bu_record = self._airtable.create_record("business_units", bu_fields)
        bu_id = bu_record["id"]
        
        logger.debug(
            "company_created",
            company_id=company_id,
            bu_id=bu_id,
            name=candidate.name,
        )
        
        return company_id, bu_id


# ==============================================================================
# FACTORY FUNCTIONS
# ==============================================================================

_agent: Optional[BuscadorEmpresas] = None


def get_buscador() -> BuscadorEmpresas:
    """Get shared BuscadorEmpresas instance.
    
    Returns:
        Singleton BuscadorEmpresas instance
    """
    global _agent
    if _agent is None:
        _agent = BuscadorEmpresas()
    return _agent

