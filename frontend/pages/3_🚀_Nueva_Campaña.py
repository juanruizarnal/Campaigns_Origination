"""Campaign creation wizard for Alter-5 Origination Engine.

Supports 3 creation modes:
1. Trigger mode: From market trigger analysis
2. Companies mode: From a list of companies  
3. News mode: From automatic news search
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.styles import inject_custom_css
from utils.api import get_api
from utils.session import get_wizard_state, reset_wizard, update_wizard
from utils.helpers import format_percentage, get_fei_status_emoji, get_sector_options, get_country_options
from components.feedback import step_indicator, loading_spinner, success_alert, error_alert, warning_alert

# Page config
st.set_page_config(
    page_title="Nueva Campana - Alter-5",
    page_icon="🚀",
    layout="wide",
)

inject_custom_css()

# Initialize wizard state
wizard = get_wizard_state()

# Navigation helpers
def go_to_step(step: int):
    wizard.step = step
    st.rerun()

def go_back():
    if wizard.step > 1:
        wizard.step -= 1
        st.rerun()

# Header
st.title("🚀 Nueva Campana")

st.markdown("---")

api = get_api()

# ============================================================================
# MODE SELECTION
# ============================================================================

if wizard.step == 0 or (wizard.step == 1 and not wizard.trigger):
    st.markdown("### Selecciona como quieres crear la campana")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="
            background: white;
            padding: 24px;
            border-radius: 12px;
            border: 2px solid #E5E7EB;
            text-align: center;
            height: 200px;
        ">
            <span style="font-size: 3rem;">📰</span>
            <h3 style="margin: 16px 0 8px 0;">Trigger Manual</h3>
            <p style="color: #6B7280; font-size: 0.875rem;">
                Introduce un evento de mercado manualmente
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Seleccionar", key="mode_trigger", use_container_width=True, type="primary"):
            wizard.mode = "trigger"
            wizard.step = 1
            st.rerun()
    
    with col2:
        st.markdown("""
        <div style="
            background: white;
            padding: 24px;
            border-radius: 12px;
            border: 2px solid #E5E7EB;
            text-align: center;
            height: 200px;
        ">
            <span style="font-size: 3rem;">🏢</span>
            <h3 style="margin: 16px 0 8px 0;">Lista de Empresas</h3>
            <p style="color: #6B7280; font-size: 0.875rem;">
                Selecciona empresas existentes para la campana
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Seleccionar", key="mode_companies", use_container_width=True):
            wizard.mode = "companies"
            wizard.step = 1
            st.rerun()
    
    with col3:
        st.markdown("""
        <div style="
            background: white;
            padding: 24px;
            border-radius: 12px;
            border: 2px solid #E5E7EB;
            text-align: center;
            height: 200px;
        ">
            <span style="font-size: 3rem;">🔍</span>
            <h3 style="margin: 16px 0 8px 0;">Busqueda Automatica</h3>
            <p style="color: #6B7280; font-size: 0.875rem;">
                Busca triggers de mercado automaticamente
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Seleccionar", key="mode_news", use_container_width=True):
            wizard.mode = "news"
            wizard.step = 1
            st.rerun()
    
    st.stop()

# ============================================================================
# TRIGGER MODE
# ============================================================================

if wizard.mode == "trigger" or wizard.mode is None:
    # Step indicator
    step_indicator(
        current_step=wizard.step,
        total_steps=4,
        labels=["Trigger", "Configuracion", "Revision", "Completado"],
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # STEP 1: TRIGGER INPUT
    if wizard.step == 1:
        st.markdown("### 🎯 Que esta pasando en el mercado?")
        st.caption("Describe el evento o noticia que genera la oportunidad de originacion")
        
        # Examples
        with st.expander("💡 Ver ejemplos de triggers"):
            st.markdown("""
            **Ejemplos de triggers efectivos:**
            
            - *"El BCE ha anunciado una bajada de tipos del 0.25%, facilitando el acceso a financiacion para PYMEs industriales."*
            
            - *"Nueva normativa europea obliga a reducir emisiones en transporte un 55% para 2030."*
            
            - *"Espana aprueba subvenciones de 2.000M€ para renovables en sector agricola."*
            """)
        
        trigger = st.text_area(
            "Trigger de mercado",
            placeholder="Ej: El BCE ha bajado los tipos de interes 0.25%...",
            height=120,
            value=wizard.trigger,
            key="trigger_input",
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("← Cambiar modo", use_container_width=True):
                reset_wizard()
                st.rerun()
        
        with col3:
            if st.button("ANALIZAR TRIGGER →", type="primary", use_container_width=True):
                if trigger:
                    wizard.trigger = trigger
                    
                    with loading_spinner("Analizando trigger con IA..."):
                        result = api.analyze_trigger(trigger)
                    
                    if result.get("success"):
                        wizard.analysis = result
                        
                        # Extract suggested sectors/countries
                        if result.get("impact"):
                            impact = result["impact"]
                            if hasattr(impact, "affected_sectors"):
                                wizard.sectors = impact.affected_sectors
                            if hasattr(impact, "affected_countries"):
                                wizard.countries = impact.affected_countries
                        
                        wizard.step = 2
                        st.rerun()
                    else:
                        error_alert(f"Error: {', '.join(result.get('errors', ['Error desconocido']))}")
                else:
                    warning_alert("Escribe un trigger de mercado primero")
    
    # STEP 2: CONFIGURATION
    elif wizard.step == 2:
        st.markdown("### ⚙️ Configuracion de la Campana")
        
        # Show trigger
        st.info(f"**Trigger:** {wizard.trigger}")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            sectors = st.multiselect(
                "Sectores objetivo",
                options=get_sector_options(),
                default=wizard.sectors or [],
                key="config_sectors",
            )
            
            max_targets = st.slider(
                "Maximo de targets",
                min_value=5,
                max_value=30,
                value=wizard.max_targets,
                key="config_max_targets",
            )
        
        with col2:
            country_opts = get_country_options()
            country_labels = [c[1] for c in country_opts]
            country_codes = [c[0] for c in country_opts]
            
            selected_countries = st.multiselect(
                "Paises objetivo",
                options=country_labels,
                default=[country_labels[country_codes.index(c)] for c in (wizard.countries or ["ES"]) if c in country_codes],
                key="config_countries",
            )
            
            countries = [country_codes[country_labels.index(l)] for l in selected_countries]
            
            min_score = st.slider(
                "Fit score minimo",
                min_value=0.0,
                max_value=1.0,
                value=wizard.min_fit_score,
                step=0.05,
                format="%.0f%%",
                key="config_min_score",
            )
        
        prioritize_fei = st.checkbox(
            "✅ Priorizar empresas FEI elegibles",
            value=wizard.prioritize_fei,
            key="config_fei",
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("← Anterior", use_container_width=True):
                go_back()
        
        with col3:
            if st.button("SELECCIONAR TARGETS →", type="primary", use_container_width=True):
                if not sectors:
                    warning_alert("Selecciona al menos un sector")
                elif not countries:
                    warning_alert("Selecciona al menos un pais")
                else:
                    wizard.sectors = sectors
                    wizard.countries = countries
                    wizard.max_targets = max_targets
                    wizard.min_fit_score = min_score
                    wizard.prioritize_fei = prioritize_fei
                    
                    with loading_spinner("Buscando y seleccionando targets..."):
                        result = api.create_campaign_proposal(
                            trigger=wizard.trigger,
                            sectors=sectors,
                            countries=countries,
                            max_targets=max_targets,
                            min_fit_score=min_score,
                        )
                    
                    if result.get("success"):
                        wizard.campaign_id = result.get("campaign_id")
                        proposal = result.get("proposal")
                        
                        # Extract targets
                        targets_list = []
                        if hasattr(proposal, "selection") and proposal.selection:
                            for i, t in enumerate(proposal.selection.targets):
                                targets_list.append({
                                    "id": getattr(t, "id", str(i)),
                                    "company_name": getattr(t, "company_name", f"Empresa {i+1}"),
                                    "sector": getattr(t, "sector", "N/A"),
                                    "fit_score": getattr(t, "fit_score", 0),
                                    "fei_status": getattr(t, "fei_status", "Unknown"),
                                })
                        
                        wizard.targets = targets_list
                        wizard.selected_target_ids = [t["id"] for t in targets_list]
                        wizard.step = 3
                        st.rerun()
                    else:
                        error_alert(f"Error: {', '.join(result.get('errors', ['Error desconocido']))}")
    
    # STEP 3: REVIEW
    elif wizard.step == 3:
        st.markdown("### 📋 Revisar Targets")
        
        targets = wizard.targets or []
        selected_ids = wizard.selected_target_ids or []
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🎯 Targets", len(selected_ids))
        
        with col2:
            fei_count = sum(1 for t in targets if t.get("fei_status") == "Eligible" and t.get("id") in selected_ids)
            st.metric("🏷️ FEI Eligible", fei_count)
        
        with col3:
            avg_score = sum(t.get("fit_score", 0) for t in targets if t.get("id") in selected_ids) / len(selected_ids) if selected_ids else 0
            st.metric("📊 Avg Score", f"{avg_score:.0%}")
        
        st.markdown("---")
        
        # Target list with selection
        if targets:
            import pandas as pd
            
            data = []
            for t in targets:
                data.append({
                    "id": t.get("id", ""),
                    "Seleccionar": t.get("id") in selected_ids,
                    "Empresa": t.get("company_name", "Sin nombre"),
                    "Sector": t.get("sector", "N/A"),
                    "Fit Score": f"{t.get('fit_score', 0):.0%}",
                    "FEI": f"{get_fei_status_emoji(t.get('fei_status', 'Unknown'))} {t.get('fei_status', 'Unknown')}",
                })
            
            df = pd.DataFrame(data)
            
            edited_df = st.data_editor(
                df,
                column_config={
                    "id": None,
                    "Seleccionar": st.column_config.CheckboxColumn("✓", default=True),
                },
                disabled=["id", "Empresa", "Sector", "Fit Score", "FEI"],
                hide_index=True,
                use_container_width=True,
                key="target_editor",
            )
            
            wizard.selected_target_ids = edited_df[edited_df["Seleccionar"]]["id"].tolist()
        else:
            st.info("No se encontraron targets. Vuelve atras para ajustar los criterios.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("← Anterior", use_container_width=True):
                go_back()
        
        with col3:
            if st.button("GENERAR EMAILS →", type="primary", use_container_width=True):
                if not wizard.selected_target_ids:
                    warning_alert("Selecciona al menos un target")
                else:
                    with loading_spinner("Generando emails personalizados..."):
                        if wizard.campaign_id:
                            api.approve_campaign(wizard.campaign_id)
                            
                            result = api.complete_campaign(
                                campaign_id=wizard.campaign_id,
                                trigger=wizard.trigger,
                            )
                            
                            wizard.messages_result = result
                    
                    wizard.step = 4
                    st.rerun()
    
    # STEP 4: COMPLETED
    elif wizard.step == 4:
        st.markdown("""
        <div style="text-align: center; padding: 32px;">
            <span style="font-size: 5rem;">✅</span>
            <h1 style="color: #10B981;">CAMPANA CREADA!</h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🎯 Targets", len(wizard.selected_target_ids or []))
        
        with col2:
            fei_count = sum(1 for t in (wizard.targets or []) if t.get("fei_status") == "Eligible")
            st.metric("🏷️ FEI Eligible", fei_count)
        
        with col3:
            st.metric("📋 Estado", "Pendiente")
        
        st.markdown("---")
        
        st.markdown("### 📝 Trigger")
        st.info(wizard.trigger)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 CREAR OTRA", use_container_width=True):
                reset_wizard()
                st.rerun()
        
        with col2:
            if st.button("📋 VER CAMPANAS", use_container_width=True, type="primary"):
                reset_wizard()
                st.switch_page("pages/5_📋_Campañas.py")
        
        with col3:
            st.link_button("🔗 AIRTABLE", "https://airtable.com", use_container_width=True)

# ============================================================================
# COMPANIES MODE (Simplified)
# ============================================================================

elif wizard.mode == "companies":
    st.markdown("### 🏢 Crear Campana desde Lista de Empresas")
    st.caption("Selecciona empresas existentes para enviar una comunicacion personalizada")
    
    st.info("⚠️ Esta funcionalidad esta en desarrollo. Por favor, usa el modo Trigger Manual.")
    
    if st.button("← Volver a seleccion de modo"):
        reset_wizard()
        st.rerun()

# ============================================================================
# NEWS MODE - Integrated with Trigger Detector
# ============================================================================

elif wizard.mode == "news":
    st.markdown("### 🔍 Búsqueda Automática de Triggers")
    st.caption("Busca automáticamente noticias y eventos de mercado relevantes")
    
    # Check for detected triggers
    if "detected_triggers" not in st.session_state:
        st.session_state.detected_triggers = []
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🔄 Buscar Nuevos Triggers", type="primary", use_container_width=True):
            with st.spinner("Escaneando fuentes de noticias... (esto puede tardar 30-60 segundos)"):
                try:
                    # Try to run trigger scan
                    result = api.run_trigger_scan()
                    if result:
                        st.session_state.detected_triggers = result
                        st.success(f"✅ Encontrados {len(result)} triggers relevantes")
                except Exception as e:
                    st.error(f"Error escaneando triggers: {e}")
    
    with col2:
        if st.button("← Volver a selección de modo", use_container_width=True):
            reset_wizard()
            st.rerun()
    
    st.markdown("---")
    
    # Show detected triggers
    if st.session_state.detected_triggers:
        st.markdown("### 📰 Triggers Detectados")
        st.info("Selecciona un trigger para crear una campaña basada en él")
        
        for i, trigger in enumerate(st.session_state.detected_triggers):
            title = trigger.get("title", "Sin título")
            source = trigger.get("source_name", "Desconocido")
            relevance = trigger.get("relevance_score", 0)
            summary = trigger.get("summary", "")[:200]
            
            relevance_emoji = "🟢" if relevance >= 0.8 else "🟡" if relevance >= 0.5 else "🔴"
            
            with st.expander(f"{relevance_emoji} **{title}** ({source}) - Relevancia: {relevance:.0%}"):
                st.markdown(f"**Resumen:** {summary}")
                st.markdown(f"**Fuente:** [{source}]({trigger.get('source_url', '#')})")
                st.markdown(f"**Sectores afectados:** {', '.join(trigger.get('affected_sectors', ['N/A']))}")
                st.markdown(f"**Países afectados:** {', '.join(trigger.get('affected_countries', ['N/A']))}")
                st.markdown(f"**Acción recomendada:** {trigger.get('recommended_action', 'N/A')}")
                
                if st.button(f"🚀 Crear Campaña desde este Trigger", key=f"create_from_trigger_{i}", type="primary"):
                    # Pre-fill wizard with trigger data
                    wizard.trigger = f"{title}\n\n{summary}"
                    wizard.mode = "trigger"
                    wizard.step = 1
                    
                    # Pre-set sectors and countries if available
                    if trigger.get("affected_sectors"):
                        wizard.sectors = trigger.get("affected_sectors")
                    if trigger.get("affected_countries"):
                        wizard.countries = trigger.get("affected_countries")
                    
                    st.rerun()
    else:
        st.info("""
        👆 Haz clic en "Buscar Nuevos Triggers" para escanear automáticamente:
        - RSS feeds de Financial Times, Reuters, El Economista
        - Noticias del BCE, Banco de España, Comisión Europea
        - Publicaciones de LinkedIn de empresas relevantes
        
        Los triggers se clasifican por relevancia para los productos de Alter-5.
        """)
    
    # Also show recent triggers from Airtable
    st.markdown("---")
    with st.expander("📋 Ver Triggers Guardados Anteriormente"):
        try:
            saved_triggers = api.get_detected_triggers(limit=10)
            if saved_triggers:
                import pandas as pd
                df = pd.DataFrame([
                    {
                        "Fecha": t.get("published_at", "N/A")[:10] if t.get("published_at") else "N/A",
                        "Título": t.get("title", "Sin título")[:50],
                        "Fuente": t.get("source_name", "N/A"),
                        "Relevancia": f"{t.get('relevance_score', 0):.0%}",
                        "Campaña Creada": "✅" if t.get("campaign_created") else "❌",
                    }
                    for t in saved_triggers
                ])
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No hay triggers guardados.")
        except Exception as e:
            st.warning(f"No se pudieron cargar triggers guardados: {e}")
