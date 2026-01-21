"""Table components for Streamlit frontend.

Provides reusable table displays with filtering and selection.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional, Callable

from utils.helpers import get_fei_status_emoji, get_campaign_status_emoji


def company_table(
    companies: List[Dict[str, Any]],
    show_actions: bool = True,
    on_select: Callable = None,
) -> Optional[str]:
    """Display company table.
    
    Args:
        companies: List of company records
        show_actions: Whether to show action column
        on_select: Callback when company is selected
        
    Returns:
        Selected company ID if any
    """
    if not companies:
        st.info("No hay empresas para mostrar")
        return None
    
    # Build dataframe
    data = []
    for company in companies:
        fields = company.get("fields", {})
        
        fei = fields.get("FEI_Status", "Unknown")
        
        data.append({
            "id": company.get("id", ""),
            "Empresa": fields.get("Company Name", "Sin nombre"),
            "Sector": fields.get("Sector", "N/A"),
            "Empleados": fields.get("Num Employees", "N/A"),
            "FEI": f"{get_fei_status_emoji(fei)} {fei}",
        })
    
    df = pd.DataFrame(data)
    
    # Display
    st.dataframe(
        df[["Empresa", "Sector", "Empleados", "FEI"]],
        use_container_width=True,
        hide_index=True,
    )
    
    return None


def target_table(
    targets: List[Dict[str, Any]],
    selectable: bool = False,
    selected_ids: List[str] = None,
    on_selection_change: Callable = None,
) -> List[str]:
    """Display target selection table.
    
    Args:
        targets: List of target dictionaries
        selectable: Whether to allow selection
        selected_ids: Currently selected IDs
        on_selection_change: Callback when selection changes
        
    Returns:
        List of selected target IDs
    """
    if not targets:
        st.info("No hay targets para mostrar")
        return []
    
    selected_ids = selected_ids or []
    
    # Build dataframe
    data = []
    for target in targets:
        fei = target.get("fei_status", "Unknown")
        score = target.get("fit_score", 0)
        
        data.append({
            "id": target.get("id", ""),
            "Seleccionar": target.get("id") in selected_ids,
            "Empresa": target.get("company_name", "Sin nombre"),
            "Sector": target.get("sector", "N/A"),
            "Fit Score": f"{score:.0%}" if isinstance(score, (int, float)) else "N/A",
            "FEI": f"{get_fei_status_emoji(fei)} {fei}",
        })
    
    df = pd.DataFrame(data)
    
    if selectable:
        # Use data editor for selection
        edited_df = st.data_editor(
            df,
            column_config={
                "id": st.column_config.Column(width=0),  # Hidden
                "Seleccionar": st.column_config.CheckboxColumn(
                    "✓",
                    help="Seleccionar para incluir en campaña",
                    default=True,
                    width="small",
                ),
                "Empresa": st.column_config.TextColumn(width="large"),
                "Sector": st.column_config.TextColumn(width="medium"),
                "Fit Score": st.column_config.TextColumn(width="small"),
                "FEI": st.column_config.TextColumn(width="medium"),
            },
            disabled=["id", "Empresa", "Sector", "Fit Score", "FEI"],
            hide_index=True,
            use_container_width=True,
            key="target_selection_editor",
        )
        
        # Get selected IDs
        new_selected = edited_df[edited_df["Seleccionar"]]["id"].tolist()
        
        if on_selection_change and new_selected != selected_ids:
            on_selection_change(new_selected)
        
        return new_selected
    else:
        # Display only
        st.dataframe(
            df[["Empresa", "Sector", "Fit Score", "FEI"]],
            use_container_width=True,
            hide_index=True,
        )
        return selected_ids


def campaign_table(
    campaigns: List[Dict[str, Any]],
    on_select: Callable = None,
) -> Optional[str]:
    """Display campaign table.
    
    Args:
        campaigns: List of campaign records
        on_select: Callback when campaign is selected
        
    Returns:
        Selected campaign ID if any
    """
    if not campaigns:
        st.info("No hay campañas para mostrar")
        return None
    
    # Build dataframe
    data = []
    for campaign in campaigns:
        fields = campaign.get("fields", {})
        
        status = fields.get("Status", "Draft")
        
        data.append({
            "id": campaign.get("id", ""),
            "Campaña": fields.get("Campaign_Name", "Sin nombre"),
            "Estado": f"{get_campaign_status_emoji(status)} {status.replace('_', ' ')}",
            "Prioridad": fields.get("Priority", "Medium"),
        })
    
    df = pd.DataFrame(data)
    
    # Display
    st.dataframe(
        df[["Campaña", "Estado", "Prioridad"]],
        use_container_width=True,
        hide_index=True,
    )
    
    return None


def news_table(
    news_items: List[Dict[str, Any]],
    selectable: bool = False,
    selected_id: str = None,
    on_select: Callable = None,
) -> Optional[str]:
    """Display news/market context table.
    
    Args:
        news_items: List of news items
        selectable: Whether to allow selection
        selected_id: Currently selected ID
        on_select: Callback when news is selected
        
    Returns:
        Selected news ID if any
    """
    if not news_items:
        st.info("No hay noticias para mostrar")
        return None
    
    for item in news_items:
        fields = item.get("fields", {}) if isinstance(item, dict) else {}
        item_id = item.get("id", "") if isinstance(item, dict) else ""
        
        title = fields.get("Context_Title", "Sin título")
        source = fields.get("Source_Name", "Desconocido")
        potential = fields.get("Campaign_Potential", 0)
        
        is_selected = item_id == selected_id
        
        # Card style
        border_color = "#1E40AF" if is_selected else "#E5E7EB"
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"""
            <div style="
                background: white;
                padding: 16px;
                border-radius: 8px;
                border: 2px solid {border_color};
                margin-bottom: 8px;
            ">
                <h4 style="margin: 0;">{title}</h4>
                <p style="color: #6B7280; margin: 8px 0 0 0; font-size: 0.875rem;">
                    📰 {source} | ⭐ Potencial: {potential}/5
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if selectable:
                if st.button("Seleccionar" if not is_selected else "✓ Seleccionado", 
                           key=f"select_news_{item_id}",
                           type="primary" if is_selected else "secondary"):
                    if on_select:
                        on_select(item_id)
                    return item_id
    
    return selected_id
