"""Feedback and progress components for Streamlit frontend.

Provides loading, alerts, progress, and status indicators.
"""

import streamlit as st
from typing import Optional, Callable, List


def loading_spinner(message: str = "Procesando..."):
    """Context manager for loading spinner.
    
    Args:
        message: Message to display while loading
        
    Returns:
        Streamlit spinner context manager
    """
    return st.spinner(message)


def success_alert(message: str) -> None:
    """Display success alert.
    
    Args:
        message: Success message
    """
    st.success(f"✅ {message}")


def error_alert(message: str) -> None:
    """Display error alert.
    
    Args:
        message: Error message
    """
    st.error(f"❌ {message}")


def warning_alert(message: str) -> None:
    """Display warning alert.
    
    Args:
        message: Warning message
    """
    st.warning(f"⚠️ {message}")


def info_alert(message: str) -> None:
    """Display info alert.
    
    Args:
        message: Info message
    """
    st.info(f"ℹ️ {message}")


def progress_with_status(
    total: int,
    current: int,
    message: str = "",
) -> None:
    """Display progress bar with status message.
    
    Args:
        total: Total items
        current: Current item
        message: Status message
    """
    progress = current / total if total > 0 else 0
    st.progress(progress)
    st.caption(f"{message} ({current}/{total})")


def step_indicator(
    current_step: int,
    total_steps: int,
    labels: List[str] = None,
) -> None:
    """Display step indicator for wizard.
    
    Args:
        current_step: Current step number (1-indexed)
        total_steps: Total number of steps
        labels: Optional list of step labels
    """
    if labels is None:
        labels = [f"Paso {i+1}" for i in range(total_steps)]
    
    # Ensure we have enough labels
    while len(labels) < total_steps:
        labels.append(f"Paso {len(labels)+1}")
    
    cols = st.columns(total_steps)
    
    for i, (col, label) in enumerate(zip(cols, labels[:total_steps])):
        step_num = i + 1
        with col:
            if step_num < current_step:
                # Completed
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="
                        width: 32px;
                        height: 32px;
                        border-radius: 50%;
                        background: #10B981;
                        color: white;
                        display: inline-flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: 600;
                    ">✓</div>
                    <p style="margin: 8px 0 0 0; font-size: 0.75rem; color: #10B981;">{label}</p>
                </div>
                """, unsafe_allow_html=True)
            elif step_num == current_step:
                # Current
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="
                        width: 32px;
                        height: 32px;
                        border-radius: 50%;
                        background: #1E40AF;
                        color: white;
                        display: inline-flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: 600;
                    ">{step_num}</div>
                    <p style="margin: 8px 0 0 0; font-size: 0.75rem; color: #1E40AF; font-weight: 600;">{label}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Pending
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="
                        width: 32px;
                        height: 32px;
                        border-radius: 50%;
                        background: #E5E7EB;
                        color: #6B7280;
                        display: inline-flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: 600;
                    ">{step_num}</div>
                    <p style="margin: 8px 0 0 0; font-size: 0.75rem; color: #9CA3AF;">{label}</p>
                </div>
                """, unsafe_allow_html=True)


def confirm_dialog(
    message: str,
    confirm_text: str = "Confirmar",
    cancel_text: str = "Cancelar",
) -> Optional[bool]:
    """Display confirmation dialog.
    
    Args:
        message: Confirmation message
        confirm_text: Text for confirm button
        cancel_text: Text for cancel button
        
    Returns:
        True if confirmed, False if cancelled, None if no action
    """
    st.warning(message)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(cancel_text, use_container_width=True):
            return False
    
    with col2:
        if st.button(confirm_text, type="primary", use_container_width=True):
            return True
    
    return None


def empty_state(
    icon: str,
    title: str,
    message: str,
    action_label: str = None,
    action_callback: Callable = None,
) -> None:
    """Display empty state with icon, message, and optional action.
    
    Args:
        icon: Emoji icon
        title: Title text
        message: Description message
        action_label: Optional button label
        action_callback: Optional callback for button
    """
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 48px;
        background: #F9FAFB;
        border-radius: 12px;
        border: 2px dashed #E5E7EB;
    ">
        <span style="font-size: 4rem;">{icon}</span>
        <h3 style="margin: 16px 0 8px 0; color: #374151;">{title}</h3>
        <p style="color: #6B7280; margin: 0;">{message}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if action_label:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(action_label, type="primary", use_container_width=True):
                if action_callback:
                    action_callback()


def toast_message(message: str, icon: str = "✅") -> None:
    """Display toast notification.
    
    Args:
        message: Toast message
        icon: Emoji icon
    """
    st.toast(f"{icon} {message}")


def status_badge(
    status: str,
    color: str = None,
) -> str:
    """Generate HTML for status badge.
    
    Args:
        status: Status text
        color: Optional custom color
        
    Returns:
        HTML string for badge
    """
    # Default colors based on common statuses
    default_colors = {
        "success": "#10B981",
        "error": "#EF4444",
        "warning": "#F59E0B",
        "info": "#3B82F6",
        "pending": "#6B7280",
    }
    
    badge_color = color or default_colors.get(status.lower(), "#6B7280")
    
    return f"""
    <span style="
        background: {badge_color}15;
        color: {badge_color};
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
    ">{status}</span>
    """
