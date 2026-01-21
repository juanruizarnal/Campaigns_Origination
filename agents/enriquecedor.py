"""Agente Enriquecedor de Datos for Alter-5 Origination Engine.

This module implements the EnriquecedorDatos agent (Agent 2) which enriches
company data by searching the web for missing information using:
- Playwright web scraping for company websites
- Proxycurl for LinkedIn data
- Gemini search grounding for additional information

The agent can:
- Complete basic company data (employees, description, LinkedIn)
- Extract certifications for FEI eligibility (ISO 14001, B Corp, etc.)
- Extract financial information (revenue, EBITDA, debt)
- Identify key persons (CEO, CFO, executives)
- Create contacts and financial records in Airtable

Usage:
    from agents.enriquecedor import EnriquecedorDatos
    
    agent = EnriquecedorDatos()
    result = agent.enrich_company("recXXXXXX")
"""

import asyncio
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Optional
import uuid

import structlog

from config.airtable_schema import (
    COMPANY_FIELDS,
    CONTACT_FIELDS,
    FINANCIALS_FIELDS,
    BUSINESS_UNIT_FIELDS,
)
from config.prompts import load_prompt
from core.airtable_client import AirtableClient, AirtableError, get_airtable_client
from core.async_utils import run_async
from core.models import (
    Company,
    Contact,
    KeyPerson,
    ScrapedCompanyData,
    ScrapedContact,
    LinkedInCompanyData,
    LinkedInPersonData,
)
from integrations.gemini import GeminiClient, GeminiError, get_gemini_client
from integrations.scraper import PlaywrightScraper, scrape_company, has_fei_certificate
from integrations.proxycurl import ProxycurlClient, find_company_linkedin

logger = structlog.get_logger()


# ==============================================================================
# DATA CLASSES
# ==============================================================================

@dataclass
class CompanyInfo:
    """Information extracted about a company."""
    num_employees: Optional[int] = None
    linkedin_url: Optional[str] = None
    description: Optional[str] = None
    hq_address: Optional[str] = None
    sector: Optional[str] = None
    founded_year: Optional[int] = None
    
    # NEW: Data from scraping
    activities: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    green_indicators: list[str] = field(default_factory=list)
    
    # NEW: LinkedIn data
    linkedin_description: Optional[str] = None
    linkedin_specialties: list[str] = field(default_factory=list)
    linkedin_posts: list[str] = field(default_factory=list)
    
    def has_data(self) -> bool:
        """Check if any data was extracted."""
        return any([
            self.num_employees,
            self.linkedin_url,
            self.description,
            self.hq_address,
            self.sector,
            self.certifications,
        ])
    
    def has_fei_relevant_data(self) -> bool:
        """Check if we have data relevant for FEI evaluation."""
        return bool(self.certifications or self.green_indicators)


@dataclass
class FinancialInfo:
    """Financial information extracted about a company."""
    annual_revenues: Optional[float] = None
    ebitda: Optional[float] = None
    net_financial_debt: Optional[float] = None
    year: Optional[int] = None
    currency: str = "EUR"
    source: Optional[str] = None
    
    def has_data(self) -> bool:
        """Check if any financial data was extracted."""
        return self.annual_revenues is not None or self.ebitda is not None


@dataclass
class KeyPersonInfo:
    """Information about a key person (executive)."""
    first_name: str
    last_name: str
    role: str
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    is_key_person: bool = True


@dataclass
class EnrichmentResult:
    """Result of company enrichment operation."""
    company_id: str
    success: bool
    company_info: Optional[CompanyInfo] = None
    financial_info: Optional[FinancialInfo] = None
    key_persons: list[KeyPersonInfo] = field(default_factory=list)
    contacts_created: int = 0
    financials_created: bool = False
    errors: list[str] = field(default_factory=list)
    processing_time_seconds: float = 0.0
    
    # NEW: Source tracking
    scraped_data: Optional[ScrapedCompanyData] = None
    linkedin_data: Optional[LinkedInCompanyData] = None
    data_sources: list[str] = field(default_factory=list)
    
    # NEW: FEI relevant
    certifications_found: list[str] = field(default_factory=list)
    has_fei_certificate: bool = False
    
    def __str__(self) -> str:
        status = "✅" if self.success else "❌"
        fei_status = "🟢 FEI" if self.has_fei_certificate else ""
        return (
            f"{status} Enrichment for {self.company_id}: "
            f"info={'yes' if self.company_info and self.company_info.has_data() else 'no'}, "
            f"financials={'yes' if self.financial_info and self.financial_info.has_data() else 'no'}, "
            f"contacts={self.contacts_created}, "
            f"certs={len(self.certifications_found)} {fei_status}"
        )


# ==============================================================================
# ENRIQUECEDOR DATOS AGENT
# ==============================================================================

