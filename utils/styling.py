import streamlit as st
import pandas as pd

def inject_custom_css() -> None:
    """
    Inject custom CSS rules to override Streamlit defaults and establish a
    consistent design system with an indigo/purple theme.
    """
    css_code = """
    <style>
    /* Styling for Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        background-color: #f3f4f6;
        border-radius: 6px 6px 0px 0px;
        padding-left: 20px;
        padding-right: 20px;
        color: #4b5563;
        font-weight: 500;
        border: 1px solid #e5e7eb;
        transition: all 0.2s ease-in-out;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e5e7eb;
        color: #1f2937;
    }
    .stTabs [aria-selected="true"] {
        background-color: #6366f1 !important;
        color: white !important;
        font-weight: bold;
        border: 1px solid #6366f1 !important;
        box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.2);
    }
    
    /* Primary buttons customization */
    div.stButton > button:first-child {
        background-color: #6366f1;
        color: white;
        border-radius: 6px;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #4f46e5;
        color: white;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }
    div.stButton > button:first-child:active {
        transform: translateY(1px);
    }
    
    /* Custom KPI Cards */
    .kpi-card {
        background-color: #1f2937;
        padding: 22px 15px;
        border-radius: 10px;
        border-left: 4px solid #8b5cf6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        text-align: center;
        margin-bottom: 12px;
        transition: transform 0.2s ease-in-out;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
    }
    .kpi-card.pass {
        border-left-color: #10b981;
    }
    .kpi-card.warning {
        border-left-color: #f59e0b;
    }
    .kpi-card.fail {
        border-left-color: #ef4444;
    }
    .kpi-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #9ca3af;
        margin-bottom: 8px;
        font-weight: 600;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #ffffff;
    }
    
    /* Top horizontal gradient line */
    .accent-divider {
        height: 6px;
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        border-radius: 3px;
        margin-bottom: 24px;
        margin-top: 6px;
    }
    
    /* Title and Subtitle styling */
    .app-title {
        color: #6366f1;
        font-weight: 800;
        font-size: 2.6rem;
        margin-bottom: 4px;
        letter-spacing: -0.02em;
    }
    .app-subtitle {
        color: #4b5563;
        font-size: 1.15rem;
        margin-top: 0px;
        margin-bottom: 18px;
    }
    </style>
    """
    st.markdown(css_code, unsafe_allow_html=True)

def render_kpi_card(label: str, value: str, status_class: str = "") -> str:
    """
    Return HTML code for a custom KPI metric card.
    
    Args:
        label: Uppercase card description.
        value: Numeric indicator.
        status_class: "pass" | "warning" | "fail" for border color styling.
        
    Returns:
        HTML string.
    """
    return f"""
    <div class="kpi-card {status_class}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """

def highlight_null_cells(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply cell highlighting to pandas DataFrame for missing/null cells.
    
    Args:
        df: The pandas DataFrame.
        
    Returns:
        A pandas Styler object with styles applied.
    """
    # Define style formatting function
    def style_null(val):
        if pd.isnull(val) or str(val).strip() in ('', 'None', 'NaN', 'NaT'):
            return 'background-color: rgba(239, 68, 68, 0.12); color: #ef4444; font-weight: 500;'
        return ''
        
    # Check if df has columns
    if df.empty:
        return df.style
        
    if hasattr(df.style, 'map'):
        return df.style.map(style_null)
    else:
        return df.style.applymap(style_null)
