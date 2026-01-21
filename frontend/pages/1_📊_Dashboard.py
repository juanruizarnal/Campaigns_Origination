"""Dashboard page for Alter-5 Origination Engine.

Displays key metrics, recent campaigns, and quick actions for the commercial team.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.styles import inject_custom_css
from utils.api import get_api
from utils.session import get_wizard_state, reset_wizard
from utils.helpers import get_campaign_status_emoji, truncate_text
from components.feedback import loading_spinner, empty_state

# Page config
st.set_page_config(
    page_title="Dashboard - Alter-5 Origination",
    page_icon="📊",
    layout="wide",
)

inject_custom_css()

# Header
st.markdown("""
<h1 style="display: flex; align-items: center; gap: 12px;">
    🏠 ALTER-5 ORIGINATION
</h1>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# QUICK CAMPAIGN ACTION
# ============================================================================

st.markdown("""
<div style="background: #F0F9FF; padding: 16px; border-radius: 12px; border: 1px solid #BAE6FD; margin-bottom: 24px;">
    <h3 style="margin: 0 0 8px 0; color: #0369A1;">🚀 CREAR NUEVA CAMPAÑA</h3>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])

with col1:
    trigger = st.text_area(
        "¿Qué está pasando en el mercado?",
        placeholder="Ej: El BCE ha bajado los tipos de interés 0.25%, lo que facilita el acceso a financiación para empresas industriales...",
        height=80,
        key="dashboard_trigger",
        label_visibility="collapsed",
    )

with col2:
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    if st.button("ANALIZAR TRIGGER →", type="primary", use_container_width=True):
        if trigger:
            # Reset and initialize wizard
            reset_wizard()
            wizard = get_wizard_state()
            wizard.trigger = trigger
            wizard.step = 1
            
            st.switch_page("pages/3_🚀_Nueva_Campaña.py")
        else:
            st.warning("⚠️ Escribe un trigger de mercado primero")

st.markdown("---")

# ============================================================================
# METRICS
# ============================================================================

st.subheader("📊 Métricas del Sistema")

# Load data
api = get_api()

with loading_spinner("Cargando métricas..."):
    metrics = api.get_dashboard_metrics()

# Metric cards row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div style="background: white; padding: 20px; border-radius: 12px; border: 1px solid #E5E7EB; text-align: center;">
        <span style="font-size: 2rem;">🏢</span>
        <h4 style="color: #6B7280; margin: 8px 0 4px 0;">EMPRESAS</h4>
        <h1 style="color: #1E40AF; margin: 0;">{metrics.total_companies}</h1>
        <p style="color: #9CA3AF; margin: 4px 0 0 0; font-size: 0.875rem;">en base de datos</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="background: white; padding: 20px; border-radius: 12px; border: 1px solid #E5E7EB; text-align: center;">
        <span style="font-size: 2rem;">🏷️</span>
        <h4 style="color: #6B7280; margin: 8px 0 4px 0;">FEI ELIGIBLE</h4>
        <h1 style="color: #10B981; margin: 0;">{metrics.fei_eligible}</h1>
        <p style="color: #9CA3AF; margin: 4px 0 0 0; font-size: 0.875rem;">{metrics.fei_rate:.1f}% del total</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style="background: white; padding: 20px; border-radius: 12px; border: 1px solid #E5E7EB; text-align: center;">
        <span style="font-size: 2rem;">🎯</span>
        <h4 style="color: #6B7280; margin: 8px 0 4px 0;">CAMPAÑAS</h4>
        <h1 style="color: #1E40AF; margin: 0;">{metrics.total_campaigns}</h1>
        <p style="color: #9CA3AF; margin: 4px 0 0 0; font-size: 0.875rem;">{metrics.active_campaigns} activas</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div style="background: white; padding: 20px; border-radius: 12px; border: 1px solid #E5E7EB; text-align: center;">
        <span style="font-size: 2rem;">📈</span>
        <h4 style="color: #6B7280; margin: 8px 0 4px 0;">TASA FEI</h4>
        <h1 style="color: #1E40AF; margin: 0;">{metrics.fei_rate:.1f}%</h1>
        <p style="color: #9CA3AF; margin: 4px 0 0 0; font-size: 0.875rem;">elegibilidad</p>
    </div>
    """, unsafe_allow_html=True)

# FEI Distribution
st.markdown("### 📊 Distribución FEI Status")

