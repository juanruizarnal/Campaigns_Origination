"""Metric display components for Streamlit frontend.

Provides reusable metric cards and displays.
"""

import streamlit as st
from typing import Optional


def metric_card(
    title: str,
    value: str,
    subtitle: str = "",
    icon: str = "📊",
    color: str = "#1E40AF",
) -> None:
    """Display a styled metric card.
    
    Args:
        title: Card title
        value: Main value to display
        subtitle: Optional subtitle
        icon: Emoji icon
        color: Main color for value
    """
    st.markdown(f"""
    <div style="
        background: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        text-align: center;
    ">
        <span style="font-size: 2rem;">{icon}</span>
        <h4 style="color: #6B7280; margin: 8px 0 4px 0;">{title}</h4>
        <h1 style="color: {color}; margin: 0;">{value}</h1>
        {f'<p style="color: #9CA3AF; margin: 4px 0 0 0; font-size: 0.875rem;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def metric_row(
    metrics: list,
) -> None:
    """Display a row of metrics.
    
    Args:
        metrics: List of metric dicts with title, value, icon, etc.
    """
    cols = st.columns(len(metrics))
    
    for col, metric in zip(cols, metrics):
        with col:
            metric_card(
                title=metric.get("title", ""),
                value=str(metric.get("value", "")),
                subtitle=metric.get("subtitle", ""),
                icon=metric.get("icon", "📊"),
                color=metric.get("color", "#1E40AF"),
            )


def fei_distribution_bar(
    eligible: int = 0,
    not_eligible: int = 0,
    partial: int = 0,
    unknown: int = 0,
) -> None:
    """Display FEI status distribution bar.
    
    Args:
        eligible: Count of eligible
        not_eligible: Count of not eligible
        partial: Count of partial
        unknown: Count of unknown
    """
    total = eligible + not_eligible + partial + unknown
    
    if total == 0:
        st.info("No hay datos de distribución FEI")
        return
    
    pct_eligible = (eligible / total * 100)
    pct_not_eligible = (not_eligible / total * 100)
    pct_partial = (partial / total * 100)
    pct_unknown = (unknown / total * 100)
    
    # Ensure minimum width
    bar_eligible = max(pct_eligible, 0.5) if eligible > 0 else 0
    bar_not_eligible = max(pct_not_eligible, 0.5) if not_eligible > 0 else 0
    bar_partial = max(pct_partial, 0.5) if partial > 0 else 0
    bar_unknown = max(pct_unknown, 0.5) if unknown > 0 else 0
    
    st.markdown(f"""
    <div style="display: flex; height: 40px; border-radius: 8px; overflow: hidden; margin-bottom: 8px;">
        <div style="width: {bar_eligible}%; background: #10B981; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 0.75rem;">
            {eligible if pct_eligible > 8 else ''}
        </div>
        <div style="width: {bar_not_eligible}%; background: #EF4444; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 0.75rem;">
            {not_eligible if pct_not_eligible > 8 else ''}
        </div>
        <div style="width: {bar_partial}%; background: #F59E0B; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 0.75rem;">
            {partial if pct_partial > 8 else ''}
        </div>
        <div style="width: {bar_unknown}%; background: #6B7280; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 0.75rem;">
            {unknown if pct_unknown > 8 else ''}
        </div>
    </div>
    <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #6B7280;">
        <span>✅ Eligible ({pct_eligible:.1f}%)</span>
        <span>❌ Not Eligible ({pct_not_eligible:.1f}%)</span>
        <span>⚠️ Partial ({pct_partial:.1f}%)</span>
        <span>❓ Unknown ({pct_unknown:.1f}%)</span>
    </div>
    """, unsafe_allow_html=True)


def campaign_stats(
    total_targets: int = 0,
    fei_eligible: int = 0,
    emails_sent: int = 0,
    avg_fit_score: float = 0.0,
) -> None:
    """Display campaign statistics.
    
    Args:
        total_targets: Total number of targets
        fei_eligible: Number of FEI eligible targets
        emails_sent: Number of emails sent
        avg_fit_score: Average fit score
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Targets", total_targets)
    
    with col2:
        fei_pct = (fei_eligible / total_targets * 100) if total_targets > 0 else 0
        st.metric("🏷️ FEI Eligible", f"{fei_eligible} ({fei_pct:.0f}%)")
    
    with col3:
        st.metric("📧 Emails", emails_sent)
    
    with col4:
        st.metric("📊 Avg Score", f"{avg_fit_score:.0%}")
