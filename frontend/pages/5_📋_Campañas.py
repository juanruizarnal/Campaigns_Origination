"""Campaigns page for Alter-5 Origination Engine.

Displays and manages existing campaigns with status tracking.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.styles import inject_custom_css
from components.sidebar import render_sidebar
from utils.api import get_api
from utils.helpers import format_date, get_campaign_status_emoji, truncate_text
from components.feedback import loading_spinner, success_alert, error_alert, empty_state
from components.metrics import metric_card

# Page config
st.set_page_config(
    page_title="Campañas - Alter-5",
    page_icon="📋",
    layout="wide",
)

inject_custom_css()
render_sidebar()

st.title("📋 Campañas")

api = get_api()

# Tabs
tab1, tab2 = st.tabs(["📋 Lista de Campañas", "📊 Detalle de Campaña"])

# ============================================================================
# TAB 1: CAMPAIGN LIST
# ============================================================================

with tab1:
    st.markdown("### 📋 Campañas Existentes")
    
    # Filters
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.text_input(
            "🔍 Buscar campaña...",
            placeholder="Escribe para buscar...",
            key="campaign_search",
            label_visibility="collapsed",
        )
    
    with col2:
        status_filter = st.selectbox(
            "Estado:",
            options=["Todos", "Draft", "Pending_Review", "Approved", "Active", "Completed"],
            key="status_filter",
            label_visibility="collapsed",
        )
    
    with col3:
        sort_by = st.selectbox(
            "Ordenar por:",
            options=["Fecha (reciente)", "Fecha (antigua)", "Nombre"],
            key="sort_by",
            label_visibility="collapsed",
        )
    
    st.markdown("---")
    
    # Load campaigns
    status_param = status_filter if status_filter != "Todos" else None
    
    with loading_spinner("Cargando campañas..."):
        campaigns = api.get_campaigns(status=status_param, limit=50)
    
    if campaigns:
        st.caption(f"Mostrando {len(campaigns)} campañas")
        
        for campaign in campaigns:
            fields = campaign.get("fields", {})
            campaign_id = campaign.get("id", "")
            
            # Use correct Airtable field names
            # Campaign_Name field is "fld4jRij88sR67xZI"
            name = fields.get("Campaign_Name", "Sin nombre")
            status = fields.get("Status", "Draft")
            description = fields.get("Description", "")
            rationale = fields.get("Campaign_Rationale", "")
            
            status_emoji = get_campaign_status_emoji(status)
            
            # Campaign card
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style="
                        background: white;
                        padding: 20px;
                        border-radius: 12px;
                        border: 1px solid #E5E7EB;
                        margin-bottom: 8px;
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <h3 style="margin: 0 0 8px 0;">{name}</h3>
                                <p style="color: #6B7280; margin: 0;">{truncate_text(description or rationale, 150)}</p>
                            </div>
                            <div style="text-align: right;">
                                <span style="
                                    background: #E5E7EB;
                                    padding: 4px 12px;
                                    border-radius: 9999px;
                                    font-size: 0.875rem;
                                ">{status_emoji} {status.replace('_', ' ')}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("Ver Detalle →", key=f"view_{campaign_id}"):
                        st.session_state["selected_campaign_id"] = campaign_id
                        st.rerun()
    else:
        empty_state(
            icon="📋",
            title="No hay campañas",
            message="Crea tu primera campaña desde el Dashboard o la sección Nueva Campaña",
            action_label="Crear Campaña",
        )
        if st.button("🚀 Crear Primera Campaña", type="primary"):
            st.switch_page("pages/3_🚀_Nueva_Campaña.py")

# ============================================================================
# TAB 2: CAMPAIGN DETAIL
# ============================================================================

with tab2:
    campaign_id = st.session_state.get("selected_campaign_id")
    
    if not campaign_id:
        st.info("👆 Selecciona una campaña de la lista para ver su detalle")
        
        # Allow direct selection
        with loading_spinner("Cargando campañas..."):
            all_campaigns = api.get_campaigns(limit=50)
        
        if all_campaigns:
            campaign_names = [c.get("fields", {}).get("Campaign_Name", "Sin nombre") for c in all_campaigns]
            selected_idx = st.selectbox(
                "O selecciona una campaña:",
                options=range(len(all_campaigns)),
                format_func=lambda i: campaign_names[i],
                key="direct_campaign_select",
            )
            
            if st.button("Ver Detalle"):
                campaign_id = all_campaigns[selected_idx].get("id")
                st.session_state["selected_campaign_id"] = campaign_id
                st.rerun()
    
    if campaign_id:
        with loading_spinner("Cargando detalle de campaña..."):
            detail = api.get_campaign_detail(campaign_id)
        
        if detail:
            campaign = detail.get("campaign", {})
            targets = detail.get("targets", [])
            fields = campaign.get("fields", {})
            
            # Header
            name = fields.get("Campaign_Name", "Sin nombre")
            status = fields.get("Status", "Draft")
            description = fields.get("Description", "")
            rationale = fields.get("Campaign_Rationale", "")
            
            st.markdown(f"### {name}")
            
            status_emoji = get_campaign_status_emoji(status)
            st.markdown(f"**Estado:** {status_emoji} {status.replace('_', ' ')}")
            
            st.markdown("---")
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🎯 Targets", len(targets))
            
            with col2:
                # Count FEI eligible targets would require querying related business units
                st.metric("🏷️ Prioridad", fields.get("Priority", "Medium"))
            
            with col3:
                product_line = fields.get("Product_Line", [])
                products = ", ".join(product_line) if isinstance(product_line, list) else str(product_line)
                st.metric("📦 Producto", products[:20] if products else "N/A")
            
            with col4:
                size = fields.get("Campaign_Size", "N/A")
                st.metric("📊 Tamaño", size)
            
            st.markdown("---")
            
            # Description / Rationale
            if description or rationale:
                st.markdown("### 📝 Descripción")
                st.info(description or rationale)
            
            # Email templates
            subject_es = fields.get("Email_Subject_Template_ES", "")
            body_es = fields.get("Email_Body_Template_ES", "")
            
            if subject_es or body_es:
                st.markdown("### 📧 Plantilla de Email (ES)")
                if subject_es:
                    st.markdown(f"**Asunto:** {subject_es}")
                if body_es:
                    with st.expander("Ver cuerpo del email"):
                        st.markdown(body_es)
            
            st.markdown("---")
            
            # Targets table
            st.markdown("### 🎯 Targets de la Campaña")
            
            if targets:
                import pandas as pd
                
                data = []
                for target in targets:
                    tf = target.get("fields", {})
                    data.append({
                        "Target": tf.get("Target_Name", "Sin nombre"),
                        "Fit Score": f"{tf.get('Fit_Score', 0):.0%}" if isinstance(tf.get('Fit_Score'), (int, float)) else "N/A",
                        "Status": tf.get("Status", "Pending_Review"),
                    })
                
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No hay targets asociados a esta campaña")
            
            st.markdown("---")
            
            # Actions
            st.markdown("### ⚡ Acciones")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if status in ["Draft", "Pending_Review"]:
                    if st.button("✅ Aprobar Campaña", type="primary", use_container_width=True):
                        with loading_spinner("Aprobando campaña..."):
                            api.approve_campaign(campaign_id)
                        success_alert("¡Campaña aprobada!")
                        st.rerun()
            
            with col2:
                if status in ["Draft", "Pending_Review", "Approved"]:
                    if st.button("📧 Generar Emails", use_container_width=True):
                        with loading_spinner("Generando emails personalizados..."):
                            result = api.complete_campaign(
                                campaign_id=campaign_id,
                                trigger=rationale or description,
                            )
                        
                        if result:
                            success_alert("¡Emails generados correctamente!")
                            st.rerun()
                        else:
                            error_alert("Error generando emails")
            
            with col3:
                # Link to Airtable - construct URL
                base_id = "appEgNSP0tOLJ9YJ9"
                table_id = "tbl0B5YGXveYzyADI"  # Origination_Campaigns table
                airtable_url = f"https://airtable.com/{base_id}/{table_id}/{campaign_id}"
                st.link_button("🔗 Abrir en Airtable", airtable_url, use_container_width=True)
        else:
            error_alert("No se pudo cargar el detalle de la campaña")
