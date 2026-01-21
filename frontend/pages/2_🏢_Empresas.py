"""Companies page for Alter-5 Origination Engine.

Two main sections:
1. Añadir Nuevas Empresas - Search and create new companies
2. Empresas en Airtable - View and enrich existing companies

Updated: 19 Enero 2026
- Multi-sector selection (up to 3)
- Multi-country selection (up to 3)
- Up to 100 companies search
- Better duplicate detection with fuzzy matching
- Fixed "Select All" button
- Show all results (not just new)
- Pagination for Airtable companies
- Additional filters (country, employees, revenue, company type)
- Fixed enrichment actions
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
import io
import asyncio
from difflib import SequenceMatcher

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.styles import inject_custom_css
from components.sidebar import render_sidebar
from utils.api import get_api
from utils.helpers import (
    format_currency,
    get_fei_status_emoji,
    truncate_text,
    get_company_sector_options,
    get_company_activity_options,
    get_country_options,
)
from components.feedback import (
    loading_spinner, 
    success_alert, 
    error_alert, 
    empty_state, 
    warning_alert,
)

# Page config
st.set_page_config(
    page_title="Empresas - Alter-5",
    page_icon="🏢",
    layout="wide",
)

inject_custom_css()
render_sidebar()

st.title("🏢 Empresas")
st.caption("Gestión completa de empresas: búsqueda, enriquecimiento y evaluación FEI")

st.markdown("---")

api = get_api()


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "search_selected" not in st.session_state:
    st.session_state.search_selected = set()
if "search_airtable_map" not in st.session_state:
    st.session_state.search_airtable_map = {}
if "airtable_selected" not in st.session_state:
    st.session_state.airtable_selected = set()

# Enrichment results for each tab
if "tab1_enrichment" not in st.session_state:
    st.session_state.tab1_enrichment = None
if "tab2_enrichment" not in st.session_state:
    st.session_state.tab2_enrichment = None

# Pagination for tab2
if "tab2_page" not in st.session_state:
    st.session_state.tab2_page = 0
if "tab2_page_size" not in st.session_state:
    st.session_state.tab2_page_size = 25

# All companies cache for deduplication
if "all_airtable_companies" not in st.session_state:
    st.session_state.all_airtable_companies = None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def similar(a: str, b: str) -> float:
    """Calculate similarity ratio between two strings."""
    if not a or not b:
        return 0.0
    a_clean = a.lower().strip()
    b_clean = b.lower().strip()
    return SequenceMatcher(None, a_clean, b_clean).ratio()

def normalize_domain(url: str) -> str:
    """Normalize a URL to compare domains."""
    if not url:
        return ""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url if url.startswith(("http://", "https://")) else f"https://{url}")
        domain = parsed.netloc.lower()
        return domain[4:] if domain.startswith("www.") else domain
    except Exception:
        return ""


def match_airtable_company(candidate: dict, airtable_companies: list, threshold: float = 0.9) -> tuple[dict | None, str | None, float | None]:
    """Match candidate with Airtable company using URL or name similarity."""
    if not candidate or not airtable_companies:
        return None, None, None

    name = candidate.get("name", candidate.get("Company Name", ""))
    url = candidate.get("home_url", candidate.get("Home URL", ""))
    candidate_domain = normalize_domain(url)

    best_match = None
    best_ratio = 0.0
    best_reason = None

    for company in airtable_companies:
        fields = company.get("fields", {})
        airtable_name = fields.get("Company Name", "")
        airtable_url = fields.get("Home URL", "")
        airtable_domain = normalize_domain(airtable_url)

        if candidate_domain and airtable_domain and candidate_domain == airtable_domain:
            return company, "same_domain", 1.0

        ratio = similar(name, airtable_name)
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = company
            best_reason = "high_name_similarity"

    if best_match and best_ratio >= threshold:
        return best_match, best_reason, best_ratio

    return None, None, None


def candidate_key(company: dict) -> str:
    """Build a stable key for a search candidate."""
    name = company.get("name", company.get("Company Name", ""))
    url = company.get("home_url", company.get("Home URL", ""))
    return f"{name.strip().lower()}|{str(url).strip().lower()}"


def update_search_airtable_map(candidates: list[dict]) -> None:
    """Populate Airtable ID map for search candidates."""
    mapping: dict[str, str] = {}
    for c in candidates:
        match = c.get("_airtable_match") or {}
        company_id = match.get("id")
        if company_id:
            mapping[candidate_key(c)] = company_id
    st.session_state.search_airtable_map = mapping


def render_enrichment_results(state_key: str, close_key: str) -> None:
    """Render enrichment results section for a given state key."""
    enrichment = st.session_state.get(state_key)
    if not enrichment:
        return

    enrichment_type = enrichment.get("type")
    enrichment_data = enrichment.get("data", [])

    st.markdown("---")

    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown("### 📊 Resultados del Enriquecimiento")
    with col2:
        if st.button("❌ Cerrar", key=close_key):
            st.session_state[state_key] = None
            st.rerun()

    if enrichment_type == "financial":
        successful = [r for r in enrichment_data if r.get("success")]
        failed = [r for r in enrichment_data if not r.get("success")]

        col1, col2 = st.columns(2)
        with col1:
            st.metric("✅ Éxito", len(successful))
        with col2:
            st.metric("❌ Errores", len(failed))

        if successful:
            st.markdown("#### Datos Encontrados:")
            df_data = []
            for r in successful:
                df_data.append({
                    "Empresa": r["company_name"],
                    "Empleados": r.get("employees") or "N/A",
                    "Facturación": format_currency(r.get("revenues")) if r.get("revenues") else "N/A",
                    "EBITDA": format_currency(r.get("ebitda")) if r.get("ebitda") else "N/A",
                    "LinkedIn": "✓" if r.get("linkedin") else "✗",
                })
            st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)

        if failed:
            with st.expander(f"❌ Ver {len(failed)} errores"):
                for r in failed:
                    st.error(f"**{r['company_name']}**: {r.get('error', 'Error desconocido')}")

        st.success("✅ Los datos se han guardado automáticamente en Airtable.")

    elif enrichment_type == "fei":
        eligible = [r for r in enrichment_data if r.get("status") == "Eligible"]
        not_eligible = [r for r in enrichment_data if r.get("status") == "Not_Eligible"]
        pending = [r for r in enrichment_data if r.get("status") not in ["Eligible", "Not_Eligible"]]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("✅ Elegibles", len(eligible))
        with col2:
            st.metric("❌ No Elegibles", len(not_eligible))
        with col3:
            st.metric("⏳ Pendientes/Otros", len(pending))

        st.markdown("#### Resultados Detallados:")
        df_data = []
        for r in enrichment_data:
            emoji = get_fei_status_emoji(r.get("status", "Unknown"))
            df_data.append({
                "Empresa": r["company_name"],
                "Estado": f"{emoji} {r.get('status', 'Unknown')}",
                "Confianza": f"{r.get('confidence', 0)*100:.0f}%" if r.get("confidence") else "N/A",
                "Criterios": ", ".join(r.get("criteria_met", [])) or "Ninguno",
            })
        st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)

        if eligible:
            with st.expander("📝 Ver razonamiento de empresas elegibles"):
                for r in eligible:
                    st.markdown(f"**{r['company_name']}:**")
                    st.markdown(f"> {r.get('reasoning', 'Sin razonamiento disponible')}")
                    st.markdown("---")

        st.success("✅ Las evaluaciones FEI se han guardado automáticamente en Airtable.")

    elif enrichment_type == "contacts":
        total_contacts = sum(len(r.get("contacts", [])) for r in enrichment_data)
        total_created = sum(r.get("contacts_created", 0) for r in enrichment_data)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("👥 Contactos Encontrados", total_contacts)
        with col2:
            st.metric("💾 Creados en Airtable", total_created)

        if total_contacts > 0:
            st.markdown("#### Contactos por Empresa:")

            for r in enrichment_data:
                contacts = r.get("contacts", [])
                if contacts:
                    st.markdown(f"**{r['company_name']}** ({len(contacts)} contactos)")

                    contact_data = []
                    for c in contacts:
                        contact_data.append({
                            "Nombre": c.get("name", "N/A"),
                            "Cargo": c.get("role", "N/A"),
                            "Email": c.get("email", "N/A"),
                            "LinkedIn": "✓" if c.get("linkedin") else "✗",
                        })
                    st.dataframe(pd.DataFrame(contact_data), use_container_width=True, hide_index=True)
                elif r.get("error"):
                    st.warning(f"**{r['company_name']}**: {r['error']}")

        st.success("✅ Los contactos encontrados se han guardado automáticamente en Airtable.")

    elif enrichment_type == "structure":
        successful = [r for r in enrichment_data if r.get("success")]

        st.markdown("#### Estructura Corporativa:")
        for r in enrichment_data:
            with st.expander(f"**{r['company_name']}**"):
                if r.get("parent_company"):
                    st.markdown(f"**Parent:** {r['parent_company']}")
                if r.get("ultimate_parent"):
                    st.markdown(f"**Ultimate Parent:** {r['ultimate_parent']}")
                if r.get("subsidiaries"):
                    st.markdown(f"**Subsidiarias:** {', '.join(r['subsidiaries'])}")
                if r.get("error"):
                    st.error(r["error"])

        st.success(f"✅ Estructura analizada para {len(successful)}/{len(enrichment_data)} empresas.")

    elif enrichment_type == "business_units":
        total_created = sum(r.get("bus_created", 0) for r in enrichment_data)
        total_updated = sum(r.get("bus_updated", 0) for r in enrichment_data)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("✅ Nuevas BU", total_created)
        with col2:
            st.metric("🔄 Actualizadas", total_updated)

        for r in enrichment_data:
            with st.expander(f"**{r['company_name']}**"):
                if r.get("bus_list"):
                    st.markdown("**Business Units:**")
                    for bu in r["bus_list"]:
                        st.markdown(f"- {bu}")
                if r.get("error"):
                    st.error(r["error"])

        st.success("✅ Business Units sincronizadas con Airtable.")


def get_airtable_url(record_id: str) -> str:
    """Generate Airtable URL for a record."""
    base_id = "appEgNSP0tOLJ9YJ9"
    table_id = "tbl47AWmhYAXerbWz"  # Stakeholders_Companies table
    return f"https://airtable.com/{base_id}/{table_id}/{record_id}"


def sync_checkbox_with_selection(state_key: str, num_items: int):
    """Sync individual checkbox states with the selection set."""
    selection_set = st.session_state.get(state_key, set())
    for i in range(num_items):
        checkbox_key = f"chk_{state_key}_{i}"
        if checkbox_key in st.session_state:
            # Sync checkbox state FROM selection set
            st.session_state[checkbox_key] = i in selection_set


def update_selection_from_checkbox(idx: int, state_key: str, checkbox_key: str):
    """Callback to update selection set when checkbox changes."""
    new_value = st.session_state.get(checkbox_key, False)
    if new_value:
        st.session_state[state_key].add(idx)
    else:
        st.session_state[state_key].discard(idx)


def display_company_card(
    company: dict, 
    idx: int, 
    state_key: str,
    show_airtable_link: bool = False,
    airtable_match: dict | None = None,
    is_search_result: bool = False,
):
    """Display a company card with standardized information.
    
    Shows: Name, Country, URL, LinkedIn URL, Airtable URL (if saved or similar), Employees, Revenue, EBITDA, FEI Status
    
    Args:
        company: Company data dict
        idx: Index for selection tracking
        state_key: Session state key for selection set
        show_airtable_link: If True, company is already in Airtable
        airtable_match: Similar company found in Airtable (if any)
        is_search_result: If True, show Airtable status indicators for search results
    """
    fields = company.get("fields", company)
    record_id = company.get("id", "")
    
    name = fields.get("Company Name", fields.get("name", "Sin nombre"))
    url = fields.get("Home URL", fields.get("home_url", ""))
    linkedin_url = fields.get("Linkedin URL", fields.get("linkedin_url", ""))
    employees = fields.get("Num Employees", fields.get("estimated_employees"))
    revenues = fields.get("Revenues", fields.get("revenues"))
    ebitda = fields.get("EBITDA", fields.get("ebitda"))
    fei_status = fields.get("FEI_Status", "Unknown") or "Unknown"
    
    # Get country
    country = fields.get("HQ Country", fields.get("hq_country", fields.get("country", "")))
    if isinstance(country, list):
        country = country[0] if country else ""
    country_str = country if country else "N/A"
    
    # Determine if selected from the selection set
    is_selected = idx in st.session_state.get(state_key, set())
    
    # Create card layout
    col_check, col_content = st.columns([1, 20])
    
    with col_check:
        checkbox_key = f"chk_{state_key}_{idx}"
        # Initialize checkbox state if not present, synced with selection set
        if checkbox_key not in st.session_state:
            st.session_state[checkbox_key] = is_selected
        
        st.checkbox(
            "Sel",
            key=checkbox_key,
            label_visibility="collapsed",
            on_change=update_selection_from_checkbox,
            args=(idx, state_key, checkbox_key),
        )
    
    with col_content:
        fei_emoji = get_fei_status_emoji(fei_status)
        
        # Create header with key info
        employees_str = str(employees) if employees else "N/A"
        revenue_str = format_currency(revenues) if revenues else "N/A"
        
        # Determine Airtable status for display
        # For search results, show explicit status
        if is_search_result:
            is_in_airtable = company.get("_is_in_airtable", False)
            match_reason = company.get("_match_reason")
            match_confidence = company.get("_match_confidence")
            if is_in_airtable and airtable_match:
                airtable_icon = "✅"
                airtable_status = "En Airtable (URL igual)"
            elif airtable_match:
                airtable_icon = "⚠️"
                match_name = airtable_match.get("fields", {}).get("Company Name", "")
                conf = f"{match_confidence*100:.0f}%" if match_confidence else "alta"
                airtable_status = f"Similar ({conf}): '{truncate_text(match_name, 25)}'"
            else:
                airtable_icon = "🆕"
                airtable_status = "Nueva"
            status_indicator = f"{airtable_icon} {airtable_status}"
        else:
            # For Airtable tab
            if show_airtable_link and record_id:
                status_indicator = "✅ En Airtable"
            else:
                status_indicator = ""
        
        # Build header with country
        header = f"**{name}** | 🌍 {country_str} | 👥 {employees_str} | 💰 {revenue_str} | {fei_emoji} {fei_status}"
        if status_indicator:
            header += f" | {status_indicator}"
        
        with st.expander(header):
            # Row 1: URLs and Airtable link
            url_cols = st.columns(4)
            with url_cols[0]:
                if url:
                    st.markdown(f"🌐 **Web:** [{truncate_text(url, 30)}]({url})")
                else:
                    st.markdown("🌐 **Web:** N/A")
            with url_cols[1]:
                if linkedin_url:
                    st.markdown(f"💼 **LinkedIn:** [Ver perfil]({linkedin_url})")
                else:
                    st.markdown("💼 **LinkedIn:** N/A")
            with url_cols[2]:
                st.markdown(f"🌍 **País:** {country_str}")
            with url_cols[3]:
                # Always show Airtable link section
                if show_airtable_link and record_id:
                    airtable_url = get_airtable_url(record_id)
                    st.markdown(f"📋 **Airtable:** [Ver]({airtable_url})")
                elif airtable_match:
                    match_id = airtable_match.get("id", "")
                    if match_id:
                        airtable_url = get_airtable_url(match_id)
                        st.markdown(f"📋 **Similar:** [Ver]({airtable_url})")
                    else:
                        st.markdown("📋 **Airtable:** —")
                else:
                    st.markdown("📋 **Airtable:** —")
            
            # Row 2: Financial data
            fin_cols = st.columns(3)
            with fin_cols[0]:
                st.markdown(f"👥 **Empleados:** {employees_str}")
            with fin_cols[1]:
                st.markdown(f"💰 **Facturación:** {revenue_str}")
            with fin_cols[2]:
                ebitda_str = format_currency(ebitda) if ebitda else "N/A"
                st.markdown(f"📊 **EBITDA:** {ebitda_str}")
            
            # Row 3: FEI and description
            st.markdown(f"🏷️ **FEI Status:** {fei_emoji} {fei_status}")
            
            description = fields.get("Description", fields.get("description", ""))
            if description:
                st.info(f"📝 {truncate_text(str(description), 300)}")
            
            # Show match warning if applicable (for search results)
            if is_search_result and airtable_match:
                match_fields = airtable_match.get("fields", {})
                match_country = match_fields.get("HQ Country", "")
                if isinstance(match_country, list):
                    match_country = match_country[0] if match_country else ""
                
                reason = company.get("_match_reason") or "similaridad"
                st.warning(f"""
                ⚠️ **Posible duplicado detectado ({reason}):**  
                Empresa en Airtable: **"{match_fields.get('Company Name', 'N/A')}"** ({match_country or 'País desconocido'})  
                Revisa antes de guardar. Si es la misma empresa en diferente país/actividad, se puede crear una Business Unit.
                """)


def generate_csv_companies(companies: list) -> str:
    """Generate CSV for companies with all standard columns."""
    headers = [
        "Company Name", 
        "Home URL", 
        "Linkedin URL",
        "Num Employees", 
        "Revenues", 
        "EBITDA", 
        "FEI_Status",
        "Description",
        "HQ Country",
        "Sector",
    ]
    
    rows = []
    for c in companies:
        fields = c.get("fields", c)
        country = fields.get("HQ Country", fields.get("country", ""))
        if isinstance(country, list):
            country = country[0] if country else ""
        sector = fields.get("Sector", fields.get("sector", ""))
        if isinstance(sector, list):
            sector = ", ".join(str(s) for s in sector)
        elif sector is None:
            sector = ""
        else:
            sector = str(sector)
        
        rows.append([
            fields.get("Company Name", fields.get("name", "")),
            fields.get("Home URL", fields.get("home_url", "")),
            fields.get("Linkedin URL", fields.get("linkedin_url", "")),
            str(fields.get("Num Employees", fields.get("estimated_employees", ""))),
            str(fields.get("Revenues", fields.get("revenues", ""))),
            str(fields.get("EBITDA", fields.get("ebitda", ""))),
            fields.get("FEI_Status", fields.get("fei_status", "")),
            str(fields.get("Description", fields.get("description", ""))).replace('"', "'")[:500],
            country,
            sector,
        ])
    
    output = io.StringIO()
    output.write(",".join(f'"{h}"' for h in headers) + "\n")
    for row in rows:
        output.write(",".join(f'"{v}"' for v in row) + "\n")
    
    return output.getvalue()


def load_all_airtable_companies():
    """Load all companies from Airtable for deduplication."""
    if st.session_state.all_airtable_companies is None:
        with st.spinner("Cargando empresas de Airtable para verificación de duplicados..."):
            companies, _ = api.get_companies(limit=5000)  # Get all
            st.session_state.all_airtable_companies = companies or []
    return st.session_state.all_airtable_companies


# ============================================================================
# MAIN TABS
# ============================================================================

tab1, tab2 = st.tabs([
    "➕ Añadir Nuevas Empresas",
    "📋 Empresas en Airtable"
])


# ============================================================================
# TAB 1: AÑADIR NUEVAS EMPRESAS
# ============================================================================

with tab1:
    st.markdown("### 🔍 Buscar Nuevas Empresas")
    
    # Row 1: Sectors, Activities and Countries (multiselect)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sector_options = get_company_sector_options()
        selected_sectors = st.multiselect(
            "Sectores * (máx 3)",
            options=sector_options,
            max_selections=3,
            key="t1_sectors",
            help="Selecciona hasta 3 sectores para la búsqueda",
        )
    
    with col2:
        activity_options = get_company_activity_options(selected_sectors)
        selected_activities = st.multiselect(
            "Actividad (opcional)",
            options=activity_options,
            key="t1_activities",
            disabled=not selected_sectors,
            help="Actividades asociadas a los sectores seleccionados",
        )

    with col3:
        country_options = get_country_options()
        country_display = {code: name for code, name in country_options}
        selected_countries = st.multiselect(
            "Países * (máx 3)",
            options=[code for code, _ in country_options],
            format_func=lambda x: country_display.get(x, x),
            max_selections=3,
            key="t1_countries",
            help="Selecciona hasta 3 países para la búsqueda",
        )
    
    # Row 2: Region, keywords, max companies
    col1, col2, col3 = st.columns(3)
    
    with col1:
        region = st.text_input("Región (opcional)", placeholder="Ej: Cataluña, Madrid", key="t1_region")
    
    with col2:
        keywords = st.text_input("Palabras clave (opcional)", placeholder="Ej: solar, eólica", key="t1_keywords")
    
    with col3:
        max_companies = st.slider("Máximo empresas", 5, 100, 20, step=5, key="t1_max")
    
    # Search button
    search_enabled = len(selected_sectors) > 0 and len(selected_countries) > 0
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "🔍 BUSCAR EMPRESAS", 
            type="primary", 
            use_container_width=True, 
            disabled=not search_enabled, 
            key="t1_search"
        ):
            # Load Airtable companies for deduplication
            airtable_companies = load_all_airtable_companies()
            
            with st.spinner(f"🔍 Buscando empresas en {len(selected_sectors)} sector(es) y {len(selected_countries)} país(es)... (30-90 segundos)"):
                all_results = []
                
                for sector in selected_sectors:
                    for country in selected_countries:
                        search_keywords = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else []
                        if selected_activities:
                            for activity in selected_activities:
                                if activity not in search_keywords:
                                    search_keywords.append(activity)

                        result = api.search_companies(
                            sector=sector,
                            country=country,
                            region=region if region else None,
                            keywords=search_keywords,
                            limit=max_companies // max(1, len(selected_sectors) * len(selected_countries)) + 5,
                            save_to_airtable=False,
                        )
                        
                        if result.get("success"):
                            for c in result.get("candidates_found", []):
                                c_name = c.get("name", c.get("Company Name", ""))
                                is_dup = any(
                                    similar(c_name, existing.get("name", existing.get("Company Name", ""))) > 0.9
                                    for existing in all_results
                                )
                                if not is_dup:
                                    airtable_match, match_reason, match_confidence = match_airtable_company(c, airtable_companies)
                                    c["_airtable_match"] = airtable_match
                                    c["_match_reason"] = match_reason
                                    c["_match_confidence"] = match_confidence
                                    c["_is_in_airtable"] = match_reason == "same_domain"
                                    all_results.append(c)
                
                all_results = all_results[:max_companies]
            
            st.session_state.search_results = {
                "success": True,
                "candidates_found": all_results,
            }
            st.session_state.search_selected = set()
            st.session_state.tab1_enrichment = None
            update_search_airtable_map(all_results)
            
            st.success(f"✅ Encontradas {len(all_results)} empresas")
    
    if not search_enabled:
        st.info("👆 Selecciona al menos 1 sector y 1 país para buscar empresas.")
    
    # Display results
    if st.session_state.search_results and st.session_state.search_results.get("success"):
        candidates = st.session_state.search_results.get("candidates_found", [])
        
        if candidates:
            st.markdown("---")
            
            # Metrics
            new_count = sum(1 for c in candidates if not c.get("_is_in_airtable"))
            existing_count = sum(1 for c in candidates if c.get("_is_in_airtable"))
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Encontradas", len(candidates))
            with col2:
                st.metric("🆕 Nuevas", new_count)
            with col3:
                st.metric("📋 Ya en Airtable", existing_count)
            with col4:
                st.metric("✔️ Seleccionadas", len(st.session_state.search_selected))
            
            st.markdown("---")
            st.markdown("### 📋 Empresas Encontradas")
            
            # Legend
            st.markdown("""
            **Leyenda:** 🆕 = Nueva | ⚠️ = Similar en Airtable (posible duplicado) | ✅ = Ya guardada
            """)
            
            # Select/Deselect buttons
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("✅ Seleccionar Todas", key="t1_sel_all", use_container_width=True):
                    st.session_state.search_selected = set(range(len(candidates)))
                    # Sync checkboxes with selection
                    for i in range(len(candidates)):
                        st.session_state[f"chk_search_selected_{i}"] = True
                    st.rerun()
            with col2:
                if st.button("❌ Deseleccionar Todas", key="t1_desel", use_container_width=True):
                    # Clear selection set and checkboxes
                    for i in range(len(candidates)):
                        checkbox_key = f"chk_search_selected_{i}"
                        if checkbox_key in st.session_state:
                            st.session_state[checkbox_key] = False
                    st.session_state.search_selected = set()
                    st.rerun()
            
            # Display all companies (not just new ones)
            for idx, candidate in enumerate(candidates):
                airtable_match = candidate.get("_airtable_match")
                is_in_airtable = candidate.get("_is_in_airtable", False)
                
                display_company_card(
                    company=candidate,
                    idx=idx,
                    state_key="search_selected",
                    show_airtable_link=is_in_airtable,
                    airtable_match=airtable_match,
                    is_search_result=True,
                )
            
            st.markdown("---")
            st.markdown("### 💾 Acciones")
            
            selected_indices = list(st.session_state.search_selected)
            selected_candidates = [candidates[i] for i in selected_indices if i < len(candidates)]
            
            # Categorize selected companies
            truly_new = []  # No match at all
            has_similar = []  # Has similar match, needs review
            already_exists = []  # Exact match, already in Airtable
            
            for c in selected_candidates:
                is_in_airtable = c.get("_is_in_airtable", False)
                airtable_match = c.get("_airtable_match")
                
                if is_in_airtable:
                    already_exists.append(c)
                elif airtable_match:
                    has_similar.append(c)
                else:
                    truly_new.append(c)
            
            # Export button
            col1, col2 = st.columns(2)
            
            with col1:
                to_export = selected_candidates if selected_candidates else candidates
                csv = generate_csv_companies(to_export)
                st.download_button(
                    f"📥 Exportar CSV ({len(to_export)})",
                    data=csv,
                    file_name=f"empresas_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            
            with col2:
                # Summary metrics
                st.markdown(f"""
                **Resumen selección:**  
                🆕 Nuevas: {len(truly_new)} | ⚠️ Similares: {len(has_similar)} | ✅ Ya existen: {len(already_exists)}
                """)
            
            st.markdown("---")
            
            # Section 1: Save truly new companies
            if truly_new:
                st.markdown("#### 🆕 Empresas Nuevas (sin coincidencias)")
                st.success(f"✅ {len(truly_new)} empresas listas para guardar directamente.")
                
                if st.button(
                    f"💾 Guardar {len(truly_new)} empresas nuevas", 
                    type="primary", 
                    use_container_width=True, 
                    key="t1_save_new",
                ):
                    with st.spinner(f"Guardando {len(truly_new)} empresas..."):
                        candidate_keys = [candidate_key(c) for c in truly_new]
                        result = api.save_companies(truly_new)
                    
                    if result.get("success"):
                        st.success(f"✅ {len(result.get('companies_created', []))} empresas guardadas")
                        created_ids = result.get("companies_created", [])
                        for key, company_id in zip(candidate_keys, created_ids):
                            if company_id:
                                st.session_state.search_airtable_map[key] = company_id
                        st.session_state.all_airtable_companies = None
                        st.info("💡 Ve a 'Empresas en Airtable' para enriquecer los datos.")
                    else:
                        st.error(f"Error: {result.get('errors', [])}")
            
            # Section 2: Handle companies with similar matches
            if has_similar:
                st.markdown("---")
                st.markdown("#### ⚠️ Empresas con Coincidencias Similares")
                st.warning(f"""
                **{len(has_similar)} empresas** tienen nombres similares a empresas existentes en Airtable.  
                Revisa cada una para decidir si:
                - Es una **empresa diferente** → Guardar como nueva
                - Es la **misma empresa** en diferente país/actividad → Crear Business Unit
                - Es un **duplicado** → No guardar
                """)
                
                # Initialize session state for similar companies decisions
                if "similar_decisions" not in st.session_state:
                    st.session_state.similar_decisions = {}
                
                for idx, company in enumerate(has_similar):
                    c_name = company.get("name", company.get("Company Name", "Sin nombre"))
                    c_country = company.get("country", company.get("HQ Country", ""))
                    if isinstance(c_country, list):
                        c_country = c_country[0] if c_country else ""
                    
                    airtable_match = company.get("_airtable_match", {})
                    match_fields = airtable_match.get("fields", {})
                    match_name = match_fields.get("Company Name", "N/A")
                    match_country = match_fields.get("HQ Country", "")
                    if isinstance(match_country, list):
                        match_country = match_country[0] if match_country else ""
                    match_id = airtable_match.get("id", "")
                    
                    with st.expander(f"**{c_name}** ({c_country}) ↔ **{match_name}** ({match_country})", expanded=True):
                        col_info, col_action = st.columns([2, 1])
                        
                        with col_info:
                            st.markdown(f"""
                            | Encontrada | En Airtable |
                            |------------|-------------|
                            | **{c_name}** | **{match_name}** |
                            | 🌍 {c_country or 'N/A'} | 🌍 {match_country or 'N/A'} |
                            """)
                            if match_id:
                                st.markdown(f"📋 [Ver empresa existente en Airtable]({get_airtable_url(match_id)})")
                        
                        with col_action:
                            decision_key = f"decision_{idx}"
                            decision = st.radio(
                                "Acción:",
                                options=["skip", "new_company", "new_bu"],
                                format_func=lambda x: {
                                    "skip": "❌ No guardar (duplicado)",
                                    "new_company": "🆕 Guardar como empresa nueva",
                                    "new_bu": "🏢 Crear Business Unit",
                                }[x],
                                key=f"t1_similar_{idx}",
                                index=0,
                            )
                            st.session_state.similar_decisions[idx] = {
                                "decision": decision,
                                "company": company,
                                "match": airtable_match,
                            }
                
                # Process similar companies button
                if st.button("✅ Procesar empresas similares", type="primary", key="t1_process_similar"):
                    saved_new = 0
                    created_bus = 0
                    skipped = 0
                    errors = []
                    
                    with st.spinner("Procesando decisiones..."):
                        for idx, data in st.session_state.similar_decisions.items():
                            decision = data["decision"]
                            company = data["company"]
                            match = data["match"]
                            
                            if decision == "skip":
                                skipped += 1
                            elif decision == "new_company":
                                # Save as new company
                                result = api.save_companies([company])
                                if result.get("success"):
                                    saved_new += 1
                                    created_id = None
                                    created_ids = result.get("companies_created", [])
                                    if created_ids:
                                        created_id = created_ids[0]
                                    if created_id:
                                        st.session_state.search_airtable_map[candidate_key(company)] = created_id
                                else:
                                    errors.extend(result.get("errors", []))
                            elif decision == "new_bu":
                                # Create Business Unit for existing company
                                match_id = match.get("id", "")
                                if match_id:
                                    c_name = company.get("name", company.get("Company Name", ""))
                                    c_country = company.get("country", company.get("HQ Country", ""))
                                    if isinstance(c_country, list):
                                        c_country = c_country[0] if c_country else ""
                                    
                                    bu_result = api.create_business_unit(
                                        company_id=match_id,
                                        bu_name=f"{c_name} - {c_country}" if c_country else c_name,
                                        bu_country=c_country,
                                    )
                                    if bu_result.get("success"):
                                        created_bus += 1
                                        st.session_state.search_airtable_map[candidate_key(company)] = match_id
                                    else:
                                        errors.extend(bu_result.get("errors", []))
                    
                    # Show results
                    if saved_new > 0:
                        st.success(f"✅ {saved_new} empresas guardadas como nuevas")
                    if created_bus > 0:
                        st.success(f"🏢 {created_bus} Business Units creadas")
                    if skipped > 0:
                        st.info(f"⏭️ {skipped} empresas omitidas")
                    if errors:
                        st.error(f"❌ Errores: {errors}")
                    
                    # Refresh cache
                    st.session_state.all_airtable_companies = None
                    st.session_state.similar_decisions = {}
            
            # Section 3: Already existing companies
            if already_exists:
                st.markdown("---")
                st.info(f"ℹ️ **{len(already_exists)} empresas** ya están en Airtable. Puedes enriquecerlas en la pestaña 'Empresas en Airtable'.")

            # ===== Enrichment actions for search results =====
            st.markdown("---")
            st.markdown("### ⚡ Acciones de Enriquecimiento (Airtable)")
            st.info("📌 Guarda o vincula empresas en Airtable para poder enriquecerlas desde aquí.")

            selected_indices = list(st.session_state.search_selected)
            selected_candidates = [candidates[i] for i in selected_indices if i < len(candidates)]

            selected_airtable_companies = []
            missing_enrichment = []

            for company in selected_candidates:
                key = candidate_key(company)
                company_id = st.session_state.search_airtable_map.get(key)

                if not company_id:
                    match = company.get("_airtable_match") or {}
                    company_id = match.get("id")

                if not company_id:
                    missing_enrichment.append(company)
                    continue

                company_name = company.get("name", company.get("Company Name", "N/A"))
                company_url = company.get("home_url", company.get("Home URL", ""))

                match_fields = (company.get("_airtable_match") or {}).get("fields", {})
                if match_fields:
                    company_name = match_fields.get("Company Name", company_name)
                    company_url = match_fields.get("Home URL", company_url)

                selected_airtable_companies.append({
                    "id": company_id,
                    "fields": {
                        "Company Name": company_name,
                        "Home URL": company_url,
                    }
                })

            if missing_enrichment:
                st.warning(f"⚠️ {len(missing_enrichment)} seleccionadas no están guardadas en Airtable. Guárdalas para enriquecer.")

            has_airtable_selection = len(selected_airtable_companies) > 0

            action_cols = st.columns(5)

            with action_cols[0]:
                t1_btn_financial = st.button(
                    "💰 Datos Financieros",
                    use_container_width=True,
                    disabled=not has_airtable_selection,
                    key="t1_btn_financial",
                )

            with action_cols[1]:
                t1_btn_structure = st.button(
                    "🏗️ Estructura",
                    use_container_width=True,
                    disabled=not has_airtable_selection,
                    key="t1_btn_structure",
                )

            with action_cols[2]:
                t1_btn_fei = st.button(
                    "🏷️ Evaluación FEI",
                    use_container_width=True,
                    disabled=not has_airtable_selection,
                    key="t1_btn_fei",
                )

            with action_cols[3]:
                t1_btn_bus = st.button(
                    "🏢 Business Units",
                    use_container_width=True,
                    disabled=not has_airtable_selection,
                    key="t1_btn_bus",
                )

            with action_cols[4]:
                t1_btn_contacts = st.button(
                    "👥 Buscar Contactos",
                    use_container_width=True,
                    disabled=not has_airtable_selection,
                    key="t1_btn_contacts",
                )

            if t1_btn_financial and has_airtable_selection:
                st.markdown("---")
                st.markdown("### 💰 Enriqueciendo Datos Financieros...")

                progress_bar = st.progress(0)
                status_text = st.empty()

                results = []
                for idx, company in enumerate(selected_airtable_companies):
                    fields = company.get("fields", {})
                    company_name = fields.get("Company Name", "N/A")
                    company_id = company.get("id")
                    company_url = fields.get("Home URL", "")

                    status_text.text(f"Procesando {idx+1}/{len(selected_airtable_companies)}: {company_name}")
                    progress_bar.progress((idx + 1) / len(selected_airtable_companies))

                    result_entry = {
                        "company_name": company_name,
                        "company_id": company_id,
                        "success": False,
                        "employees": None,
                        "revenues": None,
                        "ebitda": None,
                        "linkedin": None,
                        "error": None,
                    }

                    try:
                        enrich_result = api.enrich_company(
                            company_id,
                            company_name=company_name,
                            company_url=company_url,
                            include_financials=True,
                            include_contacts=False,
                        )

                        if hasattr(enrich_result, "success") and enrich_result.success:
                            result_entry["success"] = True
                            if hasattr(enrich_result, "company_info") and enrich_result.company_info:
                                result_entry["employees"] = enrich_result.company_info.num_employees
                                result_entry["linkedin"] = enrich_result.company_info.linkedin_url
                            if hasattr(enrich_result, "financial_info") and enrich_result.financial_info:
                                result_entry["revenues"] = enrich_result.financial_info.annual_revenues
                                result_entry["ebitda"] = enrich_result.financial_info.ebitda
                        elif isinstance(enrich_result, dict):
                            result_entry["success"] = enrich_result.get("success", False)
                            if result_entry["success"]:
                                result_entry["employees"] = enrich_result.get("num_employees")
                                result_entry["revenues"] = enrich_result.get("revenues")
                                result_entry["ebitda"] = enrich_result.get("ebitda")
                                result_entry["linkedin"] = enrich_result.get("linkedin_url")
                            result_entry["error"] = str(enrich_result.get("errors", [])) if not result_entry["success"] else None
                        else:
                            result_entry["error"] = "Resultado no reconocido"

                    except Exception as e:
                        result_entry["error"] = str(e)

                    results.append(result_entry)

                progress_bar.empty()
                status_text.empty()

                st.session_state.tab1_enrichment = {"type": "financial", "data": results}

            if t1_btn_fei and has_airtable_selection:
                st.markdown("---")
                st.markdown("### 🏷️ Evaluando Elegibilidad FEI...")

                progress_bar = st.progress(0)
                status_text = st.empty()

                results = []
                for idx, company in enumerate(selected_airtable_companies):
                    fields = company.get("fields", {})
                    company_name = fields.get("Company Name", "N/A")
                    company_id = company.get("id")

                    status_text.text(f"Evaluando {idx+1}/{len(selected_airtable_companies)}: {company_name}")
                    progress_bar.progress((idx + 1) / len(selected_airtable_companies))

                    result_entry = {
                        "company_name": company_name,
                        "company_id": company_id,
                        "status": "Unknown",
                        "confidence": 0,
                        "criteria_met": [],
                        "reasoning": "",
                        "error": None,
                    }

                    try:
                        fei_result = api.evaluate_fei(company_id, force=True)

                        if hasattr(fei_result, "status"):
                            status_val = fei_result.status.value if hasattr(fei_result.status, "value") else str(fei_result.status)
                            result_entry["status"] = status_val
                            result_entry["confidence"] = getattr(fei_result, "confidence", 0)

                            criteria = getattr(fei_result, "criteria_met", [])
                            if criteria:
                                result_entry["criteria_met"] = [c.value if hasattr(c, "value") else str(c) for c in criteria]

                            result_entry["reasoning"] = getattr(fei_result, "reasoning", "")
                        elif isinstance(fei_result, dict):
                            result_entry["status"] = fei_result.get("status", "Unknown")
                            result_entry["confidence"] = fei_result.get("confidence", 0)
                            result_entry["criteria_met"] = fei_result.get("criteria_met", [])
                            result_entry["reasoning"] = fei_result.get("reasoning", "")
                            result_entry["error"] = str(fei_result.get("errors", [])) if fei_result.get("errors") else None
                        else:
                            result_entry["error"] = "Resultado no reconocido"

                    except Exception as e:
                        result_entry["error"] = str(e)

                    results.append(result_entry)

                progress_bar.empty()
                status_text.empty()

                st.session_state.tab1_enrichment = {"type": "fei", "data": results}

            if t1_btn_contacts and has_airtable_selection:
                st.markdown("---")
                st.markdown("### 👥 Buscando Contactos...")

                progress_bar = st.progress(0)
                status_text = st.empty()

                results = []
                for idx, company in enumerate(selected_airtable_companies):
                    fields = company.get("fields", {})
                    company_name = fields.get("Company Name", "N/A")
                    company_id = company.get("id")
                    company_url = fields.get("Home URL", "")

                    status_text.text(f"Buscando {idx+1}/{len(selected_airtable_companies)}: {company_name}")
                    progress_bar.progress((idx + 1) / len(selected_airtable_companies))

                    result_entry = {
                        "company_name": company_name,
                        "company_id": company_id,
                        "contacts": [],
                        "contacts_created": 0,
                        "error": None,
                    }

                    try:
                        contacts_result = api.enrich_company(
                            company_id,
                            company_name=company_name,
                            company_url=company_url,
                            include_financials=False,
                            include_contacts=True,
                        )

                        if hasattr(contacts_result, "key_persons") and contacts_result.key_persons:
                            result_entry["contacts"] = [
                                {
                                    "name": p.get("name", ""),
                                    "role": p.get("role", ""),
                                    "email": p.get("email", ""),
                                    "linkedin": p.get("linkedin_url", ""),
                                }
                                for p in contacts_result.key_persons
                            ]
                            result_entry["contacts_created"] = len(contacts_result.key_persons)
                        elif isinstance(contacts_result, dict):
                            persons = contacts_result.get("key_persons", [])
                            result_entry["contacts"] = persons
                            result_entry["contacts_created"] = contacts_result.get("contacts_created", len(persons))
                            if not contacts_result.get("success"):
                                result_entry["error"] = str(contacts_result.get("errors", []))
                        else:
                            result_entry["error"] = "Resultado no reconocido"

                    except Exception as e:
                        result_entry["error"] = str(e)

                    results.append(result_entry)

                progress_bar.empty()
                status_text.empty()

                st.session_state.tab1_enrichment = {"type": "contacts", "data": results}

            if t1_btn_structure and has_airtable_selection:
                st.markdown("---")
                st.markdown("### 🏗️ Analizando Estructura Corporativa...")

                progress_bar = st.progress(0)
                status_text = st.empty()

                results = []
                for idx, company in enumerate(selected_airtable_companies):
                    fields = company.get("fields", {})
                    company_name = fields.get("Company Name", "N/A")
                    company_id = company.get("id")
                    company_url = fields.get("Home URL", "")

                    status_text.text(f"Procesando {idx+1}/{len(selected_airtable_companies)}: {company_name}")
                    progress_bar.progress((idx + 1) / len(selected_airtable_companies))

                    result_entry = {
                        "company_name": company_name,
                        "company_id": company_id,
                        "parent_company": None,
                        "ultimate_parent": None,
                        "subsidiaries": [],
                        "success": False,
                        "error": None,
                    }

                    try:
                        structure_result = api.enrich_structure(company_id)
                        if isinstance(structure_result, dict):
                            result_entry["success"] = structure_result.get("success", False)
                            result_entry["parent_company"] = structure_result.get("parent_company")
                            result_entry["ultimate_parent"] = structure_result.get("ultimate_parent")
                            result_entry["subsidiaries"] = structure_result.get("subsidiaries", [])
                            if not result_entry["success"]:
                                result_entry["error"] = str(structure_result.get("errors", []))
                        else:
                            result_entry["error"] = "Resultado no reconocido"

                    except Exception as e:
                        result_entry["error"] = str(e)

                    results.append(result_entry)

                progress_bar.empty()
                status_text.empty()

                st.session_state.tab1_enrichment = {"type": "structure", "data": results}

            if t1_btn_bus and has_airtable_selection:
                st.markdown("---")
                st.markdown("### 🏢 Gestionando Business Units...")

                progress_bar = st.progress(0)
                status_text = st.empty()

                results = []
                for idx, company in enumerate(selected_airtable_companies):
                    fields = company.get("fields", {})
                    company_name = fields.get("Company Name", "N/A")
                    company_id = company.get("id")

                    status_text.text(f"Procesando {idx+1}/{len(selected_airtable_companies)}: {company_name}")
                    progress_bar.progress((idx + 1) / len(selected_airtable_companies))

                    result_entry = {
                        "company_name": company_name,
                        "company_id": company_id,
                        "bus_created": 0,
                        "bus_updated": 0,
                        "bus_list": [],
                        "success": False,
                        "error": None,
                    }

                    try:
                        bu_result = api.get_or_create_business_units(company_id, company_name)
                        if isinstance(bu_result, dict):
                            result_entry["bus_created"] = bu_result.get("created", 0)
                            result_entry["bus_updated"] = bu_result.get("updated", 0)
                            result_entry["bus_list"] = bu_result.get("business_units", [])
                            result_entry["success"] = bu_result.get("success", False)
                            if not result_entry["success"]:
                                result_entry["error"] = str(bu_result.get("errors", []))
                        else:
                            result_entry["success"] = True
                            result_entry["bus_created"] = 1
                    except Exception as e:
                        result_entry["error"] = str(e)

                    results.append(result_entry)

                progress_bar.empty()
                status_text.empty()

                st.session_state.tab1_enrichment = {"type": "business_units", "data": results}

            render_enrichment_results("tab1_enrichment", "t1_close_enrichment")


# ============================================================================
# TAB 2: EMPRESAS EN AIRTABLE
# ============================================================================

with tab2:
    st.markdown("### 🔍 Filtros")
    
    # Row 1: Search and basic filters
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        search_query = st.text_input("🔍 Buscar por nombre...", placeholder="Nombre de empresa", key="t2_search")
    
    with col2:
        sector_options_t2 = ["Todos"] + get_company_sector_options()
        sector_filter = st.selectbox("Sector", options=sector_options_t2, key="t2_sector")
    
    with col3:
        if sector_filter and sector_filter != "Todos":
            activity_source = [sector_filter]
        else:
            activity_source = get_company_sector_options()
        activity_options_t2 = ["Todas"] + get_company_activity_options(activity_source)
        activity_filter = st.selectbox("Actividad", options=activity_options_t2, key="t2_activity")

    with col4:
        fei_options = ["Todos", "Eligible", "Not_Eligible", "Pending_Review", "Unknown"]
        fei_filter = st.selectbox("FEI Status", options=fei_options, key="t2_fei")
    
    # Row 2: Additional filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        country_options_t2 = [("", "Todos")] + get_country_options()
        country_filter_idx = st.selectbox(
            "País",
            options=range(len(country_options_t2)),
            format_func=lambda i: country_options_t2[i][1],
            key="t2_country",
        )
        country_filter = country_options_t2[country_filter_idx][0] if country_filter_idx > 0 else None
    
    with col2:
        employees_filter = st.selectbox(
            "Empleados",
            options=["Todos", "1-50", "51-250", "251-1000", "1000+"],
            key="t2_employees",
        )
    
    with col3:
        revenue_filter = st.selectbox(
            "Facturación",
            options=["Todos", "< 1M €", "1-10M €", "10-50M €", "50-200M €", "> 200M €"],
            key="t2_revenue",
        )
    
    with col4:
        company_type_filter = st.selectbox(
            "Tipo Empresa",
            options=["Todos", "Promotor", "Financiador", "Operador", "Desarrollador", "Otros"],
            key="t2_company_type",
        )
    
    # Refresh and pagination controls
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔄 Refrescar", use_container_width=True, key="t2_refresh"):
            st.session_state.airtable_selected = set()
            st.session_state.tab2_enrichment = None
            st.session_state.tab2_page = 0
            st.session_state.all_airtable_companies = None  # Force refresh
            st.rerun()
    
    with col2:
        page_size = st.selectbox(
            "Por página",
            options=[10, 25, 50, 100],
            index=1,
            key="t2_page_size_select",
        )
        st.session_state.tab2_page_size = page_size
    
    st.markdown("---")
    
    # Build Airtable filter formula
    def build_filter_formula():
        """Build Airtable filter formula from UI filters."""
        conditions = []
        
        if search_query:
            conditions.append(f"SEARCH(LOWER('{search_query}'), LOWER({{Company Name}}))")
        
        if sector_filter and sector_filter != "Todos":
            conditions.append(f"FIND('{sector_filter}', ARRAYJOIN({{Sector}}, ','))")

        if activity_filter and activity_filter != "Todas":
            conditions.append(f"FIND('{activity_filter}', ARRAYJOIN({{Activities}}, ','))")
        
        if fei_filter and fei_filter != "Todos":
            conditions.append(f"{{FEI_Status}} = '{fei_filter}'")
        
        if country_filter:
            conditions.append(f"FIND('{country_filter}', ARRAYJOIN({{HQ Country}}, ','))")
        
        if employees_filter and employees_filter != "Todos":
            if employees_filter == "1-50":
                conditions.append("AND({Num Employees} >= 1, {Num Employees} <= 50)")
            elif employees_filter == "51-250":
                conditions.append("AND({Num Employees} >= 51, {Num Employees} <= 250)")
            elif employees_filter == "251-1000":
                conditions.append("AND({Num Employees} >= 251, {Num Employees} <= 1000)")
            elif employees_filter == "1000+":
                conditions.append("{Num Employees} > 1000")
        
        if revenue_filter and revenue_filter != "Todos":
            if revenue_filter == "< 1M €":
                conditions.append("{Revenues} < 1000000")
            elif revenue_filter == "1-10M €":
                conditions.append("AND({Revenues} >= 1000000, {Revenues} < 10000000)")
            elif revenue_filter == "10-50M €":
                conditions.append("AND({Revenues} >= 10000000, {Revenues} < 50000000)")
            elif revenue_filter == "50-200M €":
                conditions.append("AND({Revenues} >= 50000000, {Revenues} < 200000000)")
            elif revenue_filter == "> 200M €":
                conditions.append("{Revenues} >= 200000000")
        
        if company_type_filter and company_type_filter != "Todos":
            conditions.append(f"{{Company Type}} = '{company_type_filter}'")
        
        if conditions:
            return "AND(" + ", ".join(conditions) + ")" if len(conditions) > 1 else conditions[0]
        return None
    
    # Load companies with filters
    formula = build_filter_formula()
    
    with loading_spinner("Cargando empresas de Airtable..."):
        # Get total count first (this could be optimized with a count endpoint)
        all_filtered, _ = api.get_companies(
            formula=formula,
            limit=5000,  # Get all matching for count
        )
        total_companies = len(all_filtered) if all_filtered else 0
        
        # Calculate pagination
        total_pages = max(1, (total_companies + page_size - 1) // page_size)
        current_page = min(st.session_state.tab2_page, total_pages - 1)
        
        # Get page of companies
        start_idx = current_page * page_size
        end_idx = start_idx + page_size
        companies = all_filtered[start_idx:end_idx] if all_filtered else []
    
    if total_companies > 0:
        # Metrics
        selected_count = len(st.session_state.airtable_selected)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Filtradas", total_companies)
        with col2:
            st.metric("📄 En esta página", len(companies))
        with col3:
            st.metric("✔️ Seleccionadas", f"{selected_count}/50")
        with col4:
            if selected_count > 50:
                st.warning("⚠️ Máx 50")
        
        # Pagination controls
        st.markdown("---")
        
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        
        with col1:
            if st.button("⏮️ Primera", disabled=current_page == 0, key="t2_first"):
                st.session_state.tab2_page = 0
                st.session_state.airtable_selected = set()
                st.rerun()
        
        with col2:
            if st.button("◀️ Anterior", disabled=current_page == 0, key="t2_prev"):
                st.session_state.tab2_page = current_page - 1
                st.session_state.airtable_selected = set()
                st.rerun()
        
        with col3:
            st.markdown(f"<div style='text-align: center; padding: 8px;'>Página **{current_page + 1}** de **{total_pages}**</div>", unsafe_allow_html=True)
        
        with col4:
            if st.button("Siguiente ▶️", disabled=current_page >= total_pages - 1, key="t2_next"):
                st.session_state.tab2_page = current_page + 1
                st.session_state.airtable_selected = set()
                st.rerun()
        
        with col5:
            if st.button("Última ⏭️", disabled=current_page >= total_pages - 1, key="t2_last"):
                st.session_state.tab2_page = total_pages - 1
                st.session_state.airtable_selected = set()
                st.rerun()
        
        st.markdown("---")
        
        # ========== ACTION BUTTONS ==========
        st.markdown("### ⚡ Acciones de Enriquecimiento")
        st.info("📌 Selecciona empresas (máx 50) y ejecuta una acción. Los resultados se mostrarán abajo.")
        
        selected_indices = list(st.session_state.airtable_selected)[:50]
        selected_companies = [companies[i] for i in selected_indices if i < len(companies)]
        has_selection = len(selected_companies) > 0
        
        action_cols = st.columns(5)
        
        with action_cols[0]:
            btn_financial = st.button(
                "💰 Datos Financieros",
                use_container_width=True,
                disabled=not has_selection,
                key="t2_btn_financial",
            )
        
        with action_cols[1]:
            btn_structure = st.button(
                "🏗️ Estructura",
                use_container_width=True,
                disabled=not has_selection,
                key="t2_btn_structure",
            )
        
        with action_cols[2]:
            btn_fei = st.button(
                "🏷️ Evaluación FEI",
                use_container_width=True,
                disabled=not has_selection,
                key="t2_btn_fei",
            )
        
        with action_cols[3]:
            btn_bus = st.button(
                "🏢 Business Units",
                use_container_width=True,
                disabled=not has_selection,
                key="t2_btn_bus",
            )
        
        with action_cols[4]:
            btn_contacts = st.button(
                "👥 Buscar Contactos",
                use_container_width=True,
                disabled=not has_selection,
                key="t2_btn_contacts",
            )
        
        # ========== PROCESS ENRICHMENT ACTIONS ==========
        
        if btn_financial and has_selection:
            st.markdown("---")
            st.markdown("### 💰 Enriqueciendo Datos Financieros...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = []
            for idx, company in enumerate(selected_companies):
                fields = company.get("fields", {})
                company_name = fields.get("Company Name", "N/A")
                company_id = company.get("id")
                company_url = fields.get("Home URL", "")
                
                status_text.text(f"Procesando {idx+1}/{len(selected_companies)}: {company_name}")
                progress_bar.progress((idx + 1) / len(selected_companies))
                
                result_entry = {
                    "company_name": company_name,
                    "company_id": company_id,
                    "success": False,
                    "employees": None,
                    "revenues": None,
                    "ebitda": None,
                    "linkedin": None,
                    "error": None,
                }
                
                try:
                    # Call the Enriquecedor agent
                    enrich_result = api.enrich_company(
                        company_id, 
                        company_name=company_name,
                        company_url=company_url,
                        include_financials=True, 
                        include_contacts=False
                    )
                    
                    if hasattr(enrich_result, "success") and enrich_result.success:
                        result_entry["success"] = True
                        if hasattr(enrich_result, "company_info") and enrich_result.company_info:
                            result_entry["employees"] = enrich_result.company_info.num_employees
                            result_entry["linkedin"] = enrich_result.company_info.linkedin_url
                        if hasattr(enrich_result, "financial_info") and enrich_result.financial_info:
                            result_entry["revenues"] = enrich_result.financial_info.annual_revenues
                            result_entry["ebitda"] = enrich_result.financial_info.ebitda
                    elif isinstance(enrich_result, dict):
                        result_entry["success"] = enrich_result.get("success", False)
                        if result_entry["success"]:
                            result_entry["employees"] = enrich_result.get("num_employees")
                            result_entry["revenues"] = enrich_result.get("revenues")
                            result_entry["ebitda"] = enrich_result.get("ebitda")
                            result_entry["linkedin"] = enrich_result.get("linkedin_url")
                        result_entry["error"] = str(enrich_result.get("errors", [])) if not result_entry["success"] else None
                    else:
                        result_entry["error"] = "Resultado no reconocido"
                        
                except Exception as e:
                    result_entry["error"] = str(e)
                
                results.append(result_entry)
            
            progress_bar.empty()
            status_text.empty()
            
            st.session_state.tab2_enrichment = {"type": "financial", "data": results}
        
        if btn_fei and has_selection:
            st.markdown("---")
            st.markdown("### 🏷️ Evaluando Elegibilidad FEI...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = []
            for idx, company in enumerate(selected_companies):
                fields = company.get("fields", {})
                company_name = fields.get("Company Name", "N/A")
                company_id = company.get("id")
                
                status_text.text(f"Evaluando {idx+1}/{len(selected_companies)}: {company_name}")
                progress_bar.progress((idx + 1) / len(selected_companies))
                
                result_entry = {
                    "company_name": company_name,
                    "company_id": company_id,
                    "status": "Unknown",
                    "confidence": 0,
                    "criteria_met": [],
                    "reasoning": "",
                    "error": None,
                }
                
                try:
                    # Call the real EvaluadorFEI agent
                    fei_result = api.evaluate_fei(company_id, force=True)
                    
                    if hasattr(fei_result, "status"):
                        status_val = fei_result.status.value if hasattr(fei_result.status, "value") else str(fei_result.status)
                        result_entry["status"] = status_val
                        result_entry["confidence"] = getattr(fei_result, "confidence", 0)
                        
                        criteria = getattr(fei_result, "criteria_met", [])
                        if criteria:
                            result_entry["criteria_met"] = [c.value if hasattr(c, "value") else str(c) for c in criteria]
                        
                        result_entry["reasoning"] = getattr(fei_result, "reasoning", "")
                    elif isinstance(fei_result, dict):
                        result_entry["status"] = fei_result.get("status", "Unknown")
                        result_entry["confidence"] = fei_result.get("confidence", 0)
                        result_entry["criteria_met"] = fei_result.get("criteria_met", [])
                        result_entry["reasoning"] = fei_result.get("reasoning", "")
                        result_entry["error"] = str(fei_result.get("errors", [])) if fei_result.get("errors") else None
                    else:
                        result_entry["error"] = "Resultado no reconocido"
                        
                except Exception as e:
                    result_entry["error"] = str(e)
                
                results.append(result_entry)
            
            progress_bar.empty()
            status_text.empty()
            
            st.session_state.tab2_enrichment = {"type": "fei", "data": results}
        
        if btn_contacts and has_selection:
            st.markdown("---")
            st.markdown("### 👥 Buscando Contactos...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = []
            for idx, company in enumerate(selected_companies):
                fields = company.get("fields", {})
                company_name = fields.get("Company Name", "N/A")
                company_id = company.get("id")
                company_url = fields.get("Home URL", "")
                
                status_text.text(f"Buscando {idx+1}/{len(selected_companies)}: {company_name}")
                progress_bar.progress((idx + 1) / len(selected_companies))
                
                result_entry = {
                    "company_name": company_name,
                    "company_id": company_id,
                    "contacts": [],
                    "contacts_created": 0,
                    "error": None,
                }
                
                try:
                    # Call the real contact search via Enriquecedor
                    contacts_result = api.enrich_company(
                        company_id,
                        company_name=company_name,
                        company_url=company_url,
                        include_financials=False,
                        include_contacts=True
                    )
                    
                    if hasattr(contacts_result, "key_persons") and contacts_result.key_persons:
                        result_entry["contacts"] = [
                            {
                                "name": p.get("name", ""),
                                "role": p.get("role", ""),
                                "email": p.get("email", ""),
                                "linkedin": p.get("linkedin_url", ""),
                            }
                            for p in contacts_result.key_persons
                        ]
                        result_entry["contacts_created"] = len(contacts_result.key_persons)
                    elif isinstance(contacts_result, dict):
                        persons = contacts_result.get("key_persons", [])
                        result_entry["contacts"] = persons
                        result_entry["contacts_created"] = contacts_result.get("contacts_created", len(persons))
                        if not contacts_result.get("success"):
                            result_entry["error"] = str(contacts_result.get("errors", []))
                    else:
                        result_entry["error"] = "Resultado no reconocido"
                        
                except Exception as e:
                    result_entry["error"] = str(e)
                
                results.append(result_entry)
            
            progress_bar.empty()
            status_text.empty()
            
            st.session_state.tab2_enrichment = {"type": "contacts", "data": results}
        
        if btn_structure and has_selection:
            st.markdown("---")
            st.markdown("### 🏗️ Analizando Estructura Corporativa...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = []
            for idx, company in enumerate(selected_companies):
                fields = company.get("fields", {})
                company_name = fields.get("Company Name", "N/A")
                company_id = company.get("id")
                company_url = fields.get("Home URL", "")
                
                status_text.text(f"Analizando {idx+1}/{len(selected_companies)}: {company_name}")
                progress_bar.progress((idx + 1) / len(selected_companies))
                
                result_entry = {
                    "company_name": company_name,
                    "company_id": company_id,
                    "parent_company": None,
                    "subsidiaries": [],
                    "success": False,
                    "error": None,
                }
                
                try:
                    structure_result = api.enrich_structure(company_id)
                    if isinstance(structure_result, dict):
                        result_entry["parent_company"] = structure_result.get("parent_company")
                        result_entry["ultimate_parent"] = structure_result.get("ultimate_parent")
                        result_entry["subsidiaries"] = structure_result.get("subsidiaries", [])
                        result_entry["success"] = structure_result.get("success", False)
                    
                except Exception as e:
                    result_entry["error"] = str(e)
                
                results.append(result_entry)
            
            progress_bar.empty()
            status_text.empty()
            
            st.session_state.tab2_enrichment = {"type": "structure", "data": results}
        
        if btn_bus and has_selection:
            st.markdown("---")
            st.markdown("### 🏢 Creando/Actualizando Business Units...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = []
            for idx, company in enumerate(selected_companies):
                fields = company.get("fields", {})
                company_name = fields.get("Company Name", "N/A")
                company_id = company.get("id")
                
                status_text.text(f"Procesando {idx+1}/{len(selected_companies)}: {company_name}")
                progress_bar.progress((idx + 1) / len(selected_companies))
                
                result_entry = {
                    "company_name": company_name,
                    "company_id": company_id,
                    "bus_created": 0,
                    "bus_updated": 0,
                    "bus_list": [],
                    "success": False,
                    "error": None,
                }
                
                try:
                    # Get or create business units for company
                    bu_result = api.get_or_create_business_units(company_id, company_name)
                    
                    if isinstance(bu_result, dict):
                        result_entry["bus_created"] = bu_result.get("created", 0)
                        result_entry["bus_updated"] = bu_result.get("updated", 0)
                        result_entry["bus_list"] = bu_result.get("business_units", [])
                        result_entry["success"] = bu_result.get("success", False)
                        if not result_entry["success"]:
                            result_entry["error"] = str(bu_result.get("errors", []))
                    else:
                        result_entry["success"] = True
                        result_entry["bus_created"] = 1
                        
                except Exception as e:
                    result_entry["error"] = str(e)
                
                results.append(result_entry)
            
            progress_bar.empty()
            status_text.empty()
            
            st.session_state.tab2_enrichment = {"type": "business_units", "data": results}
        
        # ========== DISPLAY ENRICHMENT RESULTS ==========
        
        if st.session_state.tab2_enrichment:
            enrichment = st.session_state.tab2_enrichment
            enrichment_type = enrichment.get("type")
            enrichment_data = enrichment.get("data", [])
            
            st.markdown("---")
            
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown("### 📊 Resultados del Enriquecimiento")
            with col2:
                if st.button("❌ Cerrar", key="t2_close_enrichment"):
                    st.session_state.tab2_enrichment = None
                    st.rerun()
            
            if enrichment_type == "financial":
                successful = [r for r in enrichment_data if r.get("success")]
                failed = [r for r in enrichment_data if not r.get("success")]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("✅ Éxito", len(successful))
                with col2:
                    st.metric("❌ Errores", len(failed))
                
                if successful:
                    st.markdown("#### Datos Encontrados:")
                    df_data = []
                    for r in successful:
                        df_data.append({
                            "Empresa": r["company_name"],
                            "Empleados": r.get("employees") or "N/A",
                            "Facturación": format_currency(r.get("revenues")) if r.get("revenues") else "N/A",
                            "EBITDA": format_currency(r.get("ebitda")) if r.get("ebitda") else "N/A",
                            "LinkedIn": "✓" if r.get("linkedin") else "✗",
                        })
                    st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)
                
                if failed:
                    with st.expander(f"❌ Ver {len(failed)} errores"):
                        for r in failed:
                            st.error(f"**{r['company_name']}**: {r.get('error', 'Error desconocido')}")
                
                st.success("✅ Los datos se han guardado automáticamente en Airtable.")
            
            elif enrichment_type == "fei":
                eligible = [r for r in enrichment_data if r.get("status") == "Eligible"]
                not_eligible = [r for r in enrichment_data if r.get("status") == "Not_Eligible"]
                pending = [r for r in enrichment_data if r.get("status") not in ["Eligible", "Not_Eligible"]]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("✅ Elegibles", len(eligible))
                with col2:
                    st.metric("❌ No Elegibles", len(not_eligible))
                with col3:
                    st.metric("⏳ Pendientes/Otros", len(pending))
                
                st.markdown("#### Resultados Detallados:")
                df_data = []
                for r in enrichment_data:
                    emoji = get_fei_status_emoji(r.get("status", "Unknown"))
                    df_data.append({
                        "Empresa": r["company_name"],
                        "Estado": f"{emoji} {r.get('status', 'Unknown')}",
                        "Confianza": f"{r.get('confidence', 0)*100:.0f}%" if r.get("confidence") else "N/A",
                        "Criterios": ", ".join(r.get("criteria_met", [])) or "Ninguno",
                    })
                st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)
                
                if eligible:
                    with st.expander("📝 Ver razonamiento de empresas elegibles"):
                        for r in eligible:
                            st.markdown(f"**{r['company_name']}:**")
                            st.markdown(f"> {r.get('reasoning', 'Sin razonamiento disponible')}")
                            st.markdown("---")
                
                st.success("✅ Las evaluaciones FEI se han guardado automáticamente en Airtable.")
            
            elif enrichment_type == "contacts":
                total_contacts = sum(len(r.get("contacts", [])) for r in enrichment_data)
                total_created = sum(r.get("contacts_created", 0) for r in enrichment_data)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("👥 Contactos Encontrados", total_contacts)
                with col2:
                    st.metric("💾 Creados en Airtable", total_created)
                
                if total_contacts > 0:
                    st.markdown("#### Contactos por Empresa:")
                    
                    for r in enrichment_data:
                        contacts = r.get("contacts", [])
                        if contacts:
                            st.markdown(f"**{r['company_name']}** ({len(contacts)} contactos)")
                            
                            contact_data = []
                            for c in contacts:
                                contact_data.append({
                                    "Nombre": c.get("name", "N/A"),
                                    "Cargo": c.get("role", "N/A"),
                                    "Email": c.get("email", "N/A"),
                                    "LinkedIn": "✓" if c.get("linkedin") else "✗",
                                })
                            st.dataframe(pd.DataFrame(contact_data), use_container_width=True, hide_index=True)
                        elif r.get("error"):
                            st.warning(f"**{r['company_name']}**: {r['error']}")
                
                st.success("✅ Los contactos encontrados se han guardado automáticamente en Airtable.")
            
            elif enrichment_type == "structure":
                successful = [r for r in enrichment_data if r.get("success")]
                
                st.markdown("#### Estructura Corporativa:")
                for r in enrichment_data:
                    with st.expander(f"**{r['company_name']}**"):
                        if r.get("parent_company"):
                            st.markdown(f"🏛️ **Empresa Matriz:** {r['parent_company']}")
                        else:
                            st.markdown("🏛️ **Empresa Matriz:** No identificada")

                        if r.get("ultimate_parent"):
                            st.markdown(f"🏢 **Holding/Grupo:** {r['ultimate_parent']}")
                        
                        subs = r.get("subsidiaries", [])
                        if subs:
                            st.markdown(f"🏢 **Subsidiarias:** {len(subs)}")
                            for sub in subs[:10]:  # Limit display
                                st.markdown(f"  - {sub}")
                        else:
                            st.markdown("🏢 **Subsidiarias:** No identificadas")
                        
                        if r.get("error"):
                            st.error(f"Error: {r['error']}")
            
            elif enrichment_type == "business_units":
                total_created = sum(r.get("bus_created", 0) for r in enrichment_data)
                total_updated = sum(r.get("bus_updated", 0) for r in enrichment_data)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("🆕 BUs Creadas", total_created)
                with col2:
                    st.metric("🔄 BUs Actualizadas", total_updated)
                
                for r in enrichment_data:
                    bus = r.get("bus_list", [])
                    if bus:
                        with st.expander(f"**{r['company_name']}** ({len(bus)} Business Units)"):
                            for bu in bus:
                                bu_name = bu.get("name", bu.get("BU Name", "N/A"))
                                bu_type = bu.get("type", bu.get("BU Type", "N/A"))
                                st.markdown(f"  - **{bu_name}** ({bu_type})")
                    elif r.get("error"):
                        st.error(f"**{r['company_name']}**: {r['error']}")
                
                st.success("✅ Las Business Units se han guardado automáticamente en Airtable.")
        
        st.markdown("---")
        
        # ========== COMPANY LIST ==========
        st.markdown("### 📋 Empresas en Base de Datos")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("✅ Seleccionar Todas (máx 50)", key="t2_sel_all", use_container_width=True):
                max_select = min(50, len(companies))
                st.session_state.airtable_selected = set(range(max_select))
                # Sync checkboxes with selection
                for i in range(len(companies)):
                    st.session_state[f"chk_airtable_selected_{i}"] = i < max_select
                st.rerun()
        with col2:
            if st.button("❌ Deseleccionar Todas", key="t2_desel", use_container_width=True):
                # Clear selection set and checkboxes
                for i in range(len(companies)):
                    checkbox_key = f"chk_airtable_selected_{i}"
                    if checkbox_key in st.session_state:
                        st.session_state[checkbox_key] = False
                st.session_state.airtable_selected = set()
                st.rerun()
        
        # Display companies
        for idx, company in enumerate(companies):
            display_company_card(
                company=company,
                idx=idx,
                state_key="airtable_selected",
                show_airtable_link=True,
            )
        
        st.markdown("---")
        
        # Export
        export_companies = selected_companies if has_selection else companies
        csv = generate_csv_companies(export_companies)
        st.download_button(
            f"📥 Descargar CSV ({len(export_companies)} empresas)",
            data=csv,
            file_name=f"airtable_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            key="t2_csv_download",
        )
    
    else:
        empty_state(
            icon="🏢",
            title="No hay empresas",
            message="No se encontraron empresas con los filtros aplicados. Ajusta los filtros o usa 'Añadir Nuevas Empresas' para buscar.",
        )


# ============================================================================
# HELP
# ============================================================================

st.markdown("---")
with st.expander("❓ Ayuda"):
    st.markdown("""
    ## Cómo usar
    
    ### Tab 1: Añadir Nuevas Empresas
    1. Selecciona hasta **3 sectores** y **3 países** para la búsqueda
    2. Opcionalmente añade región y palabras clave
    3. Configura el número máximo de empresas (hasta 100)
    4. Haz clic en "Buscar Empresas"
    5. **Revisa los resultados:**
       - 🆕 = Empresa nueva (no está en Airtable)
       - ⚠️ = Posible duplicado (nombre similar en Airtable)
       - ✅ = Ya está guardada en Airtable
    6. Selecciona las que te interesan y guárdalas
    
    ### Tab 2: Empresas en Airtable
    1. Usa los **filtros** para encontrar empresas:
       - Búsqueda por nombre
       - Sector, País, FEI Status
       - Rango de empleados y facturación
       - Tipo de empresa
    2. Navega con la **paginación** (mostrando todas las empresas)
    3. Selecciona empresas (máx 50) y ejecuta acciones:
       - **💰 Datos Financieros**: Empleados, facturación, EBITDA
       - **🏗️ Estructura**: Empresa matriz y subsidiarias
       - **🏷️ Evaluación FEI**: Elegibilidad para acuerdo FEI
       - **🏢 Business Units**: Crear/actualizar unidades de negocio
       - **👥 Buscar Contactos**: CEO, CFO, ejecutivos
    4. Los resultados se guardan automáticamente en Airtable
    
    ### Información mostrada por empresa
    - **Nombre** de la empresa
    - **URL** del sitio web
    - **LinkedIn URL**
    - **URL Airtable** (si está guardada)
    - **Número de empleados**
    - **Facturación** último año conocido
    - **EBITDA** último año conocido
    - **Validación FEI** (Eligible, Not_Eligible, Unknown)
    
    ### Tiempos Estimados
    - Datos Financieros: ~15-30 seg/empresa
    - Evaluación FEI: ~30-60 seg/empresa
    - Contactos: ~20-40 seg/empresa
    - Estructura: ~15-30 seg/empresa
    - Business Units: ~5-15 seg/empresa
    """)
