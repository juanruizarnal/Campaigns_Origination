"""Origination Pipeline page for Alter-5 Origination Engine.

End-to-end origination: Search -> (Manual Selection) -> Enrich -> FEI -> Contacts.
Companies are NOT saved automatically - user must select and save manually.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.styles import inject_custom_css
from utils.api import get_api
from utils.helpers import get_fei_status_emoji, get_sector_options, get_country_options
from components.feedback import (
    loading_spinner, 
    success_alert, 
    error_alert, 
    warning_alert,
    progress_with_status,
)

# Page config
st.set_page_config(
    page_title="Pipeline de Originación - Alter-5",
    page_icon="🔄",
    layout="wide",
)

inject_custom_css()

st.title("🔄 Pipeline de Originación")
st.caption("Buscar empresas → Seleccionar → Guardar → Enriquecer → Evaluar FEI → Buscar Contactos")

st.markdown("---")

api = get_api()

# ============================================================================
# SESSION STATE
# ============================================================================

if "orig_search_results" not in st.session_state:
    st.session_state.orig_search_results = None
if "orig_selected" not in st.session_state:
    st.session_state.orig_selected = set()
if "orig_saved_ids" not in st.session_state:
    st.session_state.orig_saved_ids = []
if "orig_enriched" not in st.session_state:
    st.session_state.orig_enriched = {}

# ============================================================================
# STEP 1: SEARCH CONFIGURATION
# ============================================================================

st.markdown("### 🔍 Paso 1: Configurar Búsqueda")

col1, col2 = st.columns(2)

with col1:
    sector_options = get_sector_options()
    sector = st.selectbox(
        "Sector *",
        options=[""] + sector_options,
        key="orig_sector",
        help="Sector de actividad de las empresas a buscar",
    )
    
    country_options = get_country_options()
    country_codes = [c[0] for c in country_options]
    country_labels = [c[1] for c in country_options]
    
    country_idx = st.selectbox(
        "País *",
        options=range(len(country_options) + 1),
        format_func=lambda i: "Seleccionar..." if i == 0 else country_labels[i-1],
        key="orig_country",
        help="País donde buscar empresas",
    )
    country = country_codes[country_idx - 1] if country_idx > 0 else None

with col2:
    region = st.text_input(
        "Región (opcional)",
        placeholder="Ej: Cataluña, Dublin, Bayern",
        key="orig_region",
        help="Región o ciudad específica",
    )
    
    limit = st.slider(
        "Máximo de empresas a buscar",
        min_value=3,
        max_value=25,
        value=10,
        key="orig_limit",
        help="Número máximo de empresas a buscar (recomendado: 10-15)",
    )

keywords_str = st.text_input(
    "Palabras clave adicionales (opcional)",
    placeholder="Ej: solar, eólica, baterías",
    key="orig_keywords",
    help="Palabras clave separadas por comas para refinar la búsqueda",
)
keywords = [k.strip() for k in keywords_str.split(",") if k.strip()] if keywords_str else None

# Search button
st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    search_button = st.button(
        "🔍 BUSCAR EMPRESAS",
        type="primary",
        use_container_width=True,
        disabled=not (sector and country),
    )

# ============================================================================
# EXECUTE SEARCH
# ============================================================================

if search_button:
    if not sector or not country:
        warning_alert("Sector y País son obligatorios")
    else:
        with st.spinner(f"🔍 Buscando empresas de {sector} en {country}... (puede tardar 20-40 segundos)"):
            result = api.search_companies(
                sector=sector,
                country=country,
                region=region if region else None,
                keywords=keywords,
                limit=limit,
                save_to_airtable=False,  # NEVER save automatically
            )
        
        st.session_state.orig_search_results = result
        st.session_state.orig_selected = set()
        st.session_state.orig_saved_ids = []
        st.session_state.orig_enriched = {}
        
        if result.get("success"):
            st.success(f"✅ Encontradas {len(result.get('candidates_found', []))} empresas en {result.get('processing_time', 0):.1f}s")
        else:
            error_alert(f"Error: {', '.join(result.get('errors', ['Error desconocido']))}")

# ============================================================================
# DISPLAY SEARCH RESULTS
# ============================================================================

if st.session_state.orig_search_results and st.session_state.orig_search_results.get("success"):
    result = st.session_state.orig_search_results
    candidates = result.get("candidates_found", [])
    
    # Filter new candidates (not duplicates)
    new_candidates = [c for c in candidates if not c.get("is_duplicate")]
    dup_candidates = [c for c in candidates if c.get("is_duplicate")]
    
    st.markdown("---")
    st.markdown("### 📋 Paso 2: Seleccionar Empresas")
    
    # Summary
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Encontradas", len(candidates))
    with col2:
        st.metric("✅ Nuevas", len(new_candidates))
    with col3:
        st.metric("⚠️ Ya existentes", len(dup_candidates))
    with col4:
        st.metric("✔️ Seleccionadas", len(st.session_state.orig_selected))
    
    if new_candidates:
        st.warning("⚠️ **Las empresas NO están guardadas.** Selecciona las que quieras y haz clic en 'Guardar Seleccionadas'.")
        
        # Selection buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("✅ Seleccionar Todas", key="orig_sel_all"):
                st.session_state.orig_selected = set(range(len(new_candidates)))
                st.rerun()
        with col2:
            if st.button("❌ Deseleccionar", key="orig_desel"):
                st.session_state.orig_selected = set()
                st.rerun()
        
        st.markdown("---")
        
        # Companies table with checkboxes
        for i, candidate in enumerate(new_candidates):
            name = candidate.get("name", "Sin nombre")
            url = candidate.get("home_url", "")
            country_code = candidate.get("country", "N/A")
            sector_text = candidate.get("sector", "N/A")[:40]
            employees = candidate.get("estimated_employees") or "?"
            verified = "✓" if candidate.get("url_verified") else "✗"
            
            col1, col2 = st.columns([1, 15])
            
            with col1:
                is_selected = st.checkbox(
                    "Sel",
                    value=i in st.session_state.orig_selected,
                    key=f"orig_sel_{i}",
                    label_visibility="collapsed",
                )
                if is_selected and i not in st.session_state.orig_selected:
                    st.session_state.orig_selected.add(i)
                elif not is_selected and i in st.session_state.orig_selected:
                    st.session_state.orig_selected.discard(i)
            
            with col2:
                with st.expander(f"🟢 **{name}** | {country_code} | {sector_text} | 👥 {employees} | URL: {verified}"):
                    col_a, col_b = st.columns([3, 1])
                    
                    with col_a:
                        if url:
                            st.markdown(f"**🌐 Website:** [{url}]({url})")
                        st.markdown(f"**📍 País:** {country_code}")
                        st.markdown(f"**🏭 Sector:** {candidate.get('sector', 'N/A')}")
                        if candidate.get("region"):
                            st.markdown(f"**📍 Región:** {candidate.get('region')}")
                        st.markdown(f"**👥 Empleados (est.):** {employees}")
                        
                        desc = candidate.get("description", "")
                        if desc:
                            st.info(f"**📝 Descripción:** {desc}")
                    
                    with col_b:
                        if candidate.get("url_verified"):
                            st.success("✅ URL verificada")
                        else:
                            st.warning("⚠️ URL no verificada")
        
        # Show duplicates (collapsed)
        if dup_candidates:
            st.markdown("---")
            with st.expander(f"⚠️ {len(dup_candidates)} empresas ya existentes en Airtable"):
                for dup in dup_candidates:
                    st.markdown(f"- **{dup.get('name', 'N/A')}** - Ya existe (ID: {dup.get('duplicate_of', 'N/A')})")
        
        # ============================================================================
        # STEP 3: SAVE SELECTED COMPANIES
        # ============================================================================
        
        st.markdown("---")
        st.markdown("### 💾 Paso 3: Guardar en Airtable")
        
        selected_count = len(st.session_state.orig_selected)
        selected_candidates = [new_candidates[i] for i in st.session_state.orig_selected if i < len(new_candidates)]
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(
                f"💾 GUARDAR {selected_count} EMPRESAS EN AIRTABLE",
                type="primary",
                use_container_width=True,
                disabled=selected_count == 0,
                key="orig_save",
            ):
                with st.spinner(f"Guardando {selected_count} empresas..."):
                    save_result = api.save_companies(selected_candidates)
                
                if save_result.get("success"):
                    saved_ids = save_result.get("companies_created", [])
                    st.session_state.orig_saved_ids = saved_ids
                    success_alert(f"✅ ¡{len(saved_ids)} empresas guardadas!")
                else:
                    error_alert(f"Error: {', '.join(save_result.get('errors', ['Error desconocido']))}")
        
        # ============================================================================
        # STEP 4: ENRICHMENT OPTIONS (after save)
        # ============================================================================
        
        if st.session_state.orig_saved_ids:
            st.markdown("---")
            st.markdown("### 📊 Paso 4: Enriquecer Datos")
            
            saved_ids = st.session_state.orig_saved_ids
            
            st.info(f"""
            **{len(saved_ids)} empresas guardadas.** Ahora puedes:
            - **Enriquecer Datos**: Obtener empleados, facturación, EBITDA y descripción detallada
            - **Evaluar FEI**: Verificar elegibilidad para garantía FEI del Fondo Europeo de Inversiones
            - **Buscar Contactos**: Identificar CEO, CFO y otros ejecutivos clave
            """)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 Enriquecer Datos", use_container_width=True, key="orig_enrich"):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    enriched = 0
                    for idx, cid in enumerate(saved_ids):
                        status_text.text(f"Enriqueciendo empresa {idx+1}/{len(saved_ids)}...")
                        progress_bar.progress((idx + 1) / len(saved_ids))
                        
                        try:
                            r = api.enrich_company(cid, include_contacts=False)
                            if (hasattr(r, "success") and r.success) or (isinstance(r, dict) and r.get("success")):
                                enriched += 1
                                st.session_state.orig_enriched[cid] = "enriched"
                        except Exception as e:
                            st.session_state.orig_enriched[cid] = f"error: {e}"
                    
                    progress_bar.progress(1.0)
                    status_text.success(f"✅ {enriched}/{len(saved_ids)} empresas enriquecidas")
            
            with col2:
                if st.button("🏷️ Evaluar FEI", use_container_width=True, key="orig_fei"):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    eligible = 0
                    for idx, cid in enumerate(saved_ids):
                        status_text.text(f"Evaluando FEI {idx+1}/{len(saved_ids)}...")
                        progress_bar.progress((idx + 1) / len(saved_ids))
                        
                        try:
                            r = api.evaluate_fei(cid)
                            if hasattr(r, "status"):
                                status = r.status.value if hasattr(r.status, "value") else str(r.status)
                                if status == "Eligible":
                                    eligible += 1
                        except:
                            pass
                    
                    progress_bar.progress(1.0)
                    status_text.success(f"✅ Evaluación completada. {eligible} elegibles para FEI")
            
            with col3:
                if st.button("👥 Buscar Contactos", use_container_width=True, key="orig_contacts"):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    contacts_found = 0
                    for idx, cid in enumerate(saved_ids):
                        status_text.text(f"Buscando contactos {idx+1}/{len(saved_ids)}...")
                        progress_bar.progress((idx + 1) / len(saved_ids))
                        
                        try:
                            r = api.search_contacts(cid)
                            if isinstance(r, dict):
                                contacts_found += len(r.get("contacts_created", []))
                            elif hasattr(r, "contacts_created"):
                                contacts_found += r.contacts_created
                        except:
                            pass
                    
                    progress_bar.progress(1.0)
                    status_text.success(f"✅ {contacts_found} contactos encontrados y guardados")
            
            # Navigation
            st.markdown("---")
            st.markdown("### 🚀 Siguientes Pasos")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📧 Crear Campaña", use_container_width=True, type="primary"):
                    st.switch_page("pages/3_🚀_Nueva_Campaña.py")
            with col2:
                if st.button("🏢 Ver Empresas", use_container_width=True):
                    st.switch_page("pages/2_🏢_Empresas.py")
            with col3:
                if st.button("🔄 Nueva Búsqueda", use_container_width=True):
                    st.session_state.orig_search_results = None
                    st.session_state.orig_selected = set()
                    st.session_state.orig_saved_ids = []
                    st.session_state.orig_enriched = {}
                    st.rerun()
    
    elif dup_candidates:
        st.info(f"Todas las {len(dup_candidates)} empresas encontradas ya existen en Airtable.")
        if st.button("🔄 Nueva Búsqueda"):
            st.session_state.orig_search_results = None
            st.rerun()
    
    else:
        st.info("No se encontraron empresas con los criterios especificados. Intenta con otros parámetros.")

# ============================================================================
# HELP SECTION
# ============================================================================

st.markdown("---")

with st.expander("❓ ¿Cómo funciona el Pipeline de Originación?"):
    st.markdown("""
    ### Flujo de trabajo
    
    1. **🔍 Buscar**: El agente Buscador utiliza Gemini para encontrar empresas reales en internet
    2. **📋 Seleccionar**: Revisa los resultados y selecciona las empresas que te interesan
    3. **💾 Guardar**: Guarda las seleccionadas en Airtable (solo nombre, URL y sector básico)
    4. **📊 Enriquecer**: El agente Enriquecedor busca datos fiables de empleados, facturación y EBITDA
    5. **🏷️ Evaluar FEI**: El agente Evaluador determina si la empresa es elegible para garantía FEI
    6. **👥 Buscar Contactos**: El agente busca CEO, CFO y otros ejecutivos clave
    
    ### Recomendaciones
    
    - Busca entre **10-15 empresas** por búsqueda para mejores resultados
    - El **enriquecimiento** puede tardar 20-30 segundos por empresa
    - La **evaluación FEI** requiere búsqueda web y puede tardar 30-60 segundos por empresa
    - **Buscar Contactos** es lo más lento (puede tardar 1-2 minutos por empresa)
    
    ### Datos que se obtienen
    
    | Paso | Datos |
    |------|-------|
    | Búsqueda | Nombre, URL, Sector, País, Descripción básica |
    | Enriquecimiento | Empleados, Facturación, EBITDA, LinkedIn, Descripción detallada |
    | FEI | Status (Eligible/Not_Eligible), Criterios cumplidos, Confianza |
    | Contactos | Nombre, Cargo, Email, Teléfono, LinkedIn del contacto |
    """)