total = metrics.total_companies
if total > 0:
    pct_eligible = (metrics.fei_eligible / total * 100)
    pct_not_eligible = (metrics.fei_not_eligible / total * 100)
    pct_partial = (metrics.fei_partial / total * 100)
    pct_unknown = (metrics.fei_unknown / total * 100)
    
    # Ensure minimum width for visibility
    bar_eligible = max(pct_eligible, 0.5) if metrics.fei_eligible > 0 else 0
    bar_not_eligible = max(pct_not_eligible, 0.5) if metrics.fei_not_eligible > 0 else 0
    bar_partial = max(pct_partial, 0.5) if metrics.fei_partial > 0 else 0
    bar_unknown = max(pct_unknown, 0.5) if metrics.fei_unknown > 0 else 0
    
    st.markdown(f"""
    <div style="display: flex; height: 40px; border-radius: 8px; overflow: hidden; margin-bottom: 8px;">
        <div style="width: {bar_eligible}%; background: #10B981; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 0.75rem;">
            {metrics.fei_eligible if pct_eligible > 8 else ''}
        </div>
        <div style="width: {bar_not_eligible}%; background: #EF4444; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 0.75rem;">
            {metrics.fei_not_eligible if pct_not_eligible > 8 else ''}
        </div>
        <div style="width: {bar_partial}%; background: #F59E0B; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 0.75rem;">
            {metrics.fei_partial if pct_partial > 8 else ''}
        </div>
        <div style="width: {bar_unknown}%; background: #6B7280; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 0.75rem;">
            {metrics.fei_unknown if pct_unknown > 8 else ''}
        </div>
    </div>
    <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #6B7280;">
        <span>✅ Eligible ({pct_eligible:.1f}%)</span>
        <span>❌ Not Eligible ({pct_not_eligible:.1f}%)</span>
        <span>⚠️ Partial ({pct_partial:.1f}%)</span>
        <span>❓ Unknown ({pct_unknown:.1f}%)</span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("No hay datos de distribución FEI")

st.markdown("---")

# ============================================================================
# RECENT CAMPAIGNS
# ============================================================================

st.subheader("📈 Campañas Recientes")

if metrics.recent_campaigns:
    for campaign in metrics.recent_campaigns[:5]:
        fields = campaign.get("fields", {})
        campaign_id = campaign.get("id", "")
        
        # Use correct Airtable field names
        name = fields.get("Campaign_Name", "Sin nombre")
        status = fields.get("Status", "Draft")
        description = fields.get("Description", "") or fields.get("Campaign_Rationale", "")
        
        status_emoji = get_campaign_status_emoji(status)
        
        col1, col2 = st.columns([5, 1])
        
        with col1:
            st.markdown(f"""
            <div style="background: white; padding: 16px; border-radius: 8px; border: 1px solid #E5E7EB; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{name}</strong>
                        <p style="color: #6B7280; margin: 4px 0 0 0; font-size: 0.875rem;">{truncate_text(description, 80)}</p>
                    </div>
                    <span style="background: #E5E7EB; padding: 4px 12px; border-radius: 9999px; font-size: 0.75rem;">
                        {status_emoji} {status.replace('_', ' ')}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("Ver →", key=f"view_camp_{campaign_id}"):
                st.session_state["selected_campaign_id"] = campaign_id
                st.switch_page("pages/5_📋_Campañas.py")
else:
    empty_state(
        icon="📋",
        title="No hay campañas todavía",
        message="Crea tu primera campaña escribiendo un trigger de mercado arriba",
    )

# ============================================================================
# QUICK LINKS
# ============================================================================

st.markdown("---")
st.subheader("🔗 Acciones Rápidas")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏢 Ver Empresas", use_container_width=True):
        st.switch_page("pages/2_🏢_Empresas.py")

with col2:
    if st.button("🏷️ Evaluar FEI", use_container_width=True):
        st.switch_page("pages/4_🏷️_Evaluacion_FEI.py")

with col3:
    if st.button("📋 Ver Campañas", use_container_width=True):
        st.switch_page("pages/5_📋_Campañas.py")

with col4:
    if st.button("🔄 Pipeline", use_container_width=True):
        st.switch_page("pages/6_🔄_Originacion.py")

# ============================================================================
# TIP
# ============================================================================

st.markdown("---")
st.info("""
**💡 Tip**: Escribe triggers como "BCE baja tipos" o "Nueva ley de renovables" para crear campañas personalizadas automáticamente.
El sistema analizará el trigger, seleccionará los mejores targets y generará emails personalizados.
""")
