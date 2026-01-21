"""Custom CSS styles for Alter-5 Origination Engine frontend."""

import streamlit as st


def inject_custom_css() -> None:
    """Inject custom CSS styles into Streamlit app."""
    css = """
    <style>
        /* ===== Variables de color ===== */
        :root {
            --primary: #1E40AF;
            --primary-light: #3B82F6;
            --primary-dark: #1E3A8A;
            --success: #10B981;
            --success-light: #D1FAE5;
            --success-dark: #065F46;
            --warning: #F59E0B;
            --warning-light: #FEF3C7;
            --warning-dark: #92400E;
            --error: #EF4444;
            --error-light: #FEE2E2;
            --error-dark: #991B1B;
            --info: #3B82F6;
            --gray-50: #F9FAFB;
            --gray-100: #F3F4F6;
            --gray-200: #E5E7EB;
            --gray-300: #D1D5DB;
            --gray-400: #9CA3AF;
            --gray-500: #6B7280;
            --gray-600: #4B5563;
            --gray-700: #374151;
            --gray-800: #1F2937;
            --gray-900: #111827;
        }
        
        /* ===== Ocultar elementos de Streamlit ===== */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        /* Hide default multipage navigation */
        section[data-testid="stSidebarNav"] {display: none;}
        div[data-testid="stSidebarNav"] {display: none;}
        
        /* ===== Tipografía ===== */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-weight: 600;
            color: var(--gray-900);
        }
        
        /* ===== Metric Cards ===== */
        .metric-card {
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid var(--gray-200);
            text-align: center;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        }
        
        .metric-card .icon {
            font-size: 2rem;
            display: block;
            margin-bottom: 8px;
        }
        
        .metric-card h3 {
            font-size: 0.875rem;
            color: var(--gray-500);
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .metric-card h1 {
            font-size: 2.5rem;
            color: var(--primary);
            margin: 8px 0;
            font-weight: 700;
        }
        
        .metric-card p {
            font-size: 0.875rem;
            color: var(--gray-500);
            margin: 0;
        }
        
        /* ===== Botones ===== */
        .stButton > button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s;
        }
        
        .stButton > button[kind="primary"] {
            background-color: var(--primary);
            color: white;
            border: none;
            padding: 12px 24px;
        }
        
        .stButton > button[kind="primary"]:hover {
            background-color: var(--primary-light);
            transform: translateY(-1px);
        }
        
        .stButton > button[kind="secondary"] {
            background-color: white;
            color: var(--gray-700);
            border: 1px solid var(--gray-300);
        }
        
        .stButton > button[kind="secondary"]:hover {
            background-color: var(--gray-50);
            border-color: var(--gray-400);
        }
        
        /* ===== FEI Status Badges ===== */
        .fei-badge {
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
        }
        
        .fei-eligible {
            background-color: var(--success-light);
            color: var(--success-dark);
        }
        
        .fei-not-eligible {
            background-color: var(--error-light);
            color: var(--error-dark);
        }
        
        .fei-partial {
            background-color: var(--warning-light);
            color: var(--warning-dark);
        }
        
        .fei-unknown {
            background-color: var(--gray-100);
            color: var(--gray-600);
        }
        
        /* ===== Wizard Progress ===== */
        .wizard-container {
            background: white;
            padding: 32px;
            border-radius: 16px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            margin-bottom: 24px;
        }
        
        .wizard-step {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            border-radius: 8px;
        }
        
        .wizard-step.completed {
            color: var(--success);
        }
        
        .wizard-step.current {
            color: var(--primary);
            font-weight: 600;
            background-color: var(--gray-50);
        }
        
        .wizard-step.pending {
            color: var(--gray-400);
        }
        
        /* ===== Campaign Cards ===== */
        .campaign-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid var(--gray-200);
            margin-bottom: 12px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .campaign-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-color: var(--primary-light);
        }
        
        .campaign-card h4 {
            margin: 0 0 8px 0;
            color: var(--gray-900);
        }
        
        .campaign-card .meta {
            font-size: 0.875rem;
            color: var(--gray-500);
        }
        
        /* ===== Tables ===== */
        .dataframe {
            border-radius: 8px;
            overflow: hidden;
        }
        
        .dataframe th {
            background-color: var(--gray-50) !important;
            font-weight: 600;
            color: var(--gray-700);
        }
        
        .dataframe td {
            border-bottom: 1px solid var(--gray-100);
        }
        
        /* ===== Form Elements ===== */
        .stTextInput > div > div > input {
            border-radius: 8px;
            border: 1px solid var(--gray-300);
        }
        
        .stTextInput > div > div > input:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
        }
        
        .stTextArea > div > div > textarea {
            border-radius: 8px;
            border: 1px solid var(--gray-300);
        }
        
        .stTextArea > div > div > textarea:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
        }
        
        .stSelectbox > div > div {
            border-radius: 8px;
        }
        
        /* ===== Sidebar ===== */
        section[data-testid="stSidebar"] {
            background-color: white;
            border-right: 1px solid var(--gray-200);
        }
        
        section[data-testid="stSidebar"] .stMarkdown h1 {
            font-size: 1.25rem;
            color: var(--primary);
        }
        
        /* ===== Alerts ===== */
        .stAlert {
            border-radius: 8px;
        }
        
        /* ===== Empty State ===== */
        .empty-state {
            text-align: center;
            padding: 48px;
            color: var(--gray-500);
        }
        
        .empty-state .icon {
            font-size: 4rem;
            display: block;
            margin-bottom: 16px;
        }
        
        .empty-state h3 {
            color: var(--gray-700);
            margin-bottom: 8px;
        }
        
        .empty-state p {
            margin-bottom: 24px;
        }
        
        /* ===== Hero Section ===== */
        .hero-section {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
            padding: 32px;
            border-radius: 16px;
            color: white;
            margin-bottom: 24px;
        }
        
        .hero-section h2 {
            color: white;
            margin: 0 0 16px 0;
        }
        
        .hero-section p {
            opacity: 0.9;
            margin-bottom: 24px;
        }
        
        /* ===== Quick Action Box ===== */
        .quick-action {
            background: white;
            padding: 24px;
            border-radius: 12px;
            border: 2px solid var(--primary);
            margin-bottom: 24px;
        }
        
        .quick-action h3 {
            color: var(--primary);
            margin: 0 0 16px 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        /* ===== Responsive adjustments ===== */
        @media (max-width: 768px) {
            .metric-card {
                padding: 16px;
            }
            
            .metric-card h1 {
                font-size: 1.75rem;
            }
            
            .wizard-container {
                padding: 20px;
            }
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def fei_status_badge(status: str) -> str:
    """Return HTML for FEI status badge."""
    status_config = {
        "Eligible": ("✅", "fei-eligible", "Eligible"),
        "Not_Eligible": ("❌", "fei-not-eligible", "Not Eligible"),
        "Partially_Eligible": ("🟡", "fei-partial", "Partial"),
        "Pending_Review": ("🔍", "fei-unknown", "Pending"),
        "Unknown": ("⬜", "fei-unknown", "Unknown"),
        "Expired": ("⏰", "fei-unknown", "Expired"),
    }
    
    emoji, css_class, label = status_config.get(status, ("❓", "fei-unknown", status))
    
    return f'<span class="fei-badge {css_class}">{emoji} {label}</span>'

