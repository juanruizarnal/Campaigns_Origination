"""Form input components for Streamlit frontend.

Provides reusable form fields with consistent styling.
"""

import streamlit as st
from typing import List, Optional, Dict
from utils.helpers import (
    get_sector_options,
    get_country_options,
    get_fei_status_options,
    parse_keywords,
)


def sector_select(
    label: str = "Sector",
    default: str = None,
    key: str = None,
    required: bool = False,
) -> Optional[str]:
    """Sector selection dropdown.
    
    Args:
        label: Field label
        default: Default value
        key: Streamlit key
        required: Whether field is required
        
    Returns:
        Selected sector or None
    """
    options = [""] + get_sector_options()
    
    label_text = f"{label} *" if required else label
    
    selected = st.selectbox(
        label_text,
        options=options,
        index=options.index(default) if default in options else 0,
        key=key,
    )
    
    return selected if selected else None


def sector_multiselect(
    label: str = "Sectores",
    default: List[str] = None,
    key: str = None,
) -> List[str]:
    """Multi-sector selection.
    
    Args:
        label: Field label
        default: Default values
        key: Streamlit key
        
    Returns:
        List of selected sectors
    """
    options = get_sector_options()
    
    return st.multiselect(
        label,
        options=options,
        default=default or [],
        key=key,
    )


def country_select(
    label: str = "País",
    default: str = "ES",
    key: str = None,
    required: bool = False,
) -> Optional[str]:
    """Country selection dropdown.
    
    Args:
        label: Field label
        default: Default country code
        key: Streamlit key
        required: Whether field is required
        
    Returns:
        Selected country code or None
    """
    options = get_country_options()
    codes = [c[0] for c in options]
    labels = [c[1] for c in options]
    
    label_text = f"{label} *" if required else label
    
    # Add empty option
    codes = [""] + codes
    labels = ["Todos"] + labels
    
    selected_idx = st.selectbox(
        label_text,
        options=range(len(codes)),
        format_func=lambda i: labels[i],
        index=codes.index(default) if default in codes else 0,
        key=key,
    )
    
    return codes[selected_idx] if selected_idx > 0 else None


def country_multiselect(
    label: str = "Países",
    default: List[str] = None,
    key: str = None,
) -> List[str]:
    """Multi-country selection.
    
    Args:
        label: Field label
        default: Default country codes
        key: Streamlit key
        
    Returns:
        List of selected country codes
    """
    options = get_country_options()
    
    # Create display labels and track selections
    code_to_label = {c[0]: c[1] for c in options}
    
    selected_labels = st.multiselect(
        label,
        options=[c[1] for c in options],
        default=[code_to_label.get(d, d) for d in (default or []) if d in code_to_label],
        key=key,
    )
    
    # Convert back to codes
    label_to_code = {c[1]: c[0] for c in options}
    return [label_to_code[l] for l in selected_labels]


def fei_status_select(
    label: str = "FEI Status",
    default: str = "",
    key: str = None,
) -> Optional[str]:
    """FEI status selection dropdown.
    
    Args:
        label: Field label
        default: Default value
        key: Streamlit key
        
    Returns:
        Selected status or None
    """
    options = get_fei_status_options()
    codes = [o[0] for o in options]
    labels = [o[1] for o in options]
    
    selected_idx = st.selectbox(
        label,
        options=range(len(codes)),
        format_func=lambda i: labels[i],
        index=codes.index(default) if default in codes else 0,
        key=key,
    )
    
    return codes[selected_idx] if codes[selected_idx] else None


def search_input(
    label: str = "Buscar",
    placeholder: str = "Escribe para buscar...",
    key: str = None,
) -> str:
    """Search text input.
    
    Args:
        label: Field label
        placeholder: Placeholder text
        key: Streamlit key
        
    Returns:
        Search query string
    """
    return st.text_input(
        label,
        placeholder=placeholder,
        key=key,
        label_visibility="collapsed",
    )


