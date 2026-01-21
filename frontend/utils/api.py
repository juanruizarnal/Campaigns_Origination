"""API wrapper for backend integration.

Provides a unified interface for Streamlit frontend to interact with backend agents.
Uses the real Airtable field names from the schema.
"""

from __future__ import annotations

import sys
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Callable, Any
import streamlit as st

# Add parent directory to path for backend imports
backend_path = str(Path(__file__).parent.parent.parent)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Track backend availability
BACKEND_AVAILABLE = False
BACKEND_ERROR = None

try:
    from core.airtable_client import AirtableClient, get_airtable_client, AirtableError
    from config.airtable_schema import (
        COMPANY_FIELDS,
        CAMPAIGN_FIELDS,
        CAMPAIGN_TARGET_FIELDS,
        FEI_STATUS_OPTIONS,
    )
    BACKEND_AVAILABLE = True
except Exception as e:
    BACKEND_ERROR = f"{type(e).__name__}: {e}"
    st.warning(f"⚠️ Backend parcialmente disponible: {BACKEND_ERROR}")


@dataclass
class DashboardMetrics:
    """Metrics for dashboard display."""
    total_companies: int = 0
    fei_eligible: int = 0
    fei_not_eligible: int = 0
    fei_partial: int = 0
    fei_unknown: int = 0
    fei_rate: float = 0.0
    total_campaigns: int = 0
    active_campaigns: int = 0
    recent_campaigns: List[dict] = field(default_factory=list)


