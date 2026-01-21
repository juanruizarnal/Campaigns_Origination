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
from core.models import ProductLine

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
tab1, tab2, tab3 = st.tabs(["📋 Lista de Campañas", "📊 Detalle de Campaña", "➕ Nueva Campaña"])

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
            message="Crea tu primera campaña desde la pestaña Nueva Campaña",
            action_label="Crear Campaña",
        )

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

# ============================================================================
# TAB 3: NEW CAMPAIGN
# ============================================================================

with tab3:
    st.markdown("### ➕ Nueva Campaña")
    st.caption("Crea campañas completas con Market_Context y Campaign_Targets.")

    if not api.airtable:
        error_alert("Airtable no disponible. Revisa la configuración.")
    else:
        product_labels = {
            "Corporate_Debt": "Corporate Debt",
            "Project_Finance": "Project Finance",
            "M&A_Advisory": "M&A Advisory",
            "FEI_Guarantee": "FEI Guarantee",
            "Refinancing": "Refinancing",
            "Bridge_Loan": "Bridge Loan",
        }
        product_options = [item.value for item in ProductLine]

        prefill_bu_ids = st.session_state.get("campaign_prefill_bu_ids", [])
        prefill_bus = st.session_state.get("campaign_prefill_business_units", [])
        prefill_mode = bool(prefill_bu_ids and prefill_bus)

        if prefill_mode:
            business_units = prefill_bus
            filtered_bus = prefill_bus
            st.info("Usando compañías seleccionadas desde Empresas. Completa el contexto para crear la campaña.")
        else:
            if "campaign_business_units_cache" not in st.session_state:
                with loading_spinner("Cargando empresas..."):
                    st.session_state["campaign_business_units_cache"] = api.get_business_units(
                        limit=1000,
                        include_company_fields=True,
                    )
            business_units = st.session_state["campaign_business_units_cache"]

            sector_options = sorted({
                sector
                for bu in business_units
                for sector in (bu.get("sector_names") or [])
                if sector
            })
            activity_options = sorted({
                activity
                for bu in business_units
                for activity in (bu.get("activities_names") or [])
                if activity
            })

            employee_values = [bu.get("employees") for bu in business_units if bu.get("employees") is not None]
            revenue_values = [bu.get("revenues") for bu in business_units if bu.get("revenues") is not None]

            st.markdown("#### 🔎 Filtros de compañías")
            col1, col2, col3 = st.columns(3)
            with col1:
                selected_sectors = st.multiselect("Sector", options=sector_options)
            with col2:
                selected_activities = st.multiselect("Actividad", options=activity_options)
            with col3:
                fei_options = ["Todos", "Eligible", "Not_Eligible", "Partially_Eligible", "Pending_Review", "Expired", "Unknown"]
                selected_fei = st.selectbox("Elegibilidad FEI", options=fei_options)

            col4, col5 = st.columns(2)
            with col4:
                emp_min_default = min(employee_values) if employee_values else 0
                emp_max_default = max(employee_values) if employee_values else 0
                emp_min = st.number_input("Empleados mín.", min_value=0.0, value=float(emp_min_default))
                emp_max = st.number_input("Empleados máx.", min_value=0.0, value=float(emp_max_default))
            with col5:
                rev_min_default = min(revenue_values) if revenue_values else 0
                rev_max_default = max(revenue_values) if revenue_values else 0
                rev_min = st.number_input("Facturación mín. (€)", min_value=0.0, value=float(rev_min_default))
                rev_max = st.number_input("Facturación máx. (€)", min_value=0.0, value=float(rev_max_default))

            def _matches_filters(bu: dict) -> bool:
                if selected_sectors:
                    bu_sectors = set(bu.get("sector_names") or [])
                    if not bu_sectors.intersection(selected_sectors):
                        return False
                if selected_activities:
                    bu_activities = set(bu.get("activities_names") or [])
                    if not bu_activities.intersection(selected_activities):
                        return False
                if selected_fei != "Todos":
                    fei_status = bu.get("fei_status") or "Unknown"
                    if fei_status != selected_fei:
                        return False
                if emp_min > 0 or emp_max > 0:
                    employees = bu.get("employees")
                    if employees is None:
                        return False
                    if emp_min > 0 and employees < emp_min:
                        return False
                    if emp_max > 0 and employees > emp_max:
                        return False
                if rev_min > 0 or rev_max > 0:
                    revenues = bu.get("revenues")
                    if revenues is None:
                        return False
                    if rev_min > 0 and revenues < rev_min:
                        return False
                    if rev_max > 0 and revenues > rev_max:
                        return False
                return True

            filtered_bus = [bu for bu in business_units if _matches_filters(bu)]
            st.caption(f"Empresas disponibles: {len(filtered_bus)}")

        bu_options = [bu["id"] for bu in filtered_bus]
        bu_labels = {bu["id"]: bu["label"] for bu in filtered_bus}
        if "new_campaign_business_units" not in st.session_state:
            st.session_state["new_campaign_business_units"] = prefill_bu_ids
        if "new_campaign_name" not in st.session_state:
            st.session_state["new_campaign_name"] = ""
        if "new_campaign_description" not in st.session_state:
            st.session_state["new_campaign_description"] = ""
        if "new_campaign_products" not in st.session_state:
            st.session_state["new_campaign_products"] = []

        with st.form("new_campaign_form", clear_on_submit=False):
            name = st.text_input(
                "Nombre Campaña *",
                placeholder="Ej. Renovables Q1 2026",
                key="new_campaign_name",
            )
            description = st.text_area(
                "Descripción *",
                height=120,
                key="new_campaign_description",
            )
            products = st.multiselect(
                "Selección productos de Alter-5 *",
                options=product_options,
                format_func=lambda value: product_labels.get(value, value),
                key="new_campaign_products",
            )
            selected_bus = st.multiselect(
                "Selección de Compañías a contactar *",
                options=bu_options,
                format_func=lambda value: bu_labels.get(value, value),
                key="new_campaign_business_units",
            )

            selected_labels = [bu_labels.get(bu_id, bu_id) for bu_id in selected_bus]
            if selected_labels:
                st.markdown("**Compañías seleccionadas:**")
                st.markdown(
                    "<br>".join(f"• {label}" for label in selected_labels),
                    unsafe_allow_html=True,
                )

            submitted = st.form_submit_button("🚀 Crear Campaña", type="primary")

        if submitted:
            errors = []
            if not name.strip():
                errors.append("Indica un nombre de campaña.")
            if not description.strip():
                errors.append("Añade una descripción.")
            if not products:
                errors.append("Selecciona al menos un producto.")
            if not selected_bus:
                errors.append("Selecciona al menos una compañía.")

            if errors:
                for message in errors:
                    error_alert(message)
            else:
                if prefill_mode:
                    filters_summary = "Origen: Empresas (selección manual)"
                else:
                    filters_summary = "; ".join(filter(None, [
                        f"Sectores: {', '.join(selected_sectors)}" if selected_sectors else None,
                        f"Actividades: {', '.join(selected_activities)}" if selected_activities else None,
                        f"Empleados: {int(emp_min)}-{int(emp_max)}" if emp_max or emp_min else None,
                        f"Facturación: €{int(rev_min)}-€{int(rev_max)}" if rev_max or rev_min else None,
                        f"FEI: {selected_fei}" if selected_fei != "Todos" else None,
                        f"Productos: {', '.join(products)}" if products else None,
                    ]))

                with loading_spinner("Creando campaña y contexto..."):
                    result = api.create_campaign_with_targets(
                        campaign_name=name.strip(),
                        description=description.strip(),
                        product_lines=products,
                        business_unit_ids=selected_bus,
                        filters_summary=filters_summary or None,
                    )

                if result.get("success"):
                    success_alert(
                        f"Campaña creada ✅ Contextos: {result.get('contexts_created', 0)} "
                        f"| Targets: {result.get('targets_created', 0)}"
                    )
                    st.session_state["selected_campaign_id"] = result.get("campaign_id")
                    st.session_state["campaign_prefill_bu_ids"] = []
                    st.rerun()
                else:
                    error_list = result.get("errors") or ["Error creando campaña"]
                    error_alert(" | ".join(error_list))
