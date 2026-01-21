"""FEI Evaluation page for Alter-5 Origination Engine.

Provides individual and batch FEI eligibility evaluation capabilities.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.styles import inject_custom_css
from utils.api import get_api
from utils.helpers import get_fei_status_emoji, format_percentage
from components.feedback import (
    loading_spinner, 
    success_alert, 
    error_alert, 
    warning_alert,
    progress_with_status,
    empty_state,
)

# Page config
st.set_page_config(
    page_title="Evaluación FEI - Alter-5",
    page_icon="🏷️",
    layout="wide",
)

inject_custom_css()

st.title("🏷️ Evaluación FEI")

api = get_api()

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Estado Actual", "🎯 Evaluación Individual", "⚡ Evaluación Batch"])

# ============================================================================
# TAB 1: CURRENT STATUS
# ============================================================================

with tab1:
    st.markdown("### 📊 Estado Actual FEI")
    
    with loading_spinner("Cargando estadísticas FEI..."):
        metrics = api.get_dashboard_metrics()
    
    # Metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 12px; border: 1px solid #E5E7EB; text-align: center;">
            <h4 style="color: #6B7280; margin: 0;">✅ ELIGIBLE</h4>
            <h1 style="color: #10B981; margin: 8px 0;">{metrics.fei_eligible}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 12px; border: 1px solid #E5E7EB; text-align: center;">
            <h4 style="color: #6B7280; margin: 0;">❌ NOT ELIGIBLE</h4>
            <h1 style="color: #EF4444; margin: 8px 0;">{metrics.fei_not_eligible}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 12px; border: 1px solid #E5E7EB; text-align: center;">
            <h4 style="color: #6B7280; margin: 0;">⚠️ PARTIAL</h4>
            <h1 style="color: #F59E0B; margin: 8px 0;">{metrics.fei_partial}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 12px; border: 1px solid #E5E7EB; text-align: center;">
            <h4 style="color: #6B7280; margin: 0;">❓ UNKNOWN</h4>
            <h1 style="color: #6B7280; margin: 8px 0;">{metrics.fei_unknown}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 12px; border: 1px solid #E5E7EB; text-align: center;">
            <h4 style="color: #6B7280; margin: 0;">📈 TASA FEI</h4>
            <h1 style="color: #1E40AF; margin: 8px 0;">{metrics.fei_rate:.1f}%</h1>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Visual distribution bar
    st.markdown("### 📊 Distribución Visual")
    
    total = metrics.total_companies
    if total > 0:
        pct_eligible = (metrics.fei_eligible / total * 100) if total > 0 else 0
        pct_not_eligible = (metrics.fei_not_eligible / total * 100) if total > 0 else 0
        pct_partial = (metrics.fei_partial / total * 100) if total > 0 else 0
        pct_unknown = (metrics.fei_unknown / total * 100) if total > 0 else 0
        
        # Ensure we have at least some width for visibility
        bar_eligible = max(pct_eligible, 1) if metrics.fei_eligible > 0 else 0
        bar_not_eligible = max(pct_not_eligible, 1) if metrics.fei_not_eligible > 0 else 0
        bar_partial = max(pct_partial, 1) if metrics.fei_partial > 0 else 0
        bar_unknown = max(pct_unknown, 1) if metrics.fei_unknown > 0 else 0
        
        st.markdown(f"""
        <div style="display: flex; height: 50px; border-radius: 8px; overflow: hidden; margin-bottom: 16px;">
            <div style="width: {bar_eligible}%; background: #10B981; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600;">
                {"Eligible" if pct_eligible > 15 else ""}
            </div>
            <div style="width: {bar_not_eligible}%; background: #EF4444; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600;">
                {"Not Eligible" if pct_not_eligible > 15 else ""}
            </div>
            <div style="width: {bar_partial}%; background: #F59E0B; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600;">
                {"Partial" if pct_partial > 15 else ""}
            </div>
            <div style="width: {bar_unknown}%; background: #6B7280; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600;">
                {"Unknown" if pct_unknown > 15 else ""}
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.875rem; color: #6B7280;">
            <span>✅ Eligible ({pct_eligible:.1f}%)</span>
            <span>❌ Not Eligible ({pct_not_eligible:.1f}%)</span>
            <span>⚠️ Partial ({pct_partial:.1f}%)</span>
            <span>❓ Unknown ({pct_unknown:.1f}%)</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No hay datos de distribución FEI")
    
    st.markdown("---")
    
    # FEI Criteria explanation
    with st.expander("📋 Criterios de Elegibilidad FEI"):
        st.markdown("""
        Una empresa es **FEI Eligible** si cumple **TODOS** estos criterios:
        
        | Criterio | Requisito |
        |----------|-----------|
        | 🏢 Tamaño | SME (< 500 empleados) |
        | 💰 Financiero | Sin dificultades financieras (no en concurso, quiebra, etc.) |
        | 🌍 Geografía | Sede en país de la UE |
        | 🏭 Sector | Sector elegible (no excluido) |
        | ⏰ Operativo | Más de 24 meses operando |
        
        **Sectores Excluidos:**
        - Armas y defensa
        - Tabaco
        - Juego y apuestas
        - Sector financiero especulativo
        """)