class OriginationAPI:
    """API unificada para frontend Streamlit.
    
    Usa los nombres de campos REALES de Airtable.
    """
    
    def __init__(self):
        """Initialize API with lazy loading of backend components."""
        self._airtable = None
        self._orchestrator = None
        self._pipeline = None
        self._evaluador_fei = None
        self._buscador = None
        self._enriquecedor = None
        self._analizador = None
    
    @property
    def airtable(self) -> Optional[AirtableClient]:
        """Lazy load Airtable client."""
        if self._airtable is None and BACKEND_AVAILABLE:
            try:
                self._airtable = get_airtable_client()
            except Exception as e:
                st.error(f"Error conectando a Airtable: {e}")
                return None
        return self._airtable
    
    def _get_evaluador_fei(self):
        """Lazy load EvaluadorFEI agent."""
        if self._evaluador_fei is None:
            try:
                from agents.evaluador_fei import EvaluadorFEI
                self._evaluador_fei = EvaluadorFEI()
            except Exception as e:
                st.error(f"Error cargando EvaluadorFEI: {e}")
        return self._evaluador_fei
    
    def _get_buscador(self):
        """Lazy load Buscador agent."""
        if self._buscador is None:
            try:
                from agents.buscador import BuscadorEmpresas
                self._buscador = BuscadorEmpresas()
            except Exception as e:
                st.error(f"Error cargando Buscador: {e}")
        return self._buscador
    
    def _get_analizador(self):
        """Lazy load Analizador agent."""
        if self._analizador is None:
            try:
                from agents.analizador import AnalizadorContexto
                self._analizador = AnalizadorContexto()
            except Exception as e:
                st.error(f"Error cargando Analizador: {e}")
        return self._analizador
    
    @property
    def orchestrator(self):
        """Lazy load campaign orchestrator."""
        if self._orchestrator is None:
            try:
                from core.campaign_orchestrator import CampaignOrchestrator
                self._orchestrator = CampaignOrchestrator()
            except Exception as e:
                pass
        return self._orchestrator
    
    @property
    def pipeline(self):
        """Lazy load origination pipeline."""
        if self._pipeline is None:
            try:
                from core.origination_pipeline import OriginationPipeline
                self._pipeline = OriginationPipeline()
            except Exception as e:
                pass
        return self._pipeline
    
    # =========================================================================
    # DASHBOARD
    # =========================================================================
    
    def get_dashboard_metrics(self) -> DashboardMetrics:
        """Get metrics for dashboard display."""
        try:
            if not self.airtable:
                return DashboardMetrics()
            
            # Get all companies (no filter)
            companies = self.airtable.query_records("companies", max_records=1000)
            
            # Get all campaigns
            campaigns = self.airtable.query_records("campaigns", max_records=100)
            
            # Count FEI statuses - use the actual field name from Airtable
            # Note: Empty/None values are treated as "Unknown"
            fei_counts = {"Eligible": 0, "Not_Eligible": 0, "Partially_Eligible": 0, "Unknown": 0}
            for c in companies:
                # FEI_Status field - it's a Select field in Airtable
                # Empty/None values should be counted as Unknown
                status = c.get("fields", {}).get("FEI_Status")
                if not status:
                    fei_counts["Unknown"] += 1
                elif status in fei_counts:
                    fei_counts[status] += 1
                elif status == "Partial" or status == "Partially_Eligible":
                    fei_counts["Partially_Eligible"] += 1
                else:
                    fei_counts["Unknown"] += 1
            
            total = len(companies)
            fei_rate = (fei_counts["Eligible"] / total * 100) if total > 0 else 0
            
            # Count active campaigns - Status field
            active = sum(
                1 for c in campaigns 
                if c.get("fields", {}).get("Status") in ["Active", "Approved", "Scheduled"]
            )
            
            return DashboardMetrics(
                total_companies=total,
                fei_eligible=fei_counts["Eligible"],
                fei_not_eligible=fei_counts["Not_Eligible"],
                fei_partial=fei_counts["Partially_Eligible"],
                fei_unknown=fei_counts["Unknown"],
                fei_rate=fei_rate,
                total_campaigns=len(campaigns),
                active_campaigns=active,
                recent_campaigns=campaigns[:5],
            )
        except Exception as e:
            st.error(f"Error cargando metricas: {e}")
            return DashboardMetrics()
    
    # =========================================================================
    # EMPRESAS
    # =========================================================================
    
    def get_companies(
        self,
        sector: str = None,
        country: str = None,
        fei_status: str = None,
        search_query: str = None,
        limit: int = 100,
        offset: int = 0,
        formula: str = None,  # Allow direct Airtable formula
    ) -> tuple[list, int]:
        """List companies with filters and pagination.
        
        NOTE: Airtable field names:
        - "Company Name" (text)
        - "FEI_Status" (select)
        - "Sector" (rollup - cannot filter directly)
        - "HQ Country" (link - cannot filter directly with text)
        
        Args:
            sector: Filter by sector (client-side)
            country: Filter by country (client-side)
            fei_status: Filter by FEI status (server-side)
            search_query: Search by company name (client-side)
            limit: Max records to return
            offset: Pagination offset (client-side)
            formula: Direct Airtable formula (overrides other filters)
        """
        try:
            if not self.airtable:
                return [], 0
            
            # Use direct formula if provided
            if formula:
                query_formula = formula
            else:
                # Build formula - only use fields that can be filtered
                formula_parts = []
                
                # FEI_Status is a Select field - CAN filter
                if fei_status:
                    formula_parts.append(f"{{FEI_Status}}='{fei_status}'")
                
                query_formula = "AND(" + ",".join(formula_parts) + ")" if formula_parts else None
            
            # Query records - get more than needed for client-side filtering
            companies = self.airtable.query_records(
                "companies",
                formula=query_formula,
                max_records=limit * 3 if (sector or country or search_query) else limit,
            )
            
            # Client-side filtering for Rollup/Link fields
            if sector and sector != "Todos":
                companies = [
                    c for c in companies
                    if sector.lower() in str(c.get("fields", {}).get("Sector", "")).lower()
                ]
            
            if country:
                companies = [
                    c for c in companies
                    if country.upper() in str(c.get("fields", {}).get("HQ Country", "")).upper()
                ]
            
            # Client-side search filter
            if search_query:
                query_lower = search_query.lower()
                companies = [
                    c for c in companies
                    if query_lower in c.get("fields", {}).get("Company Name", "").lower()
                ]
            
            # Apply limit after client-side filtering
            total = len(companies)
            companies = companies[:limit]
            
            return companies, total
        except Exception as e:
            st.error(f"Error cargando empresas: {e}")
            return [], 0
    
    def search_companies(
        self,
        sector: str,
        country: str,
        region: str = None,
        keywords: list = None,
        min_employees: int = None,
        limit: int = 25,
        on_progress: Callable = None,
        save_to_airtable: bool = False,  # Default: NO save automatically
    ) -> dict:
        """Search new companies with Buscador agent.
        
        IMPORTANT: By default, companies are NOT saved to Airtable.
        User must manually select and save using save_companies().
        
        Returns a normalized dictionary with:
        - success: bool
        - candidates_found: list of dicts with company info
        - companies_created: list of record IDs (only if save_to_airtable=True)
        - duplicates_skipped: int
        - errors: list of error messages
        """
        try:
            buscador = self._get_buscador()
            if not buscador:
                return {"success": False, "candidates_found": [], "errors": ["Buscador no disponible"]}
            
            result = buscador.search(
                sector=sector,
                country=country,
                region=region,
                keywords=keywords or [],
                limit=limit,
                create_records=save_to_airtable,  # Only save if explicitly requested
            )
            
            # Convert SearchResult to normalized dict
            candidates = []
            for candidate in getattr(result, "candidates_found", []):
                candidates.append({
                    "name": getattr(candidate, "name", ""),
                    "home_url": getattr(candidate, "home_url", ""),
                    "linkedin_url": getattr(candidate, "linkedin_url", ""),
                    "description": getattr(candidate, "description", ""),
                    "sector": getattr(candidate, "sector", ""),
                    "country": getattr(candidate, "country", ""),
                    "hq_country": getattr(candidate, "hq_country", ""),
                    "region": getattr(candidate, "region", ""),
                    "estimated_employees": getattr(candidate, "estimated_employees", None),
                    "employee_range": getattr(candidate, "employee_range", None),
                    "is_duplicate": getattr(candidate, "is_duplicate", False),
                    "duplicate_of": getattr(candidate, "duplicate_of", None),
                    "url_verified": getattr(candidate, "url_verified", False),
                    "created_company_id": getattr(candidate, "created_company_id", None),
                    "match_reason": getattr(candidate, "match_reason", None),
                    "match_confidence": getattr(candidate, "match_confidence", None),
                })
            
            return {
                "success": getattr(result, "success", False),
                "candidates_found": candidates,
                "companies_created": getattr(result, "companies_created", []),
                "duplicates_skipped": getattr(result, "duplicates_skipped", 0),
                "processing_time": getattr(result, "processing_time_seconds", 0),
                "errors": getattr(result, "errors", []),
            }
        except Exception as e:
            return {"success": False, "candidates_found": [], "errors": [str(e)]}
    
    def save_companies(self, candidates: List[dict]) -> dict:
        """Save selected companies to Airtable.
        
        Args:
            candidates: List of company dicts to save (from search_companies results)
            
        Returns:
            Dict with success status and created record IDs
        """
        try:
            if not self.airtable:
                return {"success": False, "errors": ["Airtable no disponible"]}
            
            created_companies = []
            created_bus = []
            errors = []
            
            for candidate in candidates:
                try:
                    # Create company record
                    company_fields = {
                        "Company Name": candidate.get("name", ""),
                        "Source": ["Web Scraping"],
                    }
                    
                    if candidate.get("home_url"):
                        company_fields["Home URL"] = candidate.get("home_url")
                    
                    if candidate.get("description"):
                        company_fields["Description"] = candidate.get("description")

                    if candidate.get("linkedin_url"):
                        company_fields["Linkedin URL"] = candidate.get("linkedin_url")
                    
                    if candidate.get("estimated_employees"):
                        company_fields["Num Employees"] = candidate.get("estimated_employees")
                    
                    company_record = self.airtable.create_record("companies", company_fields)
                    company_id = company_record["id"]
                    created_companies.append(company_id)

                    # Update HQ Country if provided (typecast for link resolution)
                    hq_country = candidate.get("hq_country") or candidate.get("country")
                    if hq_country:
                        hq_name = self._country_code_to_name(str(hq_country))
                        try:
                            self.airtable.update_record(
                                "companies",
                                company_id,
                                {"HQ Country": [hq_name]},
                                typecast=True,
                            )
                        except Exception:
                            pass
                    
                    # Create default business unit
                    bu_fields = {
                        "Business Unit Name": "Principal",
                        "Company": [company_id],
                    }
                    
                    bu_record = self.airtable.create_record("business_units", bu_fields)
                    created_bus.append(bu_record["id"])
                    
                except Exception as e:
                    errors.append(f"Error guardando {candidate.get('name', 'empresa')}: {str(e)}")
            
            return {
                "success": len(created_companies) > 0,
                "companies_created": created_companies,
                "bus_created": created_bus,
                "errors": errors,
            }
        except Exception as e:
            return {"success": False, "errors": [str(e)]}

    def _country_code_to_name(self, country_code: str) -> str:
        """Convert ISO country code to display name for Airtable linking."""
        mapping = {
            "ES": "España",
            "FR": "Francia",
            "DE": "Alemania",
            "IT": "Italia",
            "PT": "Portugal",
            "NL": "Países Bajos",
            "BE": "Bélgica",
            "PL": "Polonia",
            "AT": "Austria",
            "IE": "Irlanda",
            "GB": "Reino Unido",
            "UK": "Reino Unido",
            "US": "Estados Unidos",
        }
        code = country_code.strip().upper()
        return mapping.get(code, country_code)
    
    def enrich_company(
        self,
        company_id: str,
        company_name: str = None,
        company_url: str = None,
        include_financials: bool = True,
        include_contacts: bool = False,
    ) -> Any:
        """Enrich company data with Enriquecedor agent.
        
        Gets structural data: employees, revenue, EBITDA, LinkedIn, description.
        
        Args:
            company_id: Airtable record ID
            company_name: Company name (for display, not passed to agent)
            company_url: Company URL (for display, not passed to agent)
            include_financials: Whether to search for financial data
            include_contacts: Whether to search for contacts
        """
        try:
            if self._enriquecedor is None:
                from agents.enriquecedor import EnriquecedorDatos
                self._enriquecedor = EnriquecedorDatos()
            
            result = self._enriquecedor.enrich_company(
                company_id=company_id,
                include_financials=include_financials,
                include_contacts=include_contacts,
            )
            return result
        except Exception as e:
            return {"success": False, "errors": [str(e)]}

    def enrich_structure(self, company_id: str) -> dict:
        """Infer parent/holding/subsidiary relationships using Airtable data."""
        try:
            if not self.airtable:
                return {"success": False, "errors": ["Airtable no disponible"]}

            target = self.airtable.get_record("companies", company_id)
            fields = target.get("fields", {})
            target_name = fields.get("Company Name", "")
            target_url = fields.get("Home URL", "")
            target_domain = self._normalize_domain(target_url)
            normalized_target = self._normalize_company_name(target_name)

            candidates = self.airtable.query_records("companies", max_records=2000)

            parent_candidates = []
            subsidiary_candidates = []
            related_candidates = []

            for record in candidates:
                if record.get("id") == company_id:
                    continue
                other_fields = record.get("fields", {})
                other_name = other_fields.get("Company Name", "")
                other_url = other_fields.get("Home URL", "")
                other_domain = self._normalize_domain(other_url)
                normalized_other = self._normalize_company_name(other_name)

                if not normalized_other:
                    continue

                similarity = self._name_similarity(normalized_target, normalized_other)
                same_domain = target_domain and other_domain and target_domain == other_domain
                is_group = self._looks_like_group(other_name)

                if same_domain:
                    parent_candidates.append((record, 1.0, "same_domain"))
                    continue

                if similarity >= 0.9:
                    if normalized_target.startswith(normalized_other) and len(normalized_other) < len(normalized_target):
                        parent_candidates.append((record, similarity, "name_contains"))
                    elif normalized_other.startswith(normalized_target) and len(normalized_target) < len(normalized_other):
                        subsidiary_candidates.append((record, similarity, "name_contains"))
                    elif is_group:
                        parent_candidates.append((record, similarity, "group_keyword"))
                    else:
                        related_candidates.append((record, similarity, "similar_name"))

            parent = self._pick_best_relation(parent_candidates)
            ultimate = self._pick_best_relation(
                [c for c in parent_candidates if self._looks_like_group(c[0].get("fields", {}).get("Company Name", ""))]
            ) or parent

            update_fields = {}
            if parent:
                update_fields["Parent Company"] = [parent["id"]]
            if ultimate:
                update_fields["Ultimate Parent Company"] = [ultimate["id"]]
            if update_fields:
                self.airtable.update_record("companies", company_id, update_fields, typecast=True)

            return {
                "success": True,
                "parent_company": parent.get("fields", {}).get("Company Name") if parent else None,
                "ultimate_parent": ultimate.get("fields", {}).get("Company Name") if ultimate else None,
                "subsidiaries": [r.get("fields", {}).get("Company Name") for r, _, _ in subsidiary_candidates][:10],
                "related_companies": [r.get("fields", {}).get("Company Name") for r, _, _ in related_candidates][:10],
            }
        except Exception as e:
            return {"success": False, "errors": [str(e)]}

    def _normalize_company_name(self, name: str) -> str:
        """Normalize company names for comparison."""
        text = (name or "").lower()
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\b(s\.a\.|s\.l\.|ltd|limited|inc|llc|gmbh|sarl|sa)\b", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _normalize_domain(self, url: str) -> str:
        """Normalize a URL to its domain."""
        try:
            from urllib.parse import urlparse
            if not url:
                return ""
            parsed = urlparse(url if url.startswith(("http://", "https://")) else f"https://{url}")
            domain = parsed.netloc.lower()
            return domain[4:] if domain.startswith("www.") else domain
        except Exception:
            return ""

    def _name_similarity(self, a: str, b: str) -> float:
        from difflib import SequenceMatcher
        return SequenceMatcher(None, a, b).ratio()

    def _looks_like_group(self, name: str) -> bool:
        keywords = ["group", "holding", "capital", "partners", "invest", "grupo", "holdings"]
        lowered = (name or "").lower()
        return any(k in lowered for k in keywords)

    def _pick_best_relation(self, candidates: list[tuple[dict, float, str]]) -> Optional[dict]:
        if not candidates:
            return None
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]
    
    def get_or_create_business_units(self, company_id: str, company_name: str = None) -> dict:
        """Get existing business units for a company or create default ones.
        
        Args:
            company_id: Airtable company record ID
            company_name: Company name (for BU naming)
            
        Returns:
            Dict with business_units list and created/updated counts
        """
        try:
            if not self.airtable:
                return {"success": False, "errors": ["Airtable no disponible"]}
            
            # Get existing BUs for this company
            all_bus = self.airtable.query_records("business_units", max_records=500)
            existing_bus = [
                bu for bu in all_bus
                if company_id in (bu.get("fields", {}).get("Company") or [])
            ]
            
            result = {
                "success": True,
                "business_units": existing_bus,
                "created": 0,
                "updated": 0,
            }
            
            # If no BUs exist, create a "Principal" BU
            if not existing_bus:
                try:
                    bu_name = f"{company_name} - Principal" if company_name else "Principal"
                    new_bu = self.airtable.create_record("business_units", {
                        "Business Unit Name": bu_name,
                        "Company": [company_id],
                    })
                    result["business_units"] = [new_bu]
                    result["created"] = 1
                except Exception as e:
                    result["errors"] = [f"Error creando BU: {str(e)}"]

            # Ensure primary BU fields are filled
            if result.get("business_units"):
                try:
                    company_record = self.airtable.get_record("companies", company_id)
                    primary_bu_id = result["business_units"][0].get("id")
                    if primary_bu_id:
                        self._ensure_primary_bu_fields(primary_bu_id, company_record)
                except Exception:
                    pass
            
            # Transform BUs to dict format
            result["business_units"] = [
                {
                    "id": bu.get("id"),
                    "name": bu.get("fields", {}).get("Business Unit Name", "N/A"),
                    "type": bu.get("fields", {}).get("BU Type", "Principal"),
                    "sector": bu.get("fields", {}).get("Sector", ""),
                    "country": bu.get("fields", {}).get("Country", ""),
                }
                for bu in result["business_units"]
            ]
            
            return result
        except Exception as e:
            return {"success": False, "business_units": [], "errors": [str(e)]}
    
    def create_business_unit(
        self, 
        company_id: str, 
        bu_name: str,
        bu_country: str = None,
        bu_type: str = "Regional",
        bu_sector: str = None,
    ) -> dict:
        """Create a new Business Unit for an existing company.
        
        Args:
            company_id: Airtable company record ID
            bu_name: Name for the new Business Unit
            bu_country: Country for the BU (optional)
            bu_type: Type of BU (default: Regional)
            bu_sector: Sector for the BU (optional)
            
        Returns:
            Dict with success status and created BU info
        """
        try:
            if not self.airtable:
                return {"success": False, "errors": ["Airtable no disponible"]}
            
            # Build BU fields
            bu_fields = {
                "Business Unit Name": bu_name,
                "Company": [company_id],
            }
            
            if bu_type:
                bu_fields["BU Type"] = bu_type
            
            # Note: Country and Sector might be link fields, handle accordingly
            # For now, we'll add them as text if provided
            if bu_country:
                bu_fields["Notes"] = f"País: {bu_country}"
            
            # Create the BU
            new_bu = self.airtable.create_record("business_units", bu_fields)
            
            return {
                "success": True,
                "bu_id": new_bu.get("id"),
                "bu_name": bu_name,
            }
        except Exception as e:
            return {"success": False, "errors": [str(e)]}

    def _ensure_primary_bu_fields(self, bu_id: str, company_record: dict) -> None:
        """Fill required fields for the primary Business Unit."""
        fields = company_record.get("fields", {})
        company_name = fields.get("Company Name", "")
        description = fields.get("Description", "") or ""

        sector, activities = self._infer_sector_and_activities(company_name, description)
        update_fields: dict[str, object] = {}

        # Business Unit Type (linked) - use typecast to resolve by name
        update_fields["Business Unit Type"] = ["Principal"]

        if sector:
            update_fields["Sector"] = [sector]
        if activities:
            update_fields["Activities"] = activities

        hq_country = fields.get("HQ Country")
        if isinstance(hq_country, list) and hq_country:
            update_fields["Focus Countries"] = hq_country
        elif isinstance(hq_country, str) and hq_country:
            update_fields["Focus Countries"] = [self._country_code_to_name(hq_country)]

        if update_fields:
            self.airtable.update_record("business_units", bu_id, update_fields, typecast=True)

    def _infer_sector_and_activities(self, company_name: str, description: str) -> tuple[str, list[str]]:
        """Infer sector and activities for a Business Unit."""
        text = f"{company_name} {description}".lower()

        defense_keywords = ["defense", "aerospace", "military", "defence", "armament", "aircraft"]
        real_estate_keywords = ["real estate", "property", "housing", "residential", "commercial", "developer", "inmobiliaria"]
        renewable_keywords = ["renewable", "solar", "wind", "hydro", "hydrogen", "biomass", "geothermal", "energy"]

        if any(k in text for k in defense_keywords):
            sector = "Defense & Aerospace"
        elif any(k in text for k in real_estate_keywords):
            sector = "Real Estate"
        elif any(k in text for k in renewable_keywords):
            sector = "Renewable Energy"
        else:
            sector = "Renewable Energy"

        activity_map = {
            "Real Estate": [
                "Mixed-Use Developments",
                "Residential Development",
                "Retail & Shopping Centers",
                "Senior Living",
                "Student Housing",
            ],
            "Renewable Energy": [
                "Battery Storage (BESS)",
                "Biogas",
                "Biomass",
                "Geothermal",
                "Green Hydrogen Production",
                "Hydropower",
                "Ocean Energy",
                "Autoconsumption",
            ],
            "Defense & Aerospace": [
                "Defense & Aerospace",
            ],
        }

        return sector, activity_map.get(sector, [])
    
    def search_contacts(self, company_id: str) -> dict:
        """Search for contacts (CEO, CFO, executives) for a company.
        
        Separate method to find and create contact records in Airtable.
        """
        try:
            if self._enriquecedor is None:
                from agents.enriquecedor import EnriquecedorDatos
                self._enriquecedor = EnriquecedorDatos()
            
            # Use enriquecedor with only contacts
            result = self._enriquecedor.enrich_company(
                company_id=company_id,
                include_financials=False,
                include_contacts=True,
            )
            
            # Return contact-specific result
            contacts_created = getattr(result, "contacts_created", 0) if hasattr(result, "contacts_created") else 0
            key_persons = getattr(result, "key_persons", []) if hasattr(result, "key_persons") else []
            
            return {
                "success": getattr(result, "success", False) if hasattr(result, "success") else result.get("success", False),
                "contacts_created": contacts_created,
                "contacts_found": len(key_persons),
                "key_persons": [
                    {
                        "name": f"{p.first_name} {p.last_name}" if hasattr(p, "first_name") else p.get("name", ""),
                        "role": getattr(p, "role", "") if hasattr(p, "role") else p.get("role", ""),
                        "email": getattr(p, "email", None) if hasattr(p, "email") else p.get("email"),
                        "linkedin": getattr(p, "linkedin_url", None) if hasattr(p, "linkedin_url") else p.get("linkedin_url"),
                    }
                    for p in key_persons
                ],
            }
        except Exception as e:
            return {"success": False, "contacts_created": 0, "errors": [str(e)]}
    
    # =========================================================================
    # FEI
    # =========================================================================
    
    def evaluate_fei(self, company_id: str, force: bool = False) -> Any:
        """Evaluate FEI eligibility for a company.
        
        Args:
            company_id: Airtable company record ID
            force: If True, re-evaluate even if already evaluated
        """
        try:
            evaluador = self._get_evaluador_fei()
            if not evaluador:
                return {"success": False, "errors": ["EvaluadorFEI no disponible"]}
            
            return evaluador.evaluate(company_id=company_id, force=force)
        except Exception as e:
            return {"success": False, "errors": [str(e)]}
    
    def evaluate_fei_batch(
        self,
        limit: int = 50,
        on_progress: Callable = None,
    ) -> Any:
        """Batch FEI evaluation for pending companies."""
        try:
            if not self.airtable:
                return {"success": False, "errors": ["Airtable no disponible"]}
            
            # Get companies without FEI status (empty/None)
            companies = self.get_pending_fei_companies(limit=limit)
            
            if not companies:
                return {"success": True, "evaluations": [], "message": "No hay empresas pendientes"}
            
            evaluador = self._get_evaluador_fei()
            if not evaluador:
                return {"success": False, "errors": ["EvaluadorFEI no disponible"]}
            
            # Create wrapper for progress callback
            def progress_wrapper(current, total, result):
                if on_progress:
                    company_name = result.company_name if hasattr(result, 'company_name') else "Empresa"
                    status = result.status.value if hasattr(result.status, 'value') else str(result.status)
                    on_progress(current, total, company_name, status)
            
            results = evaluador.evaluate_batch(
                company_ids=[c["id"] for c in companies],
                on_progress=progress_wrapper,
            )
            
            return {"success": True, "evaluations": results}
        except Exception as e:
            return {"success": False, "errors": [str(e)]}
    
    def get_pending_fei_companies(self, limit: int = 500) -> list:
        """Get companies pending FEI evaluation.
        
        Searches for companies where FEI_Status is empty (not set).
        """
        try:
            if not self.airtable:
                return []
            
            # In Airtable, empty select fields can be filtered with OR({field}='', {field}=BLANK())
            # But the simplest is to get all and filter client-side
            all_companies = self.airtable.query_records(
                "companies",
                max_records=limit * 2,  # Get more to account for filtering
            )
            
            # Filter to companies without FEI_Status
            pending = [
                c for c in all_companies
                if not c.get("fields", {}).get("FEI_Status")
            ]
            
            return pending[:limit]
        except Exception as e:
            st.error(f"Error cargando empresas pendientes: {e}")
            return []
    
    # =========================================================================
    # ANALISIS DE TRIGGER
    # =========================================================================
    
    def analyze_trigger(self, trigger: str) -> dict:
        """Analyze market trigger with Analizador agent."""
        try:
            analizador = self._get_analizador()
            if not analizador:
                return {"success": False, "errors": ["Analizador no disponible"]}
            
            result = analizador.analyze(trigger=trigger)
            
            return {
                "success": True,
                "impact": result.impact if hasattr(result, "impact") else None,
                "key_angles": result.key_angles if hasattr(result, "key_angles") else [],
            }
        except Exception as e:
            return {"success": False, "errors": [str(e)]}
    
    # =========================================================================
    # CAMPANAS
    # =========================================================================
    
    def get_campaigns(self, status: str = None, limit: int = 20) -> list:
        """List campaigns with optional status filter.
        
        NOTE: Campaign Status field is a Select field in Airtable.
        """
        try:
            if not self.airtable:
                return []
            
            formula = f"{{Status}}='{status}'" if status else None
            return self.airtable.query_records(
                "campaigns",
                formula=formula,
                max_records=limit,
            )
        except Exception as e:
            st.error(f"Error cargando campanas: {e}")
            return []
    
    def get_campaign_detail(self, campaign_id: str) -> dict:
        """Get campaign detail with targets."""
        try:
            if not self.airtable:
                return None
            
            campaign = self.airtable.get_record("campaigns", campaign_id)
            
            # Get targets for this campaign
            targets = self.airtable.query_records(
                "campaign_targets",
                max_records=100,
            )
            
            # Filter targets that belong to this campaign
            campaign_targets = [
                t for t in targets
                if campaign_id in (t.get("fields", {}).get("Campaign") or [])
            ]
            
            return {
                "campaign": campaign,
                "targets": campaign_targets,
            }
        except Exception as e:
            st.error(f"Error cargando detalle de campana: {e}")
            return None
    
    def create_campaign_proposal(
        self,
        trigger: str,
        sectors: list,
        countries: list,
        max_targets: int = 30,
        min_fit_score: float = 0.6,
    ) -> dict:
        """Create campaign proposal from trigger."""
        try:
            if self.orchestrator:
                proposal = self.orchestrator.create_proposal(
                    trigger=trigger,
                    sectors=sectors,
                    countries=countries,
                    max_targets=max_targets,
                    min_fit_score=min_fit_score,
                )
                return {
                    "success": True,
                    "proposal": proposal,
                    "campaign_id": proposal.campaign_id if hasattr(proposal, "campaign_id") else None,
                }
            return {"success": False, "errors": ["Orchestrator no disponible"]}
        except Exception as e:
            return {"success": False, "errors": [str(e)]}
    
    def approve_campaign(self, campaign_id: str) -> None:
        """Approve campaign for sending."""
        try:
            if self.orchestrator:
                self.orchestrator.approve_campaign(campaign_id)
            elif self.airtable:
                # Direct update if orchestrator not available
                self.airtable.update_record("campaigns", campaign_id, {"Status": "Approved"})
        except Exception as e:
            st.error(f"Error aprobando campana: {e}")
    
    def complete_campaign(
        self,
        campaign_id: str,
        trigger: str,
        key_angles: list = None,
        tone: str = "professional",
    ) -> dict:
        """Generate emails and complete campaign."""
        try:
            if self.orchestrator:
                return self.orchestrator.complete_campaign(
                    campaign_id=campaign_id,
                    campaign_context=trigger,
                    key_angles=key_angles,
                    tone=tone,
                )
            return {"success": False, "errors": ["Orchestrator no disponible"]}
        except Exception as e:
            return {"success": False, "errors": [str(e)]}
    
    # =========================================================================
    # PIPELINE
    # =========================================================================
    
    def run_origination_pipeline(
        self,
        sector: str,
        country: str,
        region: str = None,
        keywords: list = None,
        limit: int = 25,
        enrich: bool = True,
        evaluate_fei: bool = True,
        save_to_airtable: bool = False,  # Default: NO save automatically
        on_progress: Callable = None,
    ) -> dict:
        """Execute origination pipeline: Search -> (optional) Enrich -> (optional) FEI.
        
        IMPORTANT: By default, companies are NOT saved to Airtable.
        User must manually select and save.
        
        Args:
            sector: Target sector
            country: Target country code
            region: Optional region
            keywords: Optional keywords list
            limit: Max companies to search
            enrich: Whether to enrich found companies (only if saved)
            evaluate_fei: Whether to evaluate FEI (only if saved)
            save_to_airtable: If True, save automatically (default: False)
            on_progress: Progress callback (step_name, current, total, message)
            
        Returns:
            Dict with candidates_found, success status, etc.
        """
        results = {
            "success": False,
            "candidates_found": [],
            "companies_saved": [],
            "duplicates": 0,
            "enriched": 0,
            "fei_eligible": 0,
            "processing_time": 0,
            "errors": [],
        }
        
        import time
        start_time = time.time()
        
        try:
            # Step 1: Search for companies (WITHOUT saving)
            if on_progress:
                on_progress("search", 0, 3, f"Buscando empresas de {sector} en {country}...")
            
            buscador = self._get_buscador()
            if not buscador:
                results["errors"].append("Buscador no disponible")
                return results
            
            search_result = buscador.search(
                sector=sector,
                country=country,
                region=region,
                keywords=keywords or [],
                limit=limit,
                create_records=save_to_airtable,  # Only save if explicitly requested
            )
            
            if not search_result.success:
                results["errors"] = getattr(search_result, "errors", ["Error en búsqueda"])
                return results
            
            # Convert candidates to dict format
            candidates = []
            for candidate in getattr(search_result, "candidates_found", []):
                candidates.append({
                    "name": getattr(candidate, "name", ""),
                    "home_url": getattr(candidate, "home_url", ""),
                    "description": getattr(candidate, "description", ""),
                    "sector": getattr(candidate, "sector", ""),
                    "country": getattr(candidate, "country", ""),
                    "region": getattr(candidate, "region", ""),
                    "estimated_employees": getattr(candidate, "estimated_employees", None),
                    "is_duplicate": getattr(candidate, "is_duplicate", False),
                    "duplicate_of": getattr(candidate, "duplicate_of", None),
                    "url_verified": getattr(candidate, "url_verified", False),
                    "created_company_id": getattr(candidate, "created_company_id", None),
                })
            
            results["candidates_found"] = candidates
            results["duplicates"] = getattr(search_result, "duplicates_skipped", 0)
            results["companies_saved"] = getattr(search_result, "companies_created", [])
            
            if on_progress:
                on_progress("search", 1, 3, f"Encontradas {len(candidates)} empresas")
            
            # Step 2: Enrich (only if we saved and enrich is enabled)
            if enrich and save_to_airtable and results["companies_saved"]:
                if on_progress:
                    on_progress("enrich", 1, 3, f"Enriqueciendo {len(results['companies_saved'])} empresas...")
                
                enriched_count = 0
                for company_id in results["companies_saved"]:
                    try:
                        enrich_result = self.enrich_company(company_id)
                        if hasattr(enrich_result, "success") and enrich_result.success:
                            enriched_count += 1
                        elif isinstance(enrich_result, dict) and enrich_result.get("success"):
                            enriched_count += 1
                    except Exception:
                        pass
                
                results["enriched"] = enriched_count
                
                if on_progress:
                    on_progress("enrich", 2, 3, f"Enriquecidas {enriched_count} empresas")
            
            # Step 3: FEI Evaluation (only if we saved and evaluate_fei is enabled)
            if evaluate_fei and save_to_airtable and results["companies_saved"]:
                if on_progress:
                    on_progress("fei", 2, 3, f"Evaluando FEI para {len(results['companies_saved'])} empresas...")
                
                fei_count = 0
                evaluador = self._get_evaluador_fei()
                if evaluador:
                    for company_id in results["companies_saved"]:
                        try:
                            fei_result = evaluador.evaluate(company_id)
                            if hasattr(fei_result, "status"):
                                status = fei_result.status.value if hasattr(fei_result.status, "value") else str(fei_result.status)
                                if status == "Eligible":
                                    fei_count += 1
                        except Exception:
                            pass
                
                results["fei_eligible"] = fei_count
            
            if on_progress:
                on_progress("complete", 3, 3, "Pipeline completado!")
            
            results["success"] = True
            results["processing_time"] = time.time() - start_time
            
            return results
            
        except Exception as e:
            results["errors"].append(str(e))
            results["processing_time"] = time.time() - start_time
            return results
    
    # =========================================================================
    # TRIGGERS (Agent 7)
    # =========================================================================
    
    def get_triggers(
        self,
        min_relevance: float = 0.0,
        status: str = None,
        limit: int = 50,
    ) -> list:
        """Get market triggers from Airtable.
        
        Args:
            min_relevance: Minimum relevance score (0-1)
            status: Filter by status (new, processed, etc.)
            limit: Max records to return
            
        Returns:
            List of trigger dicts
        """
        try:
            if not self.airtable:
                return []
            
            # Query triggers table (assuming it exists)
            triggers = self.airtable.query_records(
                "market_contexts",
                max_records=limit,
            )
            
            # Transform to trigger format
            result = []
            for t in triggers:
                fields = t.get("fields", {})
                relevance = fields.get("Campaign_Potential", 3) / 5.0  # Convert 1-5 to 0-1
                
                if relevance >= min_relevance:
                    result.append({
                        "id": t.get("id"),
                        "title": fields.get("Context_Title", ""),
                        "source_name": fields.get("Source_Name", "Manual"),
                        "source_url": fields.get("Source_URL", ""),
                        "summary": fields.get("Summary", ""),
                        "published_at": fields.get("Publication_Date"),
                        "relevance_score": relevance,
                        "keywords_matched": fields.get("Tags", []),
                        "affected_sectors": fields.get("Affected_Sectors_Names", "").split(", ") if fields.get("Affected_Sectors_Names") else [],
                        "affected_countries": fields.get("Affected_Countries_Names", "").split(", ") if fields.get("Affected_Countries_Names") else [],
                        "recommended_action": "create_campaign" if relevance >= 0.7 else "review",
                        "processed": fields.get("Status") == "Campaign_Created",
                        "campaign_created": fields.get("Status") == "Campaign_Created",
                        "campaign_id": fields.get("Campaigns", [None])[0] if fields.get("Campaigns") else None,
                    })
            
            return result
        except Exception as e:
            st.error(f"Error cargando triggers: {e}")
            return []
    
    def scan_triggers(self) -> dict:
        """Run trigger detector agent to scan for new triggers.
        
        Returns:
            Dict with triggers_detected count and high_relevance count
        """
        try:
            from agents.trigger_detector import TriggerDetector
            import asyncio
            
            detector = TriggerDetector()
            
            # Run async scan
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                triggers = loop.run_until_complete(detector.scan_feeds())
            finally:
                loop.close()
            
            # Save triggers to Airtable
            saved_count = 0
            high_count = 0
            
            for trigger in triggers:
                try:
                    if self.airtable:
                        # Create market context record
                        fields = {
                            "Context_Title": trigger.title,
                            "Source_Name": trigger.source_name,
                            "Source_URL": trigger.source_url,
                            "Summary": trigger.summary,
                            "Campaign_Potential": int(trigger.relevance_score * 5),
                            "Status": "New",
                        }
                        self.airtable.create_record("market_contexts", fields)
                        saved_count += 1
                        
                        if trigger.relevance_score >= 0.8:
                            high_count += 1
                except Exception:
                    pass
            
            return {
                "success": True,
                "triggers_detected": saved_count,
                "high_relevance": high_count,
            }
        except Exception as e:
            return {"success": False, "triggers_detected": 0, "errors": [str(e)]}
    
    def run_trigger_scan(self) -> list:
        """Run trigger scan and return the actual triggers found.
        
        Returns:
            List of trigger dicts with all details
        """
        try:
            from agents.trigger_detector import TriggerDetector
            import asyncio
            
            detector = TriggerDetector()
            
            # Run async scan
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                triggers = loop.run_until_complete(detector.scan_feeds())
            finally:
                loop.close()
            
            # Convert to dict format and save
            result = []
            for trigger in triggers:
                trigger_dict = {
                    "title": trigger.title,
                    "source_name": trigger.source_name,
                    "source_url": trigger.source_url,
                    "summary": trigger.summary,
                    "content": trigger.content,
                    "published_at": trigger.published_at.isoformat() if trigger.published_at else None,
                    "relevance_score": trigger.relevance_score,
                    "relevance_level": trigger.relevance_level.value if hasattr(trigger.relevance_level, 'value') else str(trigger.relevance_level),
                    "keywords_matched": trigger.keywords_matched,
                    "recommended_action": trigger.recommended_action,
                    "affected_sectors": trigger.affected_sectors,
                    "affected_countries": trigger.affected_countries,
                }
                
                # Save to Airtable
                try:
                    if self.airtable:
                        fields = {
                            "Context_Title": trigger.title,
                            "Source_Name": trigger.source_name,
                            "Source_URL": trigger.source_url,
                            "Summary": trigger.summary or "",
                            "Campaign_Potential": int(trigger.relevance_score * 5),
                            "Status": "New",
                        }
                        record = self.airtable.create_record("market_contexts", fields)
                        trigger_dict["id"] = record.get("id")
                except Exception:
                    pass
                
                result.append(trigger_dict)
            
            return result
        except Exception as e:
            st.error(f"Error escaneando triggers: {e}")
            return []
    
    def get_detected_triggers(self, limit: int = 50) -> list:
        """Get detected triggers from Airtable.
        
        Args:
            limit: Maximum number of triggers to return
            
        Returns:
            List of trigger dicts
        """
        try:
            if not self.airtable:
                return []
            
            # Query market contexts table
            records = self.airtable.query_records(
                "market_contexts",
                max_records=limit,
            )
            
            result = []
            for r in records:
                fields = r.get("fields", {})
                potential = fields.get("Campaign_Potential", 3)
                
                result.append({
                    "id": r.get("id"),
                    "title": fields.get("Context_Title", ""),
                    "source_name": fields.get("Source_Name", "Manual"),
                    "source_url": fields.get("Source_URL", ""),
                    "summary": fields.get("Summary", ""),
                    "published_at": fields.get("Publication_Date"),
                    "relevance_score": potential / 5.0,
                    "keywords_matched": fields.get("Tags", []),
                    "recommended_action": "create_campaign" if potential >= 4 else "review",
                    "affected_sectors": fields.get("Affected_Sectors_Names", "").split(", ") if fields.get("Affected_Sectors_Names") else [],
                    "affected_countries": fields.get("Affected_Countries_Names", "").split(", ") if fields.get("Affected_Countries_Names") else [],
                    "processed": fields.get("Status") == "Campaign_Created",
                    "campaign_created": fields.get("Status") == "Campaign_Created",
                    "campaign_id": fields.get("Campaigns", [None])[0] if fields.get("Campaigns") else None,
                })
            
            # Sort by relevance
            result.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            
            return result
        except Exception as e:
            st.error(f"Error cargando triggers: {e}")
            return []
    
    def mark_trigger_processed(self, trigger_id: str) -> None:
        """Mark a trigger as processed."""
        try:
            if self.airtable:
                self.airtable.update_record("market_contexts", trigger_id, {
                    "Status": "Analyzed",
                })
        except Exception as e:
            st.error(f"Error marcando trigger: {e}")
    
    def discard_trigger(self, trigger_id: str) -> None:
        """Discard a trigger (mark as irrelevant)."""
        try:
            if self.airtable:
                self.airtable.update_record("market_contexts", trigger_id, {
                    "Status": "Discarded",
                })
        except Exception as e:
            st.error(f"Error descartando trigger: {e}")
    
    def create_manual_trigger(
        self,
        title: str,
        source: str,
        url: str = None,
        summary: str = None,
        relevance: float = 0.7,
    ) -> dict:
        """Create a manual trigger entry."""
        try:
            if not self.airtable:
                return {"success": False, "errors": ["Airtable no disponible"]}
            
            fields = {
                "Context_Title": title,
                "Source_Name": source,
                "Source_URL": url or "",
                "Summary": summary or "",
                "Campaign_Potential": int(relevance * 5),
                "Status": "New",
                "Context_Type": "Other",
            }
            
            record = self.airtable.create_record("market_contexts", fields)
            
            return {"success": True, "trigger_id": record.get("id")}
        except Exception as e:
            return {"success": False, "errors": [str(e)]}
    
    # =========================================================================
    # FOLLOW-UP (Agent 8)
    # =========================================================================
    
    def get_hot_leads(
        self,
        lead_type: str = None,
        days: int = 7,
    ) -> list:
        """Get hot leads (clicks, responses, multiple opens).
        
        Args:
            lead_type: Filter by type (click, response, multiple_opens)
            days: Time range in days
            
        Returns:
            List of hot lead dicts
        """
        try:
            if not self.airtable:
                return []
            
            # Query campaign targets with hot lead status
            targets = self.airtable.query_records(
                "campaign_targets",
                max_records=100,
            )
            
            hot_leads = []
            for t in targets:
                fields = t.get("fields", {})
                status = fields.get("Status", "")
                
                # Filter for hot lead statuses
                if status in ["Clicked", "Replied", "Meeting_Scheduled"]:
                    action_type = "click" if status == "Clicked" else "response" if status == "Replied" else "meeting"
                    
                    # Get related data
                    contact_name = fields.get("Contact_Name", "Desconocido")
                    company_name = fields.get("Company_Name", "")
                    campaign_name = fields.get("Campaign_Name", "")
                    
                    hot_leads.append({
                        "target_id": t.get("id"),
                        "contact_name": contact_name,
                        "company_name": company_name,
                        "campaign_name": campaign_name,
                        "email": fields.get("Contact_Email", ""),
                        "action_type": action_type,
                        "action_detail": fields.get("Follow_Up_Notes", ""),
                        "response_preview": fields.get("Response_Summary", ""),
                        "timestamp": fields.get("Last_Interaction_Date"),
                        "priority": "urgent" if action_type == "response" else "high",
                    })
            
            return hot_leads
        except Exception as e:
            st.error(f"Error cargando hot leads: {e}")
            return []
    
    def get_followup_queue(self, status: str = None) -> list:
        """Get follow-up queue items.
        
        Args:
            status: Filter by status (pending, executed)
            
        Returns:
            List of follow-up task dicts
        """
        try:
            if not self.airtable:
                return []
            
            # Query followup queue table
            try:
                queue = self.airtable.query_records(
                    "followup_queue",
                    max_records=100,
                )
            except Exception:
                # Table might not exist yet
                return []
            
            result = []
            for item in queue:
                fields = item.get("fields", {})
                executed = fields.get("Executed", False)
                
                if status == "pending" and executed:
                    continue
                if status == "executed" and not executed:
                    continue
                
                result.append({
                    "id": item.get("id"),
                    "target_id": fields.get("Target_ID"),
                    "campaign_id": fields.get("Campaign_ID"),
                    "email": fields.get("Email"),
                    "followup_number": fields.get("Followup_Number", 1),
                    "scheduled_for": fields.get("Scheduled_For"),
                    "template": fields.get("Template", "followup_1"),
                    "executed": executed,
                    "executed_at": fields.get("Executed_At"),
                })
            
            return result
        except Exception as e:
            st.error(f"Error cargando cola de follow-up: {e}")
            return []
    
    def execute_followups(self, max_count: int = 10) -> dict:
        """Execute scheduled follow-ups that are due.
        
        Args:
            max_count: Maximum follow-ups to execute
            
        Returns:
            Dict with executed count
        """
        try:
            from agents.followup_manager import FollowupManager
            import asyncio
            
            manager = FollowupManager()
            
            # Run async execution
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                executed = loop.run_until_complete(manager.execute_scheduled_followups())
            finally:
                loop.close()
            
            return {"success": True, "executed": executed}
        except Exception as e:
            return {"success": False, "executed": 0, "errors": [str(e)]}
    
    def execute_single_followup(self, followup_id: str) -> dict:
        """Execute a single follow-up immediately."""
        try:
            if not self.airtable:
                return {"success": False, "errors": ["Airtable no disponible"]}
            
            # Get followup item
            item = self.airtable.get_record("followup_queue", followup_id)
            fields = item.get("fields", {})
            
            # Generate and send follow-up (simplified)
            from agents.followup_manager import FollowupManager
            import asyncio
            from datetime import datetime
            
            manager = FollowupManager()
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                subject, body = loop.run_until_complete(
                    manager.generate_followup_email(
                        fields.get("Target_ID"),
                        fields.get("Template", "followup_1"),
                    )
                )
            finally:
                loop.close()
            
            if subject and body:
                # Mark as executed
                self.airtable.update_record("followup_queue", followup_id, {
                    "Executed": True,
                    "Executed_At": datetime.now().isoformat(),
                })
                
                return {"success": True, "subject": subject}
            
            return {"success": False, "errors": ["No se pudo generar el follow-up"]}
        except Exception as e:
            return {"success": False, "errors": [str(e)]}
    
    def cancel_followup(self, followup_id: str) -> None:
        """Cancel a scheduled follow-up."""
        try:
            if self.airtable:
                # Simply delete the record or mark as cancelled
                self.airtable.update_record("followup_queue", followup_id, {
                    "Executed": True,  # Mark as executed to remove from queue
                    "Template": "cancelled",
                })
        except Exception as e:
            st.error(f"Error cancelando follow-up: {e}")
    
    def mark_lead_contacted(self, target_id: str) -> None:
        """Mark a hot lead as contacted."""
        try:
            if self.airtable:
                self.airtable.update_record("campaign_targets", target_id, {
                    "Status": "Meeting_Scheduled",
                    "Follow_Up_Notes": f"Contactado manualmente",
                })
        except Exception as e:
            st.error(f"Error actualizando lead: {e}")
    
    def schedule_meeting(self, target_id: str) -> None:
        """Schedule a meeting with a lead."""
        try:
            if self.airtable:
                from datetime import datetime
                self.airtable.update_record("campaign_targets", target_id, {
                    "Status": "Meeting_Scheduled",
                    "Last_Interaction_Date": datetime.now().isoformat(),
                })
        except Exception as e:
            st.error(f"Error programando reunión: {e}")
    
    def archive_lead(self, target_id: str) -> None:
        """Archive a lead."""
        try:
            if self.airtable:
                self.airtable.update_record("campaign_targets", target_id, {
                    "Follow_Up_Notes": "Archivado",
                })
        except Exception as e:
            st.error(f"Error archivando lead: {e}")
    
    def get_engagement_stats(self, days: int = 30) -> dict:
        """Get email engagement statistics.
        
        Args:
            days: Time range in days
            
        Returns:
            Dict with engagement metrics
        """
        try:
            if not self.airtable:
                return {}
            
            # Query campaign targets for stats
            targets = self.airtable.query_records(
                "campaign_targets",
                max_records=500,
            )
            
            total_sent = len([t for t in targets if t.get("fields", {}).get("Status") not in ["Pending_Review", "Approved"]])
            opened = len([t for t in targets if t.get("fields", {}).get("Status") in ["Opened", "Clicked", "Replied", "Meeting_Scheduled"]])
            clicked = len([t for t in targets if t.get("fields", {}).get("Status") in ["Clicked", "Replied", "Meeting_Scheduled"]])
            replied = len([t for t in targets if t.get("fields", {}).get("Status") in ["Replied", "Meeting_Scheduled"]])
            meetings = len([t for t in targets if t.get("fields", {}).get("Status") == "Meeting_Scheduled"])
            
            return {
                "total_sent": total_sent,
                "sent_last_7d": 0,  # Would calculate from dates
                "open_rate": opened / total_sent if total_sent > 0 else 0,
                "open_rate_trend": 0,
                "click_rate": clicked / total_sent if total_sent > 0 else 0,
                "click_rate_trend": 0,
                "response_rate": replied / total_sent if total_sent > 0 else 0,
                "response_rate_trend": 0,
                "meeting_rate": meetings / total_sent if total_sent > 0 else 0,
                "meetings_scheduled": meetings,
                "followup_stats": {
                    "followup_1_response_rate": 0.08,
                    "followup_2_response_rate": 0.05,
                    "total_converted": meetings,
                },
                "top_campaigns": [],  # Would aggregate by campaign
            }
        except Exception as e:
            st.error(f"Error calculando estadísticas: {e}")
            return {}


# Singleton instance
_api_instance = None


def get_api() -> OriginationAPI:
    """Get singleton API instance."""
    global _api_instance
    if _api_instance is None:
        _api_instance = OriginationAPI()
    return _api_instance
