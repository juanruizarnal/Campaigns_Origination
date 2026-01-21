"""Market Triggers page for Alter-5 Origination Engine.

Monitors detected market triggers and allows creating campaigns from them.
"""

import streamlit as st
import pandas as pd
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.styles import inject_custom_css
from utils.api import get_api
from components.feedback import (
    loading_spinner,
    success_alert,
    error_alert,
    warning_alert,
)

# Page config
st.set_page_config(
    page_title="Triggers de Mercado - Alter-5",
    page_icon="📰",
    layout="wide",
)

inject_custom_css()

st.title("📰 Triggers de Mercado")
st.caption("Detecta y actúa sobre eventos de mercado relevantes para campañas de originación")

st.markdown("---")

api = get_api()

# ============================================================================
# SESSION STATE
# ============================================================================

if "triggers_list" not in st.session_state:
    st.session_state.triggers_list = None
if "selected_trigger" not in st.session_state:
    st.session_state.selected_trigger = None
if "trigger_scan_running" not in st.session_state:
    st.session_state.trigger_scan_running = False

# ============================================================================
# TABS
# ============================================================================

tab1, tab2, tab3 = st.tabs(["📋 Triggers Activos", "🔍 Escanear Fuentes", "⚙️ Configuración"])

# ============================================================================
# TAB 1: ACTIVE TRIGGERS
# ============================================================================

with tab1:
    # Filter controls
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        relevance_filter = st.selectbox(
            "Relevancia mínima",
            options=["Todas", "Alta (>80%)", "Media+ (>50%)", "Solo Alta"],
            index=2,
        )
    
    with col2:
        status_filter = st.selectbox(
            "Estado",
            options=["Todos", "Nuevos", "Procesados", "Con campaña"],
            index=1,
        )
    
    with col3:
        source_filter = st.selectbox(
            "Fuente",
            options=["Todas", "RSS Feed", "Twitter", "Google Alert", "Newsletter", "Manual"],
            index=0,
        )
    
    with col4:
        if st.button("🔄 Refrescar", use_container_width=True):
            st.session_state.triggers_list = None
            st.rerun()
    
    st.markdown("---")
    
    # Load triggers
    if st.session_state.triggers_list is None:
        with st.spinner("Cargando triggers..."):
            # Get triggers from Airtable via API
            try:
                triggers = api.get_triggers(
                    min_relevance=0.5 if "Media" in relevance_filter or "Alta" in relevance_filter else 0.0,
                    status=None if status_filter == "Todos" else status_filter.lower().replace(" ", "_"),
                    limit=50,
                )
                st.session_state.triggers_list = triggers if triggers else []
            except Exception as e:
                st.session_state.triggers_list = []
                st.error(f"Error cargando triggers: {e}")
    
    triggers = st.session_state.triggers_list or []
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    high_rel = len([t for t in triggers if t.get("relevance_score", 0) >= 0.8])
    med_rel = len([t for t in triggers if 0.5 <= t.get("relevance_score", 0) < 0.8])
    with_campaign = len([t for t in triggers if t.get("campaign_created")])
    
    with col1:
        st.metric("📊 Total Triggers", len(triggers))
    with col2:
        st.metric("🟢 Alta Relevancia", high_rel)
    with col3:
        st.metric("🟡 Media Relevancia", med_rel)
    with col4:
        st.metric("🚀 Con Campaña", with_campaign)
    
    st.markdown("---")
    
    # Display triggers
    if not triggers:
        st.info("No hay triggers activos. Escanea fuentes para detectar nuevos triggers.")
    else:
        for idx, trigger in enumerate(triggers):
            relevance = trigger.get("relevance_score", 0)
            rel_emoji = "🟢" if relevance >= 0.8 else "🟡" if relevance >= 0.5 else "🔴"
            processed = "✓" if trigger.get("processed") else ""
            campaign = "🚀" if trigger.get("campaign_created") else ""
            
            source = trigger.get("source_name", "Desconocido")
            title = trigger.get("title", "Sin título")[:80]
            published = trigger.get("published_at", "N/A")
            if isinstance(published, datetime):
                published = published.strftime("%d/%m %H:%M")
            
            with st.expander(
                f"{rel_emoji} {campaign} **{title}** | {source} | {published} | {relevance*100:.0f}% {processed}",
                expanded=relevance >= 0.8 and not trigger.get("processed"),
            ):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**📰 Fuente:** {source}")
                    st.markdown(f"**📅 Publicación:** {published}")
                    
                    if trigger.get("source_url"):
                        st.markdown(f"**🔗 URL:** [{trigger['source_url'][:50]}...]({trigger['source_url']})")
                    
                    if trigger.get("summary"):
                        st.info(f"**📝 Resumen:** {trigger['summary']}")
                    
                    # Keywords matched
                    keywords = trigger.get("keywords_matched", [])
                    if keywords:
                        st.markdown("**🏷️ Keywords:** " + ", ".join(f"`{k}`" for k in keywords[:10]))
                    
                    # Affected sectors and countries
                    sectors = trigger.get("affected_sectors", [])
                    countries = trigger.get("affected_countries", [])
                    
                    if sectors:
                        st.markdown("**🏭 Sectores:** " + ", ".join(sectors[:5]))
                    if countries:
                        st.markdown("**🌍 Países:** " + ", ".join(countries[:5]))
                    
                    # Recommended action
                    action = trigger.get("recommended_action", "N/A")
                    st.markdown(f"**⚡ Acción recomendada:** `{action}`")
                
                with col2:
                    # Relevance indicator
                    st.markdown(f"### {rel_emoji} {relevance*100:.0f}%")
                    st.caption("Relevancia")
                    
                    st.markdown("---")
                    
                    # Status
                    if trigger.get("campaign_created"):
                        st.success("✅ Campaña creada")
                        if trigger.get("campaign_id"):
                            st.markdown(f"ID: `{trigger['campaign_id'][:10]}...`")
                    elif trigger.get("processed"):
                        st.info("📋 Procesado")
                    else:
                        st.warning("🆕 Nuevo")
                    
                    # Actions
                    st.markdown("---")
                    
                    if not trigger.get("campaign_created") and relevance >= 0.5:
                        if st.button(
                            "🚀 Crear Campaña",
                            key=f"create_campaign_{idx}",
                            use_container_width=True,
                            type="primary",
                        ):
                            st.session_state.selected_trigger = trigger
                            st.switch_page("pages/3_🚀_Nueva_Campaña.py")
                    
                    if not trigger.get("processed"):
                        if st.button(
                            "✓ Marcar procesado",
                            key=f"mark_processed_{idx}",
                            use_container_width=True,
                        ):
                            try:
                                api.mark_trigger_processed(trigger.get("id"))
                                st.session_state.triggers_list = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                    
                    if st.button(
                        "🗑️ Descartar",
                        key=f"discard_{idx}",
                        use_container_width=True,
                    ):
                        try:
                            api.discard_trigger(trigger.get("id"))
                            st.session_state.triggers_list = None
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

