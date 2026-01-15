"""Agente Enriquecedor de Datos for Alter-5 Origination Engine.

This module implements the EnriquecedorDatos agent (Agent 2) which enriches
company data by searching the web for missing information using Gemini's
search grounding capabilities.

The agent can:
- Complete basic company data (employees, description, LinkedIn)
- Extract financial information (revenue, EBITDA, debt)
- Identify key persons (CEO, CFO, executives)
- Create contacts and financial records in Airtable

Usage:
    from agents.enriquecedor import EnriquecedorDatos
    
    agent = EnriquecedorDatos()
    result = agent.enrich_company("recXXXXXX")
"""

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
from core.models import Company, Contact, KeyPerson
from integrations.gemini import GeminiClient, GeminiError, get_gemini_client

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
    
    def has_data(self) -> bool:
        """Check if any data was extracted."""
        return any([
            self.num_employees,
            self.linkedin_url,
            self.description,
            self.hq_address,
            self.sector,
        ])


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
    
    def __str__(self) -> str:
        status = "✅" if self.success else "❌"
        return (
            f"{status} Enrichment for {self.company_id}: "
            f"info={'yes' if self.company_info and self.company_info.has_data() else 'no'}, "
            f"financials={'yes' if self.financial_info and self.financial_info.has_data() else 'no'}, "
            f"contacts={self.contacts_created}"
        )


# ==============================================================================
# ENRIQUECEDOR DATOS AGENT
# ==============================================================================

class EnriquecedorDatos:
    """Agent for enriching company data from web sources.
    
    Uses Gemini's search grounding capabilities to find and extract:
    - Basic company information (employees, description, address)
    - Financial data (revenue, EBITDA, debt)
    - Key personnel (executives, decision makers)
    
    Example:
        agent = EnriquecedorDatos()
        result = agent.enrich_company("recXXXXXX")
        
        if result.success:
            print(f"Enriched {result.company_id}")
            print(f"- Employees: {result.company_info.num_employees}")
            print(f"- Contacts created: {result.contacts_created}")
    """
    
    def __init__(
        self,
        airtable_client: Optional[AirtableClient] = None,
        gemini_client: Optional[GeminiClient] = None,
    ):
        """Initialize the EnriquecedorDatos agent.
        
        Args:
            airtable_client: Optional custom Airtable client
            gemini_client: Optional custom Gemini client
        """
        self._airtable = airtable_client or get_airtable_client()
        self._gemini = gemini_client or get_gemini_client()
        self._system_prompt = load_prompt("enriquecedor")
        
        logger.info("enriquecedor_datos_initialized")
    
    def enrich_company(
        self,
        company_id: str,
        include_financials: bool = True,
        include_contacts: bool = True,
        dry_run: bool = False,
    ) -> EnrichmentResult:
        """Enrich a company with additional data from web sources.
        
        Args:
            company_id: Airtable record ID of the company
            include_financials: Whether to search for financial data
            include_contacts: Whether to search for key persons
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
            dry_run=dry_run,
        )
        
        result = EnrichmentResult(company_id=company_id, success=False)
        
        try:
            # 1. Get company from Airtable
            company_record = self._airtable.get_record("companies", company_id)
            company_name = company_record.get("fields", {}).get("Company Name", "")
            company_url = company_record.get("fields", {}).get("Home URL", "")
            
            if not company_name:
                result.errors.append("Company name is empty")
                return result
            
            logger.info(
                "enrichment_company_loaded",
                task_id=task_id,
                company_name=company_name,
                company_url=company_url,
            )
            
            # 2. Search for company info
            company_info = self._search_company_info(company_name, company_url)
            result.company_info = company_info
            
            # 3. Search for financial data
            if include_financials:
                financial_info = self._extract_financials(company_name, company_url)
                result.financial_info = financial_info
            
            # 4. Search for key persons
            if include_contacts:
                key_persons = self._identify_key_persons(company_name, company_url)
                result.key_persons = key_persons
            
            # 5. Save results to Airtable
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
        
        # Build search query
        query = f"""
Search for information about the company "{company_name}".
{f'Their website is: {company_url}' if company_url else ''}

Find and extract:
1. Number of employees (approximate)
2. LinkedIn company page URL
3. Brief description of what the company does (2-3 sentences)
4. Headquarters address (city, country)
5. Industry/sector classification

Return ONLY a JSON object with this exact structure:
{{
    "num_employees": <number or null>,
    "linkedin_url": "<url or null>",
    "description": "<string or null>",
    "hq_address": "<string or null>",
    "sector": "<string or null>",
    "founded_year": <number or null>
}}

