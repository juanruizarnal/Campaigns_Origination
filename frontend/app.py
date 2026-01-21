"""Main entry point for Alter-5 Origination Engine Streamlit application.

This application provides a user-friendly interface for the commercial team
to create campaigns, evaluate FEI eligibility, and manage company data.

Usage:
    streamlit run frontend/app.py
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="Alter-5 Origination",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "Motor de Originación Alter-5 v1.0\n\nHerramienta de automatización para el equipo comercial.",
    }
)

# Import and inject custom CSS
from utils.styles import inject_custom_css
from components.sidebar import render_sidebar
inject_custom_css()
render_sidebar()

# Main page content - redirect to Dashboard
st.markdown("""
<div style="text-align: center; padding: 48px;">
    <h1>🚀 Bienvenido a Alter-5 Origination</h1>
    <p style="color: #6B7280; font-size: 1.125rem; margin-bottom: 32px;">
        Motor de automatización de originación de campañas
    </p>
</div>
""", unsafe_allow_html=True)

# Quick navigation cards (only Empresas + Campañas)
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="metric-card" style="cursor: pointer;">
        <span class="icon">🏢</span>
        <h3>EMPRESAS</h3>
        <p>Gestión de empresas: búsqueda y enriquecimiento</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ir a Empresas →", key="btn_empresas", use_container_width=True, type="primary"):
        st.switch_page("pages/2_🏢_Empresas.py")

with col2:
    st.markdown("""
    <div class="metric-card" style="cursor: pointer;">
        <span class="icon">📋</span>
        <h3>CAMPAÑAS</h3>
        <p>Listado y gestión de campañas activas</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ir a Campañas →", key="btn_campanas", use_container_width=True):
        st.switch_page("pages/5_📋_Campañas.py")

# Footer
st.markdown("""
<div style="text-align: center; padding: 24px; color: #9CA3AF; font-size: 0.875rem;">
    <p>Motor de Originación Alter-5 v1.0</p>
    <p>© 2026 Alter-5 Capital</p>
</div>
""", unsafe_allow_html=True)