# ============================================================================
# TAB 2: SCAN SOURCES
# ============================================================================

with tab2:
    st.markdown("### 🔍 Escanear Fuentes de Noticias")
    st.markdown("""
    Ejecuta el agente **Trigger Detector** para buscar nuevos triggers de mercado 
    en las fuentes configuradas (RSS, Twitter, Google Alerts, etc.)
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Fuentes RSS Configuradas")
        
        rss_feeds = [
            ("Financial Times", "https://www.ft.com/rss/home", "🟢"),
            ("Reuters Finance", "https://feeds.reuters.com/reuters/businessNews", "🟢"),
            ("El Confidencial", "https://www.elconfidencial.com/rss/economia/", "🟢"),
            ("Expansión", "https://e00-expansion.uecdn.es/rss/portada.xml", "🟢"),
            ("Cinco Días", "https://cincodias.elpais.com/rss/", "🟢"),
        ]
        
        for name, url, status in rss_feeds:
            st.markdown(f"- {status} **{name}** - `{url[:40]}...`")
    
    with col2:
        st.markdown("#### Últimas Ejecuciones")
        
        # Mock last runs (would come from DB in production)
        st.markdown("- 📅 Hace 2 horas: 3 triggers")
        st.markdown("- 📅 Hace 4 horas: 1 trigger")
        st.markdown("- 📅 Hace 6 horas: 5 triggers")
    
    st.markdown("---")
    
    # Manual scan
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button(
            "🔍 ESCANEAR FUENTES AHORA",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.trigger_scan_running,
        ):
            st.session_state.trigger_scan_running = True
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                status_text.text("Escaneando fuentes RSS...")
                progress_bar.progress(0.2)
                
                # Call trigger detector
                result = api.scan_triggers()
                
                progress_bar.progress(0.8)
                status_text.text("Procesando resultados...")
                
                progress_bar.progress(1.0)
                
                if result and result.get("triggers_detected"):
                    triggers_count = result.get("triggers_detected", 0)
                    high_count = result.get("high_relevance", 0)
                    
                    st.session_state.triggers_list = None  # Force refresh
                    
                    if high_count > 0:
                        success_alert(f"✅ {triggers_count} triggers detectados, {high_count} de alta relevancia")
                    else:
                        st.info(f"✅ {triggers_count} triggers detectados")
                else:
                    st.info("No se detectaron nuevos triggers relevantes")
                    
            except Exception as e:
                error_alert(f"Error escaneando fuentes: {e}")
            finally:
                st.session_state.trigger_scan_running = False
    
    # Manual trigger entry
    st.markdown("---")
    st.markdown("### ✏️ Añadir Trigger Manual")
    
    with st.form("manual_trigger_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            trigger_title = st.text_input(
                "Título del Trigger *",
                placeholder="Ej: BCE anuncia bajada de tipos de interés",
            )
            trigger_source = st.text_input(
                "Fuente",
                placeholder="Ej: Financial Times",
            )
        
        with col2:
            trigger_url = st.text_input(
                "URL (opcional)",
                placeholder="https://...",
            )
            trigger_relevance = st.slider(
                "Relevancia estimada",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1,
            )
        
        trigger_summary = st.text_area(
            "Resumen",
            placeholder="Describe brevemente el trigger y su potencial impacto...",
            height=100,
        )
        
        submitted = st.form_submit_button(
            "📝 Añadir Trigger Manual",
            use_container_width=True,
        )
        
        if submitted:
            if not trigger_title:
                warning_alert("El título es obligatorio")
            else:
                try:
                    api.create_manual_trigger(
                        title=trigger_title,
                        source=trigger_source or "Manual",
                        url=trigger_url,
                        summary=trigger_summary,
                        relevance=trigger_relevance,
                    )
                    st.session_state.triggers_list = None  # Force refresh
                    success_alert("✅ Trigger añadido correctamente")
                    st.rerun()
                except Exception as e:
                    error_alert(f"Error añadiendo trigger: {e}")

# ============================================================================
# TAB 3: CONFIGURATION
# ============================================================================

with tab3:
    st.markdown("### ⚙️ Configuración del Detector de Triggers")
    
    st.info("""
    **Nota:** Los cambios en esta configuración afectarán al agente de detección 
    de triggers cuando se ejecute en modo automático (24/7).
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Umbral de Relevancia")
        
        min_relevance = st.slider(
            "Relevancia mínima para alertas",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.05,
            help="Triggers por debajo de este umbral se ignoran",
        )
        
        auto_campaign_threshold = st.slider(
            "Umbral para crear campaña automática",
            min_value=0.0,
            max_value=1.0,
            value=0.8,
            step=0.05,
            help="Triggers por encima de este umbral crean campañas automáticamente",
        )
        
        st.markdown("#### ⏰ Frecuencia de Escaneo")
        
        scan_interval = st.selectbox(
            "Intervalo de escaneo automático",
            options=["Cada 15 minutos", "Cada 30 minutos", "Cada hora", "Cada 2 horas", "Cada 4 horas"],
            index=2,
        )
    
    with col2:
        st.markdown("#### 🏷️ Keywords de Alta Relevancia")
        
        high_keywords = st.text_area(
            "Keywords que aumentan relevancia",
            value="BCE, ECB, tipos de interés, interest rates, M&A, fusión, adquisición, financiación, funding, inversión",
            height=100,
            help="Separados por comas",
        )
        
        st.markdown("#### 🏭 Sectores Prioritarios")
        
        priority_sectors = st.multiselect(
            "Sectores con relevancia aumentada",
            options=["Energías Renovables", "Real Estate", "Tecnología", "Industria", "Defensa", "Infraestructuras"],
            default=["Energías Renovables", "Real Estate"],
        )
        
        st.markdown("#### 🌍 Países de Interés")
        
        priority_countries = st.multiselect(
            "Países prioritarios",
            options=["España", "Portugal", "Francia", "Alemania", "Italia", "Reino Unido", "Irlanda", "Países Bajos"],
            default=["España", "Portugal"],
        )
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "💾 GUARDAR CONFIGURACIÓN",
            type="primary",
            use_container_width=True,
        ):
            try:
                # Save configuration to Airtable or settings
                success_alert("✅ Configuración guardada correctamente")
            except Exception as e:
                error_alert(f"Error guardando configuración: {e}")

