"""Sidebar navigation component for Alter-5 Origination Engine frontend."""

import streamlit as st
from typing import Optional


def render_sidebar() -> str:
    """Render the sidebar navigation.
    
    Returns:
        Name of the selected page
    """
    with st.sidebar:
        # Logo / Title
        st.markdown("""
        <div style="text-align: center; padding: 16px 0;">
            <h1 style="font-size: 1.5rem; color: #1E40AF; margin: 0;">🚀 ALTER-5</h1>
            <p style="color: #6B7280; font-size: 0.875rem; margin: 4px 0 0 0;">Origination Engine</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation menu
        st.markdown("### Navegación")
        
        # Using native Streamlit navigation
        # Pages are handled by Streamlit's multipage app feature
        
        st.markdown("""
        <div style="font-size: 0.875rem; color: #6B7280; padding: 8px 0;">
            <p>🏢 <a href="/Empresas" target="_self" style="color: inherit; text-decoration: none;">Empresas</a></p>
            <p>📋 <a href="/Campañas" target="_self" style="color: inherit; text-decoration: none;">Campañas</a></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### Acciones Rápidas")

        if st.button("🏢 Ver Empresas", use_container_width=True, type="primary"):
            st.switch_page("pages/2_🏢_Empresas.py")

        if st.button("📋 Ver Campañas", use_container_width=True):
            st.switch_page("pages/5_📋_Campañas.py")
        
        st.markdown("---")
        
        # Footer info
        st.markdown("""
        <div style="font-size: 0.75rem; color: #9CA3AF; text-align: center;">
            <p style="margin: 4px 0;">Motor de Originación v1.0</p>
            <p style="margin: 4px 0;">© 2026 Alter-5</p>
        </div>
        """, unsafe_allow_html=True)
    
    return ""


def quick_campaign_input() -> Optional[str]:
    """Render a quick campaign trigger input in sidebar.
    
    Returns:
        Trigger text if submitted, None otherwise
    """
    with st.sidebar:
        st.markdown("### 🚀 Campaña Rápida")
        
        trigger = st.text_area(
            "Trigger de mercado",
            placeholder="Ej: BCE baja tipos...",
            height=80,
            key="sidebar_trigger",
            label_visibility="collapsed",
        )
        
        if st.button("Analizar →", use_container_width=True, type="primary"):
            if trigger:
                # Store in session and navigate
                st.session_state.quick_trigger = trigger
                st.switch_page("pages/3_🚀_Nueva_Campaña.py")
                return trigger
            else:
                st.warning("Escribe un trigger primero")
        
        return None


def show_user_info(username: str = "Usuario") -> None:
    """Show user info in sidebar.
    
    Args:
        username: Username to display
    """
    with st.sidebar:
        st.markdown("---")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown("""
            <div style="
                width: 32px;
                height: 32px;
                background: #1E40AF;
                color: white;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
            ">
                {}
            </div>
            """.format(username[0].upper()), unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"**{username}**")
            st.caption("Equipo Comercial")

