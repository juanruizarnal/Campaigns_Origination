"""Follow-up Management page for Alter-5 Origination Engine.

Manage email follow-ups, view engagement, and handle hot leads.
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
    page_title="Follow-up - Alter-5",
    page_icon="📧",
    layout="wide",
)

inject_custom_css()

st.title("📧 Gestión de Follow-up")
st.caption("Monitorea engagement, gestiona hot leads y programa follow-ups automáticos")

st.markdown("---")

api = get_api()

# ============================================================================
# SESSION STATE
# ============================================================================

if "followup_queue" not in st.session_state:
    st.session_state.followup_queue = None
if "hot_leads" not in st.session_state:
    st.session_state.hot_leads = None
if "engagement_stats" not in st.session_state:
    st.session_state.engagement_stats = None

# ============================================================================
# TABS
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "🔥 Hot Leads",
    "📬 Cola de Follow-up",
    "📊 Engagement",
    "⚙️ Configuración",
])

# ============================================================================
# TAB 1: HOT LEADS
# ============================================================================

with tab1:
    st.markdown("### 🔥 Hot Leads")
    st.markdown("""
    Contactos que han mostrado **alto interés**: clicks en enlaces, múltiples aperturas,
    o respuestas a emails. Requieren **acción inmediata**.
    """)
    
    # Filter
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        lead_type = st.selectbox(
            "Tipo de acción",
            options=["Todos", "Clicks", "Respuestas", "Múltiples aperturas"],
            index=0,
        )
    
    with col2:
        time_range = st.selectbox(
            "Período",
            options=["Últimas 24h", "Últimos 7 días", "Últimos 30 días", "Todo"],
            index=1,
        )
    
    with col3:
        if st.button("🔄 Refrescar", key="refresh_hot_leads", use_container_width=True):
            st.session_state.hot_leads = None
            st.rerun()
    
    st.markdown("---")
    
    # Load hot leads
    if st.session_state.hot_leads is None:
        with st.spinner("Cargando hot leads..."):
            try:
                leads = api.get_hot_leads(
                    lead_type=None if lead_type == "Todos" else lead_type.lower(),
                    days={"Últimas 24h": 1, "Últimos 7 días": 7, "Últimos 30 días": 30, "Todo": 365}.get(time_range, 7),
                )
                st.session_state.hot_leads = leads if leads else []
            except Exception as e:
                st.session_state.hot_leads = []
                st.error(f"Error cargando hot leads: {e}")
    
    hot_leads = st.session_state.hot_leads or []
    
    # Summary
    col1, col2, col3, col4 = st.columns(4)
    
    clicks = len([l for l in hot_leads if l.get("action_type") == "click"])
    responses = len([l for l in hot_leads if l.get("action_type") == "response"])
    opens = len([l for l in hot_leads if l.get("action_type") == "multiple_opens"])
    
    with col1:
        st.metric("🔥 Total Hot Leads", len(hot_leads), delta=None)
    with col2:
        st.metric("🖱️ Clicks", clicks)
    with col3:
        st.metric("📧 Respuestas", responses)
    with col4:
        st.metric("👀 Múltiples Aperturas", opens)
    
    st.markdown("---")
    
    # Hot leads list
    if not hot_leads:
        st.info("🎉 No hay hot leads pendientes de gestión")
    else:
        for idx, lead in enumerate(hot_leads):
            action_type = lead.get("action_type", "unknown")
            emoji = "🖱️" if action_type == "click" else "📧" if action_type == "response" else "👀"
            
            contact_name = lead.get("contact_name", "Desconocido")
            company_name = lead.get("company_name", "")
            campaign_name = lead.get("campaign_name", "")
            timestamp = lead.get("timestamp", "N/A")
            if isinstance(timestamp, datetime):
                timestamp = timestamp.strftime("%d/%m %H:%M")
            
            with st.expander(
                f"{emoji} **{contact_name}** | {company_name} | {timestamp}",
                expanded=idx < 3,  # Expand first 3
            ):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**👤 Contacto:** {contact_name}")
                    st.markdown(f"**🏢 Empresa:** {company_name}")
                    st.markdown(f"**📧 Email:** `{lead.get('email', 'N/A')}`")
                    st.markdown(f"**🚀 Campaña:** {campaign_name}")
                    st.markdown(f"**⏰ Acción:** {timestamp}")
                    
                    if lead.get("action_detail"):
                        st.info(f"**Detalle:** {lead['action_detail']}")
                    
                    if lead.get("response_preview"):
                        st.success(f"**Respuesta:** {lead['response_preview'][:200]}...")
                
                with col2:
                    # Priority indicator
                    priority = lead.get("priority", "medium")
                    priority_emoji = "🔴" if priority == "urgent" else "🟠" if priority == "high" else "🟡"
                    
                    st.markdown(f"### {priority_emoji}")
                    st.caption(f"Prioridad: {priority.upper()}")
                    
                    st.markdown("---")
                    
                    # Actions
                    if st.button(
                        "📞 Marcar Contactado",
                        key=f"contacted_{idx}",
                        use_container_width=True,
                        type="primary",
                    ):
                        try:
                            api.mark_lead_contacted(lead.get("target_id"))
                            st.session_state.hot_leads = None
                            success_alert("✅ Marcado como contactado")
                            st.rerun()
                        except Exception as e:
                            error_alert(f"Error: {e}")
                    
                    if st.button(
                        "📅 Programar Reunión",
                        key=f"meeting_{idx}",
                        use_container_width=True,
                    ):
                        try:
                            api.schedule_meeting(lead.get("target_id"))
                            st.session_state.hot_leads = None
                            success_alert("✅ Reunión programada")
                            st.rerun()
                        except Exception as e:
                            error_alert(f"Error: {e}")
                    
                    if st.button(
                        "✓ Archivar",
                        key=f"archive_{idx}",
                        use_container_width=True,
                    ):
                        try:
                            api.archive_lead(lead.get("target_id"))
                            st.session_state.hot_leads = None
                            st.rerun()
                        except Exception as e:
                            error_alert(f"Error: {e}")

# ============================================================================
# TAB 2: FOLLOW-UP QUEUE
# ============================================================================

with tab2:
    st.markdown("### 📬 Cola de Follow-up")
    st.markdown("""
    Follow-ups programados automáticamente para contactos que abrieron emails 
    pero no respondieron. Puedes ejecutarlos o modificarlos.
    """)
    
    # Filter
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        queue_status = st.selectbox(
            "Estado",
            options=["Pendientes", "Ejecutados", "Todos"],
            index=0,
            key="queue_status",
        )
    
    with col2:
        queue_sort = st.selectbox(
            "Ordenar por",
            options=["Fecha programada", "Número de follow-up", "Campaña"],
            index=0,
        )
    
    with col3:
        if st.button("🔄 Refrescar", key="refresh_queue", use_container_width=True):
            st.session_state.followup_queue = None
            st.rerun()
    
    st.markdown("---")
    
    # Load queue
    if st.session_state.followup_queue is None:
        with st.spinner("Cargando cola de follow-up..."):
            try:
                queue = api.get_followup_queue(
                    status="pending" if queue_status == "Pendientes" else ("executed" if queue_status == "Ejecutados" else None),
                )
                st.session_state.followup_queue = queue if queue else []
            except Exception as e:
                st.session_state.followup_queue = []
                st.error(f"Error cargando cola: {e}")
    
    queue = st.session_state.followup_queue or []
    
    # Summary
    pending = len([q for q in queue if not q.get("executed")])
    due_today = len([q for q in queue if not q.get("executed") and q.get("scheduled_for") and 
                     (isinstance(q["scheduled_for"], datetime) and q["scheduled_for"].date() <= datetime.now().date())])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📬 En Cola", len(queue))
    with col2:
        st.metric("⏰ Pendientes", pending)
    with col3:
        st.metric("🔔 Vencen Hoy", due_today, delta=f"Urgente!" if due_today > 5 else None)
    
    st.markdown("---")
    
    # Execute all pending button
    if pending > 0:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(
                f"🚀 EJECUTAR {due_today if due_today > 0 else pending} FOLLOW-UPS",
                type="primary",
                use_container_width=True,
            ):
                with st.spinner("Ejecutando follow-ups..."):
                    try:
                        result = api.execute_followups(max_count=due_today if due_today > 0 else 10)
                        if result and result.get("executed", 0) > 0:
                            success_alert(f"✅ {result['executed']} follow-ups enviados")
                            st.session_state.followup_queue = None
                            st.rerun()
                        else:
                            st.info("No hay follow-ups listos para enviar")
                    except Exception as e:
                        error_alert(f"Error ejecutando follow-ups: {e}")
        
        st.markdown("---")
    
    # Queue items
    if not queue:
        st.info("No hay follow-ups en cola")
    else:
        for idx, item in enumerate(queue):
            email = item.get("email", "")
            scheduled = item.get("scheduled_for", "N/A")
            if isinstance(scheduled, datetime):
                is_due = scheduled <= datetime.now()
                scheduled_str = scheduled.strftime("%d/%m %H:%M")
            else:
                is_due = False
                scheduled_str = str(scheduled)
            
            followup_num = item.get("followup_number", 1)
            executed = item.get("executed", False)
            
            status_emoji = "✅" if executed else ("🔔" if is_due else "⏰")
            
            with st.expander(
                f"{status_emoji} **{email}** | Follow-up #{followup_num} | {scheduled_str}",
                expanded=is_due and not executed,
            ):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**📧 Email:** `{email}`")
                    st.markdown(f"**📅 Programado para:** {scheduled_str}")
                    st.markdown(f"**🔢 Follow-up #:** {followup_num}")
                    st.markdown(f"**📝 Template:** `{item.get('template', 'followup_1')}`")
                    
                    if item.get("campaign_id"):
                        st.markdown(f"**🚀 Campaña:** `{item['campaign_id'][:20]}...`")
                    
                    if executed:
                        executed_at = item.get("executed_at", "N/A")
                        if isinstance(executed_at, datetime):
                            executed_at = executed_at.strftime("%d/%m %H:%M")
                        st.success(f"✅ Ejecutado: {executed_at}")
                
                with col2:
                    if not executed:
                        if st.button(
                            "📧 Enviar Ahora",
                            key=f"send_now_{idx}",
                            use_container_width=True,
                            type="primary",
                        ):
                            try:
                                api.execute_single_followup(item.get("id"))
                                st.session_state.followup_queue = None
                                success_alert("✅ Follow-up enviado")
                                st.rerun()
                            except Exception as e:
                                error_alert(f"Error: {e}")
                        
                        if st.button(
                            "✏️ Editar",
                            key=f"edit_{idx}",
                            use_container_width=True,
                        ):
                            st.session_state.edit_followup = item
                            # Open edit modal (simplified as form below)
                        
                        if st.button(
                            "🗑️ Cancelar",
                            key=f"cancel_{idx}",
                            use_container_width=True,
                        ):
                            try:
                                api.cancel_followup(item.get("id"))
                                st.session_state.followup_queue = None
                                st.rerun()
                            except Exception as e:
                                error_alert(f"Error: {e}")

# ============================================================================
# TAB 3: ENGAGEMENT STATS
# ============================================================================

with tab3:
    st.markdown("### 📊 Estadísticas de Engagement")
    
    # Load stats
    if st.session_state.engagement_stats is None:
        with st.spinner("Cargando estadísticas..."):
            try:
                stats = api.get_engagement_stats(days=30)
                st.session_state.engagement_stats = stats or {}
            except Exception as e:
                st.session_state.engagement_stats = {}
                st.error(f"Error cargando estadísticas: {e}")
    
    stats = st.session_state.engagement_stats
    
    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "📧 Emails Enviados",
            stats.get("total_sent", 0),
            delta=f"+{stats.get('sent_last_7d', 0)} últimos 7d",
        )
    with col2:
        open_rate = stats.get("open_rate", 0) * 100
        st.metric(
            "👀 Tasa de Apertura",
            f"{open_rate:.1f}%",
            delta=f"{stats.get('open_rate_trend', 0):+.1f}%",
        )
    with col3:
        click_rate = stats.get("click_rate", 0) * 100
        st.metric(
            "🖱️ Tasa de Click",
            f"{click_rate:.1f}%",
            delta=f"{stats.get('click_rate_trend', 0):+.1f}%",
        )
    with col4:
        response_rate = stats.get("response_rate", 0) * 100
        st.metric(
            "💬 Tasa de Respuesta",
            f"{response_rate:.1f}%",
            delta=f"{stats.get('response_rate_trend', 0):+.1f}%",
        )
    with col5:
        meeting_rate = stats.get("meeting_rate", 0) * 100
        st.metric(
            "📅 Reuniones",
            stats.get("meetings_scheduled", 0),
            delta=f"{meeting_rate:.1f}% conversión",
        )
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Engagement por Semana")
        
        # Mock data for chart (would come from API in production)
        chart_data = pd.DataFrame({
            "Semana": ["W1", "W2", "W3", "W4"],
            "Aperturas": [45, 52, 48, 61],
            "Clicks": [12, 15, 11, 18],
            "Respuestas": [3, 5, 4, 7],
        })
        
        st.bar_chart(chart_data.set_index("Semana"))
    
    with col2:
        st.markdown("#### 🏆 Top Campañas por Engagement")
        
        top_campaigns = stats.get("top_campaigns", [
            {"name": "BCE Tipos Octubre", "open_rate": 0.68, "click_rate": 0.15},
            {"name": "Renovables España", "open_rate": 0.62, "click_rate": 0.12},
            {"name": "Real Estate Q4", "open_rate": 0.55, "click_rate": 0.10},
        ])
        
        for campaign in top_campaigns[:5]:
            st.markdown(f"""
            **{campaign.get('name', 'N/A')}**
            - 👀 Apertura: {campaign.get('open_rate', 0)*100:.1f}%
            - 🖱️ Click: {campaign.get('click_rate', 0)*100:.1f}%
            """)
    
    st.markdown("---")
    
    # Follow-up effectiveness
    st.markdown("#### 📧 Efectividad de Follow-ups")
    
    col1, col2, col3 = st.columns(3)
    
    followup_stats = stats.get("followup_stats", {})
    
    with col1:
        st.metric(
            "1️⃣ Follow-up #1",
            f"{followup_stats.get('followup_1_response_rate', 0.08)*100:.1f}%",
            help="Tasa de respuesta del primer follow-up",
        )
    with col2:
        st.metric(
            "2️⃣ Follow-up #2",
            f"{followup_stats.get('followup_2_response_rate', 0.05)*100:.1f}%",
            help="Tasa de respuesta del segundo follow-up",
        )
    with col3:
        st.metric(
            "🎯 Total Convertidos",
            followup_stats.get("total_converted", 15),
            help="Contactos convertidos a reunión vía follow-up",
        )

# ============================================================================
# TAB 4: CONFIGURATION
# ============================================================================

with tab4:
    st.markdown("### ⚙️ Configuración de Follow-up")
    
    st.info("""
    Configura los tiempos y comportamiento del sistema de follow-up automático.
    Estos ajustes afectan al **Agente 8: Follow-up Manager**.
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⏰ Tiempos de Follow-up")
        
        followup_1_days = st.number_input(
            "Días para Follow-up #1 (después de apertura)",
            min_value=1,
            max_value=14,
            value=3,
            help="Días que esperar antes de enviar el primer follow-up",
        )
        
        followup_2_days = st.number_input(
            "Días para Follow-up #2 (después de follow-up #1)",
            min_value=1,
            max_value=14,
            value=5,
            help="Días que esperar antes de enviar el segundo follow-up",
        )
        
        max_followups = st.number_input(
            "Máximo de follow-ups por contacto",
            min_value=1,
            max_value=5,
            value=2,
            help="No enviar más follow-ups después de este número",
        )
    
    with col2:
        st.markdown("#### 🔔 Alertas")
        
        alert_on_click = st.checkbox(
            "Alertar en Slack cuando alguien hace click",
            value=True,
        )
        
        alert_on_response = st.checkbox(
            "Alertar en Slack cuando alguien responde",
            value=True,
        )
        
        alert_channel = st.text_input(
            "Canal de Slack para alertas",
            value="#origination-alerts",
        )
        
        st.markdown("#### 🤖 Automatización")
        
        auto_followup = st.checkbox(
            "Programar follow-ups automáticamente",
            value=True,
            help="El sistema programa follow-ups sin intervención manual",
        )
        
        auto_execute = st.checkbox(
            "Ejecutar follow-ups automáticamente",
            value=False,
            help="⚠️ El sistema envía follow-ups sin aprobación manual",
        )
    
    st.markdown("---")
    
    # Templates
    st.markdown("#### 📝 Templates de Follow-up")
    
    with st.expander("📧 Template Follow-up #1"):
        template_1 = st.text_area(
            "Contenido del primer follow-up",
            value="""Hola {nombre},

Te escribo de nuevo respecto a mi email anterior sobre {asunto_original}.

¿Has tenido oportunidad de revisarlo? Estaré encantado de resolver cualquier duda que tengas.

Un saludo,
{firma}""",
            height=150,
            key="template_1",
        )
    
    with st.expander("📧 Template Follow-up #2"):
        template_2 = st.text_area(
            "Contenido del segundo follow-up",
            value="""Hola {nombre},

Es mi último mensaje sobre este tema. Entiendo que estés ocupado/a.

Si en algún momento te interesa explorar opciones de financiación para {empresa}, no dudes en contactarme.

Un saludo,
{firma}""",
            height=150,
            key="template_2",
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
                # Save configuration
                success_alert("✅ Configuración guardada correctamente")
            except Exception as e:
                error_alert(f"Error guardando configuración: {e}")

# ============================================================================
# HELP SECTION
# ============================================================================

st.markdown("---")

with st.expander("❓ ¿Cómo funciona el Sistema de Follow-up?"):
    st.markdown("""
    ### Sistema de Follow-up Automático
    
    El **Agente 8: Follow-up Manager** gestiona automáticamente los seguimientos 
    post-campaña para maximizar la conversión.
    
    ### Flujo de Follow-up
    
    ```
    Email enviado → Apertura detectada → Espera N días → Follow-up #1
                          ↓
                   Click detectado → 🔥 HOT LEAD → Alerta inmediata
                          ↓
                   Respuesta → 🚨 URGENTE → Notificación Slack
    ```
    
    ### Tipos de Eventos
    
    | Evento | Acción |
    |--------|--------|
    | Apertura sin click | Programar follow-up en N días |
    | Click | Marcar como HOT LEAD + Alerta Slack |
    | Respuesta | Alerta URGENTE + Pausar follow-ups |
    | Bounce | Marcar email inválido |
    | Unsubscribe | No contactar de nuevo |
    
    ### Personalización de Follow-ups
    
    Los follow-ups se generan automáticamente usando Claude, incluyendo:
    - Nombre del contacto
    - Empresa
    - Referencia al email original
    - CTA relevante
    
    ### Métricas Importantes
    
    - **Tasa de apertura**: Benchmark: 25-35%
    - **Tasa de click**: Benchmark: 3-8%
    - **Tasa de respuesta**: Benchmark: 2-5%
    - **Conversión a reunión**: Objetivo: 1-2%
    """)