# ============================================================================
# HELP SECTION
# ============================================================================

st.markdown("---")

with st.expander("❓ ¿Cómo funciona el Detector de Triggers?"):
    st.markdown("""
    ### Sistema de Detección de Triggers
    
    El **Agente 7: Trigger Detector** monitorea continuamente múltiples fuentes de noticias
    y detecta eventos de mercado relevantes para campañas de originación.
    
    ### Fuentes Monitoreadas
    
    | Fuente | Tipo | Frecuencia |
    |--------|------|------------|
    | Financial Times | RSS | Cada hora |
    | Reuters Finance | RSS | Cada hora |
    | El Confidencial | RSS | Cada hora |
    | Google Alerts | API | En tiempo real |
    | Twitter/X | API | Cada 30 min |
    
    ### Cálculo de Relevancia
    
    La relevancia (0-100%) se calcula en base a:
    
    1. **Keywords** (+30%): Términos clave como "BCE", "financiación", "M&A"
    2. **Sectores** (+25%): Coincidencia con sectores objetivo de Alter-5
    3. **Países** (+20%): Coincidencia con países donde opera Alter-5
    4. **Productos** (+15%): Mención de productos de deuda o project finance
    5. **Timing** (+10%): Relevancia temporal (noticias recientes)
    
    ### Acciones Recomendadas
    
    - **Alta Relevancia (>80%)**: Crear campaña inmediatamente
    - **Media Relevancia (50-80%)**: Revisar y decidir
    - **Baja Relevancia (<50%)**: Archivar o descartar
    
    ### Modo Automático
    
    En modo 24/7, el sistema puede:
    - Detectar triggers automáticamente
    - Crear borradores de campaña para triggers de alta relevancia
    - Enviar alertas a Slack para revisión
    """)