If you cannot find reliable information for a field, use null.
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
Search for financial information about "{company_name}".
{f'Website: {company_url}' if company_url else ''}

Find the most recent financial data (from {current_year-3} to {current_year}):
1. Annual revenues (in EUR or USD)
2. EBITDA (in EUR or USD)
3. Net financial debt (in EUR or USD)
4. The year of these figures

Look for:
- Annual reports
- Press releases about financial results
- Company registries
- Business databases

Return ONLY a JSON object with this exact structure:
{{
    "annual_revenues": <number in EUR or null>,
    "ebitda": <number in EUR or null>,
    "net_financial_debt": <number in EUR or null>,
    "year": <4-digit year or null>,
    "currency": "EUR" or "USD",
    "source": "<source name or null>"
}}

Convert to EUR if needed (use approximate exchange rate).
If you cannot find reliable data, use null.
"""
        
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
            if year and (year < current_year - 3 or year > current_year):
                year = None
            
            return FinancialInfo(
                annual_revenues=result.get("annual_revenues"),
                ebitda=result.get("ebitda"),
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
    
    def _identify_key_persons(
        self,
        company_name: str,
        company_url: Optional[str],
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
        
        query = f"""
Search for key executives at "{company_name}".
{f'Website: {company_url}' if company_url else ''}

Find these roles if possible:
1. CEO / Director General / Managing Director
2. CFO / Director Financiero / Finance Director
3. COO / Director de Operaciones / Operations Director

For each person found, get:
- Full name (first and last)
- Exact role/title
- LinkedIn profile URL (if available)
- Business email (if publicly available)

Return ONLY a JSON object with this exact structure:
{{
    "key_persons": [
        {{
            "first_name": "<string>",
            "last_name": "<string>",
            "role": "<exact title>",
            "linkedin_url": "<url or null>",
            "email": "<email or null>",
            "phone": "<phone or null>"
        }}
    ]
}}

Only include people you can verify. Maximum 5 people.
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
                    key_persons.append(KeyPersonInfo(
                        first_name=person_data["first_name"],
                        last_name=person_data["last_name"],
                        role=person_data.get("role", "Executive"),
                        email=person_data.get("email"),
                        phone=person_data.get("phone"),
                        linkedin_url=person_data.get("linkedin_url"),
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
            
            if company_info.num_employees and not existing_fields.get("Num Employees"):
                update_fields["Num Employees"] = company_info.num_employees
            
            if company_info.linkedin_url and not existing_fields.get("Linkedin URL"):
                update_fields["Linkedin URL"] = company_info.linkedin_url
            
            if company_info.description and not existing_fields.get("Description"):
                update_fields["Description"] = company_info.description
            
            if company_info.hq_address and not existing_fields.get("HQ Address"):
                update_fields["HQ Address"] = company_info.hq_address
            
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
        
        # 2. Create financials record if we have data
        if financial_info and financial_info.has_data():
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
    
    def enrich_batch(
        self,
        company_ids: list[str],
        include_financials: bool = True,
        include_contacts: bool = True,
        dry_run: bool = False,
        on_progress: Optional[callable] = None,
    ) -> list[EnrichmentResult]:
        """Enrich multiple companies.
        
        Args:
            company_ids: List of company record IDs
            include_financials: Whether to search for financial data
            include_contacts: Whether to search for key persons
            dry_run: If True, don't save changes
            on_progress: Optional callback(current, total, result)
            
        Returns:
            List of EnrichmentResult for each company
        """
        results = []
        total = len(company_ids)
        
        logger.info(
            "batch_enrichment_started",
            total_companies=total,
            include_financials=include_financials,
            include_contacts=include_contacts,
            dry_run=dry_run,
        )
        
        for i, company_id in enumerate(company_ids, 1):
            result = self.enrich_company(
                company_id=company_id,
                include_financials=include_financials,
                include_contacts=include_contacts,
                dry_run=dry_run,
            )
            results.append(result)
            
            if on_progress:
                on_progress(i, total, result)
        
        # Log summary
        successful = sum(1 for r in results if r.success)
        contacts_created = sum(r.contacts_created for r in results)
        financials_created = sum(1 for r in results if r.financials_created)
        
        logger.info(
            "batch_enrichment_completed",
            total=total,
            successful=successful,
            failed=total - successful,
            contacts_created=contacts_created,
            financials_created=financials_created,
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

