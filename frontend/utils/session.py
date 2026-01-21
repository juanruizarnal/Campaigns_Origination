"""Session state management for Streamlit frontend.

Provides wizard state management for multi-step processes.
"""

import streamlit as st
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class WizardState:
    """State for campaign creation wizard."""
    step: int = 1
    mode: str = "trigger"  # "trigger", "companies", "news"
    
    # Trigger mode
    trigger: str = ""
    analysis: Optional[Dict[str, Any]] = None
    
    # Configuration
    sectors: List[str] = field(default_factory=list)
    countries: List[str] = field(default_factory=list)
    max_targets: int = 20
    min_fit_score: float = 0.6
    prioritize_fei: bool = True
    
    # Targets
    targets: List[Dict[str, Any]] = field(default_factory=list)
    selected_target_ids: List[str] = field(default_factory=list)
    
    # Campaign result
    campaign_id: Optional[str] = None
    messages_result: Optional[Dict[str, Any]] = None
    
    # Company mode
    company_ids: List[str] = field(default_factory=list)
    
    # News mode
    news_items: List[Dict[str, Any]] = field(default_factory=list)
    selected_news_id: Optional[str] = None


def get_wizard_state() -> WizardState:
    """Get or create wizard state from session.
    
    Returns:
        Current wizard state
    """
    if "wizard_state" not in st.session_state:
        st.session_state.wizard_state = WizardState()
    return st.session_state.wizard_state


def reset_wizard() -> None:
    """Reset wizard state to initial values."""
    st.session_state.wizard_state = WizardState()


def update_wizard(**kwargs) -> WizardState:
    """Update wizard state with new values.
    
    Args:
        **kwargs: Fields to update
        
    Returns:
        Updated wizard state
    """
    wizard = get_wizard_state()
    for key, value in kwargs.items():
        if hasattr(wizard, key):
            setattr(wizard, key, value)
    return wizard


def set_wizard_step(step: int) -> WizardState:
    """Set wizard step.
    
    Args:
        step: Step number (1-indexed)
        
    Returns:
        Updated wizard state
    """
    wizard = get_wizard_state()
    wizard.step = step
    return wizard


def set_wizard_mode(mode: str) -> WizardState:
    """Set wizard mode.
    
    Args:
        mode: Mode ("trigger", "companies", "news")
        
    Returns:
        Updated wizard state
    """
    wizard = get_wizard_state()
    wizard.mode = mode
    wizard.step = 1  # Reset to step 1 when changing mode
    return wizard