class EnriquecedorDatos:
    """Agent for enriching company data from multiple sources.
    
    Uses multiple data sources for comprehensive enrichment:
    - Playwright scraping for company websites (certifications, contacts)
    - Proxycurl for LinkedIn data (employees, posts, executives)
    - Gemini search grounding for additional information
    
    Critical for FEI evaluation:
    - Extracts certifications (ISO 14001, B Corp, EMAS, etc.)
    - Identifies green/sustainability indicators
    
    Example:
        agent = EnriquecedorDatos()
        result = agent.enrich_company("recXXXXXX")
        
        if result.success:
            print(f"Enriched {result.company_id}")
            print(f"- Employees: {result.company_info.num_employees}")
            print(f"- Certifications: {result.certifications_found}")
            print(f"- FEI eligible: {result.has_fei_certificate}")
    """
    
    def __init__(
        self,
        airtable_client: Optional[AirtableClient] = None,
        gemini_client: Optional[GeminiClient] = None,
        use_scraping: bool = True,
        use_linkedin: bool = True,
    ):
        """Initialize the EnriquecedorDatos agent.
        
        Args:
            airtable_client: Optional custom Airtable client
            gemini_client: Optional custom Gemini client
            use_scraping: Whether to use Playwright scraping
            use_linkedin: Whether to use Proxycurl for LinkedIn
        """
        self._airtable = airtable_client or get_airtable_client()
        self._gemini = gemini_client or get_gemini_client()
        self._system_prompt = load_prompt("enriquecedor")
        self._use_scraping = use_scraping
        self._use_linkedin = use_linkedin
        
        logger.info(
            "enriquecedor_datos_initialized",
            use_scraping=use_scraping,
            use_linkedin=use_linkedin,
        )
    
    def enrich_company(
        self,
        company_id: str,
        include_financials: bool = True,
        include_contacts: bool = True,
        include_scraping: bool = True,
        include_linkedin: bool = True,
        dry_run: bool = False,
    ) -> EnrichmentResult:
        """Enrich a company with additional data from multiple sources.
        
        This is a sync wrapper that safely runs the async implementation.
        """
        return run_async(
            self._enrich_company_async(
                company_id=company_id,
                include_financials=include_financials,
                include_contacts=include_contacts,
                include_scraping=include_scraping,
                include_linkedin=include_linkedin,
                dry_run=dry_run,
            )
        )

    def enrich(
        self,
        company_id: str,
        dry_run: bool = False,
        include_financials: bool = True,
        include_contacts: bool = True,
        include_scraping: bool = True,
        include_linkedin: bool = True,
    ) -> EnrichmentResult:
        """Backward-compatible alias for enrich_company."""
        return self.enrich_company(
            company_id=company_id,
            include_financials=include_financials,
            include_contacts=include_contacts,
            include_scraping=include_scraping,
            include_linkedin=include_linkedin,
            dry_run=dry_run,
        )

    async def _enrich_company_async(
        self,
        company_id: str,
        include_financials: bool = True,
        include_contacts: bool = True,
        include_scraping: bool = True,
        include_linkedin: bool = True,
        dry_run: bool = False,
    ) -> EnrichmentResult:
        """Enrich a company with additional data from multiple sources.
        
        Args:
            company_id: Airtable record ID of the company
            include_financials: Whether to search for financial data
            include_contacts: Whether to search for key persons
            include_scraping: Whether to scrape the company website
            include_linkedin: Whether to fetch LinkedIn data
            dry_run: If True, don't save changes to Airtable
            
        Returns:
            EnrichmentResult with all extracted data and operation status
        """
        start_time = datetime.now()
        task_id = str(uuid.uuid4())[:8]
        
        logger.info(
            "enrichment_started",
            task_id=task_id,
            company_id=company_id,
            include_financials=include_financials,
            include_contacts=include_contacts,
            include_scraping=include_scraping,
            include_linkedin=include_linkedin,
            dry_run=dry_run,
        )
        
        result = EnrichmentResult(company_id=company_id, success=False)
        
        try:
            # 1. Get company from Airtable
            company_record = self._airtable.get_record("companies", company_id)
            company_name = company_record.get("fields", {}).get("Company Name", "")
            company_url = company_record.get("fields", {}).get("Home URL", "")
            existing_linkedin = company_record.get("fields", {}).get("Linkedin URL", "")
            
            if not company_name:
                result.errors.append("Company name is empty")
                return result
            
            logger.info(
                "enrichment_company_loaded",
                task_id=task_id,
                company_name=company_name,
                company_url=company_url,
            )
            
            # Initialize company_info
            company_info = CompanyInfo()
            
            # 2. NEW: Scrape company website (critical for FEI)
            if include_scraping and self._use_scraping and company_url:
                try:
                    scraped_data = await scrape_company(company_url)
                    result.scraped_data = scraped_data
                    result.data_sources.append("web_scraping")
                    
                    if scraped_data.success:
                        # Extract FEI-relevant data
                        company_info.certifications = scraped_data.certifications
                        company_info.green_indicators = scraped_data.green_indicators
                        company_info.activities = scraped_data.activities
                        
                        result.certifications_found = scraped_data.certifications
                        result.has_fei_certificate = has_fei_certificate(scraped_data)
                        
                        # Use scraped data if not available elsewhere
                        if scraped_data.employee_count:
                            company_info.num_employees = scraped_data.employee_count
                        if scraped_data.description:
                            company_info.description = scraped_data.description
                        if scraped_data.linkedin_url and not existing_linkedin:
                            company_info.linkedin_url = scraped_data.linkedin_url
                        
                        logger.info(
                            "scraping_complete",
                            task_id=task_id,
                            certifications=len(scraped_data.certifications),
                            green_indicators=len(scraped_data.green_indicators),
                            has_fei=result.has_fei_certificate,
                        )
                except Exception as e:
                    logger.warning("scraping_failed", task_id=task_id, error=str(e))
                    result.errors.append(f"Scraping failed: {e}")
            
            # 3. NEW: Fetch LinkedIn data
            linkedin_url = existing_linkedin or company_info.linkedin_url
            if include_linkedin and self._use_linkedin:
                try:
                    # Find LinkedIn URL if we don't have it
                    if not linkedin_url:
                        linkedin_url = await find_company_linkedin(company_name)
                        if linkedin_url:
                            company_info.linkedin_url = linkedin_url
                    
                    if linkedin_url:
                        async with ProxycurlClient() as client:
                            linkedin_data = await client.get_company_profile(linkedin_url)
                            
                        if linkedin_data:
                            result.linkedin_data = linkedin_data
                            result.data_sources.append("linkedin")
                            
                            # Merge LinkedIn data
                            if linkedin_data.employee_count and not company_info.num_employees:
                                company_info.num_employees = linkedin_data.employee_count
                            if linkedin_data.description:
                                company_info.linkedin_description = linkedin_data.description
                                if not company_info.description:
                                    company_info.description = linkedin_data.description
                            if linkedin_data.industry and not company_info.sector:
                                company_info.sector = linkedin_data.industry
                            if linkedin_data.specialties:
                                company_info.linkedin_specialties = linkedin_data.specialties
                            if linkedin_data.recent_posts:
                                company_info.linkedin_posts = linkedin_data.recent_posts
                            
                            logger.info(
                                "linkedin_data_fetched",
                                task_id=task_id,
                                employees=linkedin_data.employee_count,
                                has_posts=bool(linkedin_data.recent_posts),
                            )
                except Exception as e:
                    logger.warning("linkedin_fetch_failed", task_id=task_id, error=str(e))
                    result.errors.append(f"LinkedIn fetch failed: {e}")
            
            # 4. Use Gemini for additional info (fallback/complement)
            gemini_info = self._search_company_info(company_name, company_url)
            
            # Merge Gemini data (only fill gaps)
            if gemini_info.num_employees and not company_info.num_employees:
                company_info.num_employees = gemini_info.num_employees
            if gemini_info.description and not company_info.description:
                company_info.description = gemini_info.description
            if gemini_info.linkedin_url and not company_info.linkedin_url:
                company_info.linkedin_url = gemini_info.linkedin_url
            if gemini_info.hq_address and not company_info.hq_address:
                company_info.hq_address = gemini_info.hq_address
            if gemini_info.sector and not company_info.sector:
                company_info.sector = gemini_info.sector
            if gemini_info.founded_year:
                company_info.founded_year = gemini_info.founded_year
            
            result.data_sources.append("gemini")
            result.company_info = company_info
            
            # 5. Search for financial data
            if include_financials:
                financial_info = self._extract_financials(company_name, company_url, result.scraped_data)
                result.financial_info = financial_info
            
            # 6. Search for key persons
            if include_contacts:
                key_persons = self._identify_key_persons(company_name, company_url, result.scraped_data)
                result.key_persons = key_persons
            
            # 7. Save results to Airtable
            if not dry_run:
                self._save_results(
                    company_id=company_id,
                    company_record=company_record,
                    company_info=result.company_info,
                    financial_info=result.financial_info,
                    key_persons=result.key_persons,
                    result=result,
                )
            
            result.success = True
            
        except AirtableError as e:
            logger.error(
                "enrichment_airtable_error",
                task_id=task_id,
                company_id=company_id,
                error=str(e),
            )
            result.errors.append(f"Airtable error: {e}")
            
        except GeminiError as e:
            logger.error(
                "enrichment_gemini_error",
                task_id=task_id,
                company_id=company_id,
                error=str(e),
            )
            result.errors.append(f"Gemini error: {e}")
            
        except Exception as e:
            logger.error(
                "enrichment_unexpected_error",
                task_id=task_id,
                company_id=company_id,
                error=str(e),
                exc_info=True,
            )
            result.errors.append(f"Unexpected error: {e}")
        
        # Calculate processing time
        result.processing_time_seconds = (datetime.now() - start_time).total_seconds()
        
        logger.info(
            "enrichment_completed",
            task_id=task_id,
            company_id=company_id,
            success=result.success,
            has_company_info=result.company_info is not None and result.company_info.has_data(),
            has_financials=result.financial_info is not None and result.financial_info.has_data(),
            contacts_found=len(result.key_persons),
            contacts_created=result.contacts_created,
            certifications_found=len(result.certifications_found),
            has_fei_certificate=result.has_fei_certificate,
            data_sources=result.data_sources,
            processing_time=result.processing_time_seconds,
        )
        
        return result
    
    def _search_company_info(
        self,
        company_name: str,
        company_url: Optional[str],
    ) -> CompanyInfo:
        """Search for basic company information using Gemini.
        
        Args:
            company_name: Name of the company
            company_url: Company website URL (optional)
            
        Returns:
            CompanyInfo with extracted data
        """
        logger.debug(
            "searching_company_info",
            company_name=company_name,
        )
        
        # Build search query - more specific for better results
        query = f"""
Busca información VERIFICABLE sobre la empresa "{company_name}".
{f'Su sitio web oficial es: {company_url}' if company_url else ''}

INSTRUCCIONES IMPORTANTES:
1. Busca en fuentes OFICIALES: LinkedIn, página de la empresa, registros mercantiles, memorias anuales
2. NO inventes datos. Si no encuentras información fiable, indica null
3. Los empleados deben ser datos reales de LinkedIn o fuentes oficiales
4. La descripción debe ser objetiva y basada en información de la empresa

Información a buscar:
1. Número de empleados (de LinkedIn o fuentes oficiales)
2. URL del perfil de empresa en LinkedIn (formato: linkedin.com/company/xxx)
3. Descripción breve de la actividad principal (2-3 oraciones)
4. Dirección de la sede central (ciudad, país)
5. Sector/industria principal (clasificación GICS o similar)
6. Año de fundación

Devuelve ÚNICAMENTE un objeto JSON con esta estructura exacta:
{{
    "num_employees": <número entero o null si no disponible>,
    "linkedin_url": "<URL completa de LinkedIn o null>",
    "description": "<descripción objetiva o null>",
    "hq_address": "<ciudad, país o null>",
    "sector": "<sector principal o null>",
    "founded_year": <año como número o null>
}}

CRÍTICO: Solo incluye datos que puedas verificar. Es mejor null que un dato inventado.
"""
        
        try:
            response = self._gemini.search_and_generate(
                query=query,
                system_prompt=self._system_prompt,
            )
            
            # Parse JSON response
            result = self._gemini.generate_json(
                prompt=f"Extract a JSON object from this text. Only return valid JSON:\n\n{response['response']}",
            )
            
            return CompanyInfo(
                num_employees=result.get("num_employees"),
                linkedin_url=result.get("linkedin_url"),
                description=result.get("description"),
                hq_address=result.get("hq_address"),
                sector=result.get("sector"),
                founded_year=result.get("founded_year"),
            )
            
        except (GeminiError, KeyError, TypeError) as e:
            logger.warning(
                "company_info_search_failed",
                company_name=company_name,
                error=str(e),
            )
            return CompanyInfo()
    
    def _extract_financials(
        self,
        company_name: str,
        company_url: Optional[str],
        scraped_data: Optional[ScrapedCompanyData] = None,
    ) -> FinancialInfo:
        """Search for company financial information.
        
        Args:
            company_name: Name of the company
            company_url: Company website URL (optional)
            
        Returns:
            FinancialInfo with extracted data
        """
        logger.debug(
            "extracting_financials",
            company_name=company_name,
        )
        
        current_year = date.today().year
        
        query = f"""
Busca información financiera OFICIAL y VERIFICABLE de la empresa "{company_name}".
{f'Sitio web: {company_url}' if company_url else ''}

FUENTES PRIORITARIAS (buscar en este orden):
1. Cuentas anuales depositadas en Registro Mercantil (España: SABI, Francia: Infogreffe, etc.)
2. Memorias anuales o informes financieros publicados en la web de la empresa
3. Base de datos empresariales (Dun & Bradstreet, Bureau van Dijk, etc.)
4. Artículos de prensa económica con datos verificados
5. LinkedIn (para tamaño de empresa)

DATOS A BUSCAR (años {current_year-3} a {current_year}):
1. Ingresos/Facturación anual (en EUR o moneda local)
2. EBITDA (si está disponible)
3. Deuda financiera neta (si está disponible)
4. Año de los datos
5. Fuente de los datos (importante para verificabilidad)

Devuelve ÚNICAMENTE un objeto JSON con esta estructura:
{{
    "annual_revenues": <número en EUR o null si no fiable>,
    "ebitda": <número en EUR o null>,
    "net_financial_debt": <número en EUR o null>,
    "year": <año de los datos como número o null>,
    "currency": "EUR",
    "source": "<nombre de la fuente específica>"
}}

REGLAS CRÍTICAS:
- NO inventes cifras. Si no hay datos públicos fiables, usa null
- Convierte a EUR si es necesario (usa tipo de cambio aproximado del año)
- La fuente debe ser específica (ej: "Memoria Anual 2023", "Registro Mercantil España")
- Los ingresos deben estar en unidades (no millones). Ej: 50000000 para 50M€
- Preferir datos más recientes
"""
        
        # Try to extract from scraped website mentions first (avoid paid APIs)
        if scraped_data and scraped_data.revenue_mentions:
            scraped_financials = self._extract_financials_from_scrape(scraped_data)
            if scraped_financials and scraped_financials.has_data():
                return scraped_financials

        try:
            response = self._gemini.search_and_generate(
                query=query,
                system_prompt=self._system_prompt,
            )
            
            result = self._gemini.generate_json(
                prompt=f"Extract a JSON object from this text. Only return valid JSON:\n\n{response['response']}",
            )
            
            # Validate year is recent
            year = result.get("year")
            if year and (year < current_year - 5 or year > current_year):
                year = None
            
            # Convert revenues to proper number format if needed
            revenues = result.get("annual_revenues")
            if revenues and isinstance(revenues, str):
                # Handle "50M" or "50.5M" format
                try:
                    revenues = float(revenues.replace("M", "").replace("€", "").strip()) * 1_000_000
                except:
                    revenues = None
            
            ebitda = result.get("ebitda")
            if ebitda and isinstance(ebitda, str):
                try:
                    ebitda = float(ebitda.replace("M", "").replace("€", "").strip()) * 1_000_000
                except:
                    ebitda = None
            
            return FinancialInfo(
                annual_revenues=revenues,
                ebitda=ebitda,
                net_financial_debt=result.get("net_financial_debt"),
                year=year,
                currency=result.get("currency", "EUR"),
                source=result.get("source"),
            )
            
        except (GeminiError, KeyError, TypeError) as e:
            logger.warning(
                "financials_extraction_failed",
                company_name=company_name,
                error=str(e),
            )
            return FinancialInfo()

    def _extract_financials_from_scrape(self, scraped_data: ScrapedCompanyData) -> FinancialInfo:
        """Extract financials from scraped revenue mentions."""
        if not scraped_data or not scraped_data.revenue_mentions:
            return FinancialInfo()

        best_revenue = None
        for mention in scraped_data.revenue_mentions:
            amount = self._parse_financial_amount(mention)
            if amount and (best_revenue is None or amount > best_revenue):
                best_revenue = amount

        if best_revenue is None:
            return FinancialInfo()

        return FinancialInfo(
            annual_revenues=best_revenue,
            currency="EUR",
            source="Website",
        )

    def _parse_financial_amount(self, text: str) -> Optional[float]:
        """Parse a numeric amount from text like '50M€' or '50 millones'."""
        if not text:
            return None

        raw = text.lower().replace("€", "").replace("$", "").replace("eur", "").strip()
        match = re.search(r"(\d+(?:[.,]\d+)?)\s*(k|m|b|bn|million|millones|millon|billion)?", raw)
        if not match:
            return None

        value_str = match.group(1).replace(",", ".")
        try:
            value = float(value_str)
        except ValueError:
            return None

        multiplier = match.group(2) or ""
        if multiplier in {"k"}:
            value *= 1_000
        elif multiplier in {"m", "million", "millones", "millon"}:
            value *= 1_000_000
        elif multiplier in {"b", "bn", "billion"}:
            value *= 1_000_000_000

        # Ignore tiny values that look like counts, not revenues
        if value < 10_000:
            return None

        return value
    
    def _identify_key_persons(
        self,
        company_name: str,
        company_url: Optional[str],
        scraped_data: Optional[ScrapedCompanyData] = None,
    ) -> list[KeyPersonInfo]:
        """Identify key persons (executives) at the company.
        
        Args:
            company_name: Name of the company
            company_url: Company website URL (optional)
            
        Returns:
            List of KeyPersonInfo for found executives
        """
        logger.debug(
            "identifying_key_persons",
            company_name=company_name,
        )
        
        # Prefer contacts extracted from the website (free, verifiable)
        if scraped_data and scraped_data.contacts:
            contacts = self._select_key_contacts_from_scrape(scraped_data.contacts)
            if contacts:
                return contacts

        query = f"""
Busca los ejecutivos clave REALES de la empresa "{company_name}".
{f'Sitio web: {company_url}' if company_url else ''}

FUENTES PRIORITARIAS:
1. Página de LinkedIn de la empresa → Sección "Personas"
2. Sección "Equipo" o "About Us" de la web de la empresa
3. Perfiles individuales de LinkedIn
4. Artículos de prensa con nombres verificables

ROLES A BUSCAR (en orden de prioridad):
1. CEO / Consejero Delegado / Director General / Managing Director
2. CFO / Director Financiero / Finance Director
3. COO / Director de Operaciones / Operations Director
4. CCO / Chief Commercial Officer / Director Comercial
5. CTO / Director de Tecnología (si aplica)

PARA CADA PERSONA, BUSCAR:
- Nombre completo (nombre y apellidos reales)
- Cargo/título exacto en la empresa
- URL de su perfil de LinkedIn (verificar que sea la persona correcta)
- Email de contacto (solo si es público)
- Teléfono (solo si es público)

Devuelve ÚNICAMENTE un objeto JSON con esta estructura:
{{
    "key_persons": [
        {{
            "first_name": "<nombre>",
            "last_name": "<apellidos>",
            "role": "<cargo exacto en la empresa>",
            "linkedin_url": "<URL del perfil de LinkedIn o null>",
            "email": "<email profesional o null>",
            "phone": "<teléfono o null>"
        }}
    ]
}}

REGLAS CRÍTICAS:
- Solo incluye personas que puedas VERIFICAR en fuentes públicas
- Los nombres deben ser REALES, no inventados
- El LinkedIn debe ser de la persona correcta en la empresa correcta
- NO inventes emails ni teléfonos. Solo datos públicos verificables
- Máximo 5 personas, priorizando C-suite
"""
        
        try:
            response = self._gemini.search_and_generate(
                query=query,
                system_prompt=self._system_prompt,
            )
            
            result = self._gemini.generate_json(
                prompt=f"Extract a JSON object from this text. Only return valid JSON:\n\n{response['response']}",
            )
            
            key_persons = []
            for person_data in result.get("key_persons", []):
                if person_data.get("first_name") and person_data.get("last_name"):
                    # Validate LinkedIn URL format
                    linkedin = person_data.get("linkedin_url")
                    if linkedin and "linkedin.com" not in linkedin:
                        linkedin = None
                    
                    key_persons.append(KeyPersonInfo(
                        first_name=person_data["first_name"],
                        last_name=person_data["last_name"],
                        role=person_data.get("role", "Executive"),
                        email=person_data.get("email"),
                        phone=person_data.get("phone"),
                        linkedin_url=linkedin,
                        is_key_person=True,
                    ))
            
            return key_persons[:5]  # Max 5 contacts
            
        except (GeminiError, KeyError, TypeError) as e:
            logger.warning(
                "key_persons_identification_failed",
                company_name=company_name,
                error=str(e),
            )
            return []

    def _select_key_contacts_from_scrape(self, contacts: list[ScrapedContact]) -> list[KeyPersonInfo]:
        """Filter and normalize key contacts from scraped website data."""
        if not contacts:
            return []

        role_keywords = [
            "ceo", "cfo", "coo", "cto", "chief", "director", "president",
            "managing", "partner", "founder", "gerente", "consejero", "executive",
        ]

        key_people: list[KeyPersonInfo] = []
        for contact in contacts:
            role = (contact.role or "").lower()
            if role and not any(k in role for k in role_keywords):
                continue

            first_name, last_name = self._split_name(contact.name or "")
            if not first_name and not contact.email:
                continue

            key_people.append(KeyPersonInfo(
                first_name=first_name or "N/A",
                last_name=last_name or "",
                role=contact.role or "Executive",
                email=contact.email,
                phone=contact.phone,
                linkedin_url=contact.linkedin_url,
                is_key_person=True,
            ))

        return key_people[:5]

    def _split_name(self, full_name: str) -> tuple[str, str]:
        """Split a full name into first and last name parts."""
        name = (full_name or "").strip()
        if not name:
            return "", ""
        parts = name.split()
        if len(parts) == 1:
            return parts[0], ""
        return parts[0], " ".join(parts[1:])
    
    def _save_results(
        self,
        company_id: str,
        company_record: dict,
        company_info: Optional[CompanyInfo],
        financial_info: Optional[FinancialInfo],
        key_persons: list[KeyPersonInfo],
        result: EnrichmentResult,
    ) -> None:
        """Save enrichment results to Airtable.
        
        Args:
            company_id: Company record ID
            company_record: Original company record from Airtable
            company_info: Extracted company information
            financial_info: Extracted financial information
            key_persons: List of key persons found
            result: EnrichmentResult to update with save status
        """
        # 1. Update company record with new info
        if company_info and company_info.has_data():
            update_fields = {}
            
            # Only update fields that are currently empty in Airtable
            existing_fields = company_record.get("fields", {})
            
            if company_info.num_employees:
                existing_employees = existing_fields.get("Num Employees")
                strong_source = "linkedin" in result.data_sources or "web_scraping" in result.data_sources
                should_update = not existing_employees
                if existing_employees and strong_source:
                    try:
                        existing_val = float(existing_employees)
                        new_val = float(company_info.num_employees)
                        if existing_val == 0:
                            should_update = True
                        else:
                            delta = abs(new_val - existing_val) / max(existing_val, 1)
                            should_update = delta >= 0.25
                    except Exception:
                        should_update = True
                if should_update:
                    update_fields["Num Employees"] = company_info.num_employees
            
            if company_info.linkedin_url and not existing_fields.get("Linkedin URL"):
                update_fields["Linkedin URL"] = company_info.linkedin_url
            
            if company_info.description and not existing_fields.get("Description"):
                update_fields["Description"] = company_info.description
            
            if company_info.hq_address and not existing_fields.get("HQ Address"):
                update_fields["HQ Address"] = company_info.hq_address
            
            # NEW: Save scraped content as JSON for future reference
            if result.scraped_data and result.scraped_data.success:
                scraped_summary = {
                    "certifications": result.scraped_data.certifications,
                    "green_indicators": result.scraped_data.green_indicators,
                    "activities": result.scraped_data.activities[:3],
                    "scraped_at": result.scraped_data.scraped_at.isoformat(),
                }
                # Store in a text field if available
                if not existing_fields.get("Scraped_Content"):
                    import json
                    update_fields["Scraped_Content"] = json.dumps(scraped_summary, ensure_ascii=False)
            
            if update_fields:
                try:
                    self._airtable.update_record("companies", company_id, update_fields)
                    logger.info(
                        "company_record_updated",
                        company_id=company_id,
                        fields_updated=list(update_fields.keys()),
                    )
                except AirtableError as e:
                    result.errors.append(f"Failed to update company: {e}")
        
        # 1b. NEW: Create certificate records for FEI tracking
        if company_info and company_info.certifications:
            self._save_certificates(company_id, company_info.certifications, result)
        
        # 2. Create financials record if we have data
        if financial_info and financial_info.has_data():
            existing_fields = company_record.get("fields", {})
            existing_revenues = existing_fields.get("Revenues")
            existing_ebitda = existing_fields.get("EBITDA")
            if isinstance(existing_revenues, list):
                existing_revenues = existing_revenues[0] if existing_revenues else None
            if isinstance(existing_ebitda, list):
                existing_ebitda = existing_ebitda[0] if existing_ebitda else None
            if not (existing_revenues or existing_ebitda):
                try:
                    financial_fields = {
                        "Company": [company_id],  # Link field
                    }

                    if financial_info.year:
                        financial_fields["Year"] = str(financial_info.year)
                    if financial_info.annual_revenues:
                        financial_fields["Annual_Revenues"] = financial_info.annual_revenues
                    if financial_info.ebitda:
                        financial_fields["EBITDA"] = financial_info.ebitda
                    if financial_info.net_financial_debt:
                        financial_fields["Net_Financial_Debt"] = financial_info.net_financial_debt

                    self._airtable.create_record("financials", financial_fields)
                    result.financials_created = True

                    logger.info(
                        "financials_record_created",
                        company_id=company_id,
                        year=financial_info.year,
                    )
                except AirtableError as e:
                    result.errors.append(f"Failed to create financials: {e}")
        
        # 3. Create contact records for key persons
        # First, get or create a business unit for the contacts
        business_unit_id = self._get_or_create_business_unit(company_id, company_record)
        
        for person in key_persons:
            try:
                contact_fields = {
                    "First Name": person.first_name,
                    "Last Name": person.last_name,
                    "Role": person.role,
                    "Key Person": "Yes" if person.is_key_person else "No",
                }
                
                if person.email:
                    contact_fields["Email"] = person.email
                if person.phone:
                    contact_fields["Phone Number"] = person.phone
                if person.linkedin_url:
                    contact_fields["Linkedin URL"] = person.linkedin_url
                
                if business_unit_id:
                    contact_fields["Business Unit"] = [business_unit_id]
                
                self._airtable.create_record("contacts", contact_fields)
                result.contacts_created += 1
                
                logger.info(
                    "contact_created",
                    company_id=company_id,
                    contact_name=f"{person.first_name} {person.last_name}",
                    role=person.role,
                )
            except AirtableError as e:
                result.errors.append(
                    f"Failed to create contact {person.first_name} {person.last_name}: {e}"
                )
    
    def _get_or_create_business_unit(
        self,
        company_id: str,
        company_record: dict,
    ) -> Optional[str]:
        """Get existing business unit or create a default one.
        
        Args:
            company_id: Company record ID
            company_record: Company record from Airtable
            
        Returns:
            Business unit record ID or None
        """
        existing_fields = company_record.get("fields", {})
        
        # Check if company already has business units
        business_units = existing_fields.get("Business Units", [])
        if business_units:
            return business_units[0]  # Return first BU
        
        # Create a default business unit
        try:
            company_name = existing_fields.get("Company Name", "Unknown")
            bu_fields = {
                "Business Unit Name": f"{company_name} - Principal",
                "Company": [company_id],
                "Record Status": "Active",
            }
            
            bu_record = self._airtable.create_record("business_units", bu_fields)
            
            logger.info(
                "default_business_unit_created",
                company_id=company_id,
                bu_id=bu_record["id"],
            )
            
            return bu_record["id"]
            
        except AirtableError as e:
            logger.warning(
                "failed_to_create_business_unit",
                company_id=company_id,
                error=str(e),
            )
            return None
    
    def _save_certificates(
        self,
        company_id: str,
        certifications: list[str],
        result: EnrichmentResult,
    ) -> None:
        """Save certificate records to Airtable.
        
        Args:
            company_id: Company record ID
            certifications: List of certification names found
            result: EnrichmentResult to update with errors
        """
        for cert_name in certifications:
            try:
                # Determine certificate type
                cert_type = "ISO"
                if "B Corp" in cert_name:
                    cert_type = "Eco-label"
                elif "EMAS" in cert_name or "Eco" in cert_name:
                    cert_type = "Eco-label"
                elif "LEED" in cert_name or "BREEAM" in cert_name:
                    cert_type = "Eco-label"
                elif "FSC" in cert_name or "PEFC" in cert_name:
                    cert_type = "Eco-label"
                
                cert_fields = {
                    "Company": [company_id],
                    "Certificate_Type": cert_type,
                    "Certificate_Name": cert_name,
                    "Verified": False,  # Needs manual verification
                    "Source": "Web",
                }
                
                self._airtable.create_record("company_certificates", cert_fields)
                
                logger.info(
                    "certificate_record_created",
                    company_id=company_id,
                    certificate=cert_name,
                )
            except AirtableError as e:
                # Don't fail on certificate creation errors
                logger.warning(
                    "certificate_creation_failed",
                    company_id=company_id,
                    certificate=cert_name,
                    error=str(e),
                )
    
    def enrich_batch(
        self,
        company_ids: list[str],
        include_financials: bool = True,
        include_contacts: bool = True,
        include_scraping: bool = True,
        include_linkedin: bool = True,
        dry_run: bool = False,
        on_progress: Optional[callable] = None,
        max_concurrent: int = 3,
    ) -> list[EnrichmentResult]:
        """Enrich multiple companies with concurrency control.
        
        This is a sync wrapper that safely runs the async implementation.
        """
        return run_async(
            self._enrich_batch_async(
                company_ids=company_ids,
                include_financials=include_financials,
                include_contacts=include_contacts,
                include_scraping=include_scraping,
                include_linkedin=include_linkedin,
                dry_run=dry_run,
                on_progress=on_progress,
                max_concurrent=max_concurrent,
            )
        )

    async def _enrich_batch_async(
        self,
        company_ids: list[str],
        include_financials: bool = True,
        include_contacts: bool = True,
        include_scraping: bool = True,
        include_linkedin: bool = True,
        dry_run: bool = False,
        on_progress: Optional[callable] = None,
        max_concurrent: int = 3,
    ) -> list[EnrichmentResult]:
        """Enrich multiple companies with concurrency control.
        
        Args:
            company_ids: List of company record IDs
            include_financials: Whether to search for financial data
            include_contacts: Whether to search for key persons
            include_scraping: Whether to scrape company websites
            include_linkedin: Whether to fetch LinkedIn data
            dry_run: If True, don't save changes
            on_progress: Optional callback(current, total, result)
            max_concurrent: Maximum concurrent enrichments
            
        Returns:
            List of EnrichmentResult for each company
        """
        results = []
        total = len(company_ids)
        semaphore = asyncio.Semaphore(max_concurrent)
        
        logger.info(
            "batch_enrichment_started",
            total_companies=total,
            include_financials=include_financials,
            include_contacts=include_contacts,
            include_scraping=include_scraping,
            include_linkedin=include_linkedin,
            dry_run=dry_run,
            max_concurrent=max_concurrent,
        )
        
        async def enrich_with_semaphore(company_id: str, index: int) -> EnrichmentResult:
            async with semaphore:
                result = await self._enrich_company_async(
                    company_id=company_id,
                    include_financials=include_financials,
                    include_contacts=include_contacts,
                    include_scraping=include_scraping,
                    include_linkedin=include_linkedin,
                    dry_run=dry_run,
                )
                if on_progress:
                    on_progress(index, total, result)
                return result
        
        # Run all enrichments with concurrency control
        tasks = [
            enrich_with_semaphore(company_id, i + 1)
            for i, company_id in enumerate(company_ids)
        ]
        results = await asyncio.gather(*tasks)
        
        # Log summary
        successful = sum(1 for r in results if r.success)
        contacts_created = sum(r.contacts_created for r in results)
        financials_created = sum(1 for r in results if r.financials_created)
        certs_found = sum(len(r.certifications_found) for r in results)
        fei_eligible = sum(1 for r in results if r.has_fei_certificate)
        
        logger.info(
            "batch_enrichment_completed",
            total=total,
            successful=successful,
            failed=total - successful,
            contacts_created=contacts_created,
            financials_created=financials_created,
            certifications_found=certs_found,
            fei_eligible_count=fei_eligible,
        )
        
        return results


# ==============================================================================
# FACTORY FUNCTIONS
# ==============================================================================

_agent: Optional[EnriquecedorDatos] = None


def get_enriquecedor() -> EnriquecedorDatos:
    """Get shared EnriquecedorDatos instance.
    
    Returns:
        Singleton EnriquecedorDatos instance
    """
    global _agent
    if _agent is None:
        _agent = EnriquecedorDatos()
    return _agent