# ============================================================================
# TAB 2: INDIVIDUAL EVALUATION
# ============================================================================

with tab2:
    st.markdown("### 🎯 Evaluación Individual")
    st.caption("Evalúa la elegibilidad FEI de una empresa específica")
    
    st.markdown("---")
    
    # Company selector - load all companies
    with loading_spinner("Cargando empresas..."):
        companies_for_eval, _ = api.get_companies(limit=500)
    
    if companies_for_eval:
        company_options = [
            (c.get("id", ""), c.get("fields", {}).get("Company Name", "Sin nombre"))
            for c in companies_for_eval
        ]
        
        selected_idx = st.selectbox(
            "Seleccionar empresa:",
            options=range(len(company_options)),
            format_func=lambda i: company_options[i][1] if i < len(company_options) else "",
            key="fei_eval_company",
        )
        
        if company_options and selected_idx is not None:
            company_id = company_options[selected_idx][0]
            company_name = company_options[selected_idx][1]
            
            # Find company details
            company = next((c for c in companies_for_eval if c.get("id") == company_id), None)
            
            if company:
                fields = company.get("fields", {})
                current_status = fields.get("FEI_Status", "Unknown")
                
                st.markdown(f"""
                **Empresa:** {company_name}  
                **Estado Actual:** {get_fei_status_emoji(current_status)} {current_status}
                """)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Evaluate button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🏷️ EVALUAR ELEGIBILIDAD FEI", type="primary", use_container_width=True):
                    with loading_spinner("Evaluando elegibilidad con IA..."):
                        result = api.evaluate_fei(company_id)
                    
                    if hasattr(result, "status"):
                        status = result.status.value if hasattr(result.status, "value") else str(result.status)
                        
                        st.markdown("---")
                        st.markdown("### 📋 Resultado de Evaluación")
                        
                        # Status display
                        status_colors = {
                            "Eligible": "#10B981",
                            "Not_Eligible": "#EF4444",
                            "Partially_Eligible": "#F59E0B",
                            "Partial": "#F59E0B",
                            "Unknown": "#6B7280",
                        }
                        color = status_colors.get(status, "#6B7280")
                        
                        st.markdown(f"""
                        <div style="
                            text-align: center;
                            padding: 32px;
                            background: {color}20;
                            border: 2px solid {color};
                            border-radius: 12px;
                        ">
                            <h1 style="color: {color}; margin: 0;">
                                {get_fei_status_emoji(status)} {status.replace('_', ' ')}
                            </h1>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Criteria breakdown
                        if hasattr(result, "criteria_results"):
                            st.markdown("### 📊 Detalle de Criterios")
                            
                            criteria = result.criteria_results
                            
                            criteria_map = {
                                "company_size": "🏢 Tamaño de empresa",
                                "financial_health": "💰 Salud financiera",
                                "geography": "🌍 Geografía (UE)",
                                "sector": "🏭 Sector elegible",
                                "operational_time": "⏰ Tiempo operando",
                            }
                            
                            for key, label in criteria_map.items():
                                value = getattr(criteria, key, None)
                                if value is not None:
                                    icon = "✅" if value else "❌"
                                    st.markdown(f"{icon} {label}")
                        
                        # Reasoning
                        if hasattr(result, "reasoning") and result.reasoning:
                            st.markdown("### 💭 Razonamiento")
                            st.info(result.reasoning)
                        
                        success_alert("¡Evaluación completada y guardada!")
                    elif isinstance(result, dict) and result.get("success") is False:
                        error_alert(f"Error: {', '.join(result.get('errors', ['Error desconocido']))}")
                    else:
                        error_alert("Error al evaluar la empresa")
    else:
        empty_state(
            icon="🏢",
            title="No hay empresas",
            message="No se encontraron empresas en la base de datos",
        )

# ============================================================================
# TAB 3: BATCH EVALUATION
# ============================================================================

with tab3:
    st.markdown("### ⚡ Evaluación Batch")
    st.caption("Evalúa múltiples empresas con FEI_Status = 'Unknown' automáticamente")
    
    st.markdown("---")
    
    # Get pending companies count
    with loading_spinner("Verificando empresas pendientes..."):
        pending_companies = api.get_pending_fei_companies(limit=500)
    
    pending_count = len(pending_companies)
    
    st.markdown(f"""
    <div style="background: white; padding: 24px; border-radius: 12px; border: 1px solid #E5E7EB; text-align: center;">
        <h3 style="color: #6B7280; margin: 0;">❓ Empresas Pendientes</h3>
        <h1 style="color: #6B7280; margin: 16px 0;">{pending_count}</h1>
        <p style="color: #9CA3AF; margin: 0;">empresas con FEI_Status = Unknown</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if pending_count > 0:
        # Show list of pending companies
        with st.expander(f"📋 Ver {min(pending_count, 20)} empresas pendientes"):
            for i, company in enumerate(pending_companies[:20]):
                fields = company.get("fields", {})
                name = fields.get("Company Name", "Sin nombre")
                st.write(f"{i+1}. {name}")
            if pending_count > 20:
                st.caption(f"... y {pending_count - 20} más")
        
        # Batch size selector
        max_batch = min(pending_count, 100)
        batch_size = st.slider(
            "Cantidad a evaluar:",
            min_value=1,
            max_value=max_batch,
            value=min(25, max_batch),
            key="batch_size",
        )
        
        st.info(f"""
        ℹ️ Se evaluarán {batch_size} empresas.
        - Tiempo estimado: ~{batch_size * 3} segundos
        - Se actualizará el FEI_Status de cada empresa en Airtable
        """)
        
        # Progress placeholders
        progress_placeholder = st.empty()
        results_placeholder = st.empty()
        
        # Run button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("⚡ INICIAR EVALUACIÓN BATCH", type="primary", use_container_width=True):
                results = []
                
                def on_progress(current: int, total: int, company_name: str, status: str):
                    results.append({"company": company_name, "status": status})
                    with progress_placeholder:
                        progress_with_status(
                            total=total,
                            current=current,
                            message=f"Evaluando: {company_name}...",
                        )
                
                # Run batch evaluation
                with loading_spinner("Iniciando evaluación batch..."):
                    batch_result = api.evaluate_fei_batch(
                        limit=batch_size,
                        on_progress=on_progress,
                    )
                
                # Show results
                with results_placeholder:
                    st.markdown("---")
                    st.markdown("### 📊 Resultados del Batch")
                    
                    if isinstance(batch_result, dict):
                        if batch_result.get("success") is False:
                            error_alert(f"Error: {', '.join(batch_result.get('errors', ['Error desconocido']))}")
                        elif batch_result.get("message"):
                            st.info(batch_result["message"])
                    elif hasattr(batch_result, "evaluations"):
                        evaluations = batch_result.evaluations
                        
                        # Summary
                        eligible_count = sum(1 for e in evaluations if getattr(e, "status", None) == "Eligible" or (hasattr(e, "status") and hasattr(e.status, "value") and e.status.value == "Eligible"))
                        not_eligible_count = sum(1 for e in evaluations if getattr(e, "status", None) == "Not_Eligible" or (hasattr(e, "status") and hasattr(e.status, "value") and e.status.value == "Not_Eligible"))
                        partial_count = sum(1 for e in evaluations if getattr(e, "status", None) in ["Partial", "Partially_Eligible"])
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("✅ Eligible", eligible_count)
                        with col2:
                            st.metric("❌ Not Eligible", not_eligible_count)
                        with col3:
                            st.metric("⚠️ Partial", partial_count)
                        
                        success_alert(f"¡{len(evaluations)} empresas evaluadas correctamente!")
                    else:
                        st.info("Evaluación completada")
    else:
        empty_state(
            icon="✅",
            title="No hay empresas pendientes",
            message="Todas las empresas ya tienen un FEI_Status asignado",
        )