def trigger_input(
    label: str = "Trigger de mercado",
    placeholder: str = "Ej: El BCE ha bajado los tipos de interés...",
    key: str = None,
    show_examples: bool = False,
) -> str:
    """Market trigger text area.
    
    Args:
        label: Field label
        placeholder: Placeholder text
        key: Streamlit key
        show_examples: Whether to show example triggers
        
    Returns:
        Trigger text
    """
    if show_examples:
        with st.expander("💡 Ver ejemplos de triggers"):
            st.markdown("""
            **Ejemplos de triggers efectivos:**
            
            - *"El BCE ha anunciado una bajada de tipos del 0.25%, facilitando el acceso a financiación para PYMEs industriales."*
            
            - *"Nueva normativa europea obliga a reducir emisiones en transporte un 55% para 2030."*
            
            - *"España aprueba subvenciones de 2.000M€ para renovables en sector agrícola."*
            
            - *"Crisis de suministros afecta a fabricantes de automoción en el sur de Europa."*
            """)
    
    return st.text_area(
        label,
        placeholder=placeholder,
        height=120,
        key=key,
    )


def target_count_slider(
    label: str = "Máximo de targets",
    default: int = 20,
    min_value: int = 5,
    max_value: int = 30,
    key: str = None,
) -> int:
    """Target count slider.
    
    Args:
        label: Field label
        default: Default value
        min_value: Minimum value
        max_value: Maximum value
        key: Streamlit key
        
    Returns:
        Selected target count
    """
    return st.slider(
        label,
        min_value=min_value,
        max_value=max_value,
        value=default,
        key=key,
        help=f"Número máximo de targets para la campaña (máximo permitido: {max_value})",
    )


def fit_score_slider(
    label: str = "Fit score mínimo",
    default: float = 0.6,
    min_value: float = 0.0,
    max_value: float = 1.0,
    key: str = None,
) -> float:
    """Fit score slider.
    
    Args:
        label: Field label
        default: Default value
        min_value: Minimum value
        max_value: Maximum value
        key: Streamlit key
        
    Returns:
        Selected fit score
    """
    return st.slider(
        label,
        min_value=min_value,
        max_value=max_value,
        value=default,
        step=0.05,
        format="%.0f%%",
        key=key,
        help="Score mínimo de relevancia para incluir un target",
    )


def limit_slider(
    label: str = "Límite",
    default: int = 25,
    min_value: int = 5,
    max_value: int = 100,
    key: str = None,
) -> int:
    """Generic limit slider.
    
    Args:
        label: Field label
        default: Default value
        min_value: Minimum value
        max_value: Maximum value
        key: Streamlit key
        
    Returns:
        Selected limit
    """
    return st.slider(
        label,
        min_value=min_value,
        max_value=max_value,
        value=default,
        key=key,
    )


def region_input(
    label: str = "Región",
    placeholder: str = "Ej: Cataluña, Madrid",
    key: str = None,
) -> str:
    """Region text input.
    
    Args:
        label: Field label
        placeholder: Placeholder text
        key: Streamlit key
        
    Returns:
        Region string
    """
    return st.text_input(
        label,
        placeholder=placeholder,
        key=key,
    )


def keywords_input(
    label: str = "Palabras clave",
    placeholder: str = "Ej: renovables, exportación",
    key: str = None,
) -> List[str]:
    """Keywords input (comma separated).
    
    Args:
        label: Field label
        placeholder: Placeholder text
        key: Streamlit key
        
    Returns:
        List of keywords
    """
    keywords_str = st.text_input(
        label,
        placeholder=placeholder,
        key=key,
        help="Separa las palabras clave con comas",
    )
    
    return parse_keywords(keywords_str)


def company_search_form(
    key_prefix: str = "search",
) -> Dict:
    """Complete company search form.
    
    Args:
        key_prefix: Prefix for form field keys
        
    Returns:
        Dict with search parameters
    """
    col1, col2 = st.columns(2)
    
    with col1:
        sector = sector_select(
            label="Sector *",
            key=f"{key_prefix}_sector",
            required=True,
        )
        
        country = country_select(
            label="País *",
            key=f"{key_prefix}_country",
            required=True,
        )
    
    with col2:
        region = region_input(
            label="Región (opcional)",
            key=f"{key_prefix}_region",
        )
        
        keywords = keywords_input(
            label="Palabras clave (opcional)",
            key=f"{key_prefix}_keywords",
        )
    
    col3, col4 = st.columns(2)
    
    with col3:
        min_employees = st.number_input(
            "Empleados mínimos",
            min_value=0,
            value=10,
            key=f"{key_prefix}_min_employees",
        )
    
    with col4:
        limit = limit_slider(
            label="Empresas a buscar",
            default=25,
            min_value=5,
            max_value=50,
            key=f"{key_prefix}_limit",
        )
    
    return {
        "sector": sector,
        "country": country,
        "region": region,
        "keywords": keywords,
        "min_employees": min_employees,
        "limit": limit,
    }
