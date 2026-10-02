import streamlit as st
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.database.database import init_db
from backend.auth.authentication import seed_default_users
from backend.rag.ingestion import ingest_knowledge_base
from frontend.auth.login import render_login
from frontend.components.sidebar import render_sidebar
from frontend.pages.dashboard import render_dashboard
from frontend.pages.orders import render_orders_page
from frontend.pages.conversations import render_conversations_workspace
from frontend.pages.tickets import render_tickets_management
from frontend.pages.knowledge import render_knowledge_center
from frontend.pages.contact import render_contact_support_page
from frontend.pages.profile import render_profile_and_settings
from frontend.pages.operations_dashboard import render_operations_dashboard
from frontend.pages.human_review import render_human_review_queue
from frontend.pages.evaluation import render_ai_evaluation
from frontend.pages.cost import render_cost_and_latency
from frontend.pages.audit import render_audit_and_traceability
from frontend.pages.settings import render_system_settings

st.set_page_config(
    page_title="Intelligent Support | Enterprise Customer Experience",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sophisticated Enterprise SaaS CSS Design System (Mobile-First & Responsive)
# CAUTION: Do NOT apply font-family !important to [class*="st-"] or [class*="css"] to preserve Material Icon ligatures
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #0F172A;
        background-color: #F8FAFC;
        -webkit-tap-highlight-color: transparent;
    }
    
    /* App background */
    .stApp {
        background-color: #F8FAFC;
    }

    /* Main container padding optimization */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 1200px;
    }
    
    /* Metrics Card Styling */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        padding: 12px 14px !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03) !important;
        min-width: 100% !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.45rem !important;
        font-weight: 800 !important;
        color: #0F172A !important;
        line-height: 1.2 !important;
        word-break: break-word !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        color: #64748B !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    /* Enterprise Touch-Friendly Buttons */
    .stButton > button {
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        min-height: 42px !important;
        padding: 0.5rem 0.9rem !important;
        transition: all 0.15s ease-in-out !important;
        touch-action: manipulation;
    }
    .stButton > button[kind="primary"] {
        background-color: #2563EB !important;
        border-color: #2563EB !important;
        color: #FFFFFF !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #1D4ED8 !important;
        border-color: #1D4ED8 !important;
    }
    .stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        color: #334155 !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #F1F5F9 !important;
        border-color: #94A3B8 !important;
        color: #0F172A !important;
    }

    /* Inputs touch optimization */
    input, select, textarea {
        font-size: 16px !important; /* Prevents auto-zoom on iOS */
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    
    /* Container & card borders */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #E2E8F0 !important;
        border-radius: 8px !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        border-bottom: 1px solid #E2E8F0;
        overflow-x: auto;
        flex-wrap: nowrap;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.88rem;
        color: #64748B;
        padding: 10px 8px;
        white-space: nowrap;
    }
    .stTabs [aria-selected="true"] {
        color: #2563EB !important;
        border-bottom-color: #2563EB !important;
    }

    /* Chat message container styling */
    .stChatMessage {
        background: transparent !important;
        padding: 6px 0 !important;
    }

    /* Responsive Mobile Overrides */
    @media (max-width: 768px) {
        .main .block-container {
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }

        h1, h2 {
            font-size: 1.5rem !important;
        }

        h3 {
            font-size: 1.25rem !important;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
        }

        div[data-testid="column"] {
            min-width: 100% !important;
            margin-bottom: 0.5rem;
        }

        .stButton > button {
            width: 100% !important;
            min-height: 44px !important;
        }

        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
            padding: 12px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize system resources on first load
@st.cache_resource
def bootstrap_system():
    init_db()
    seed_default_users()
    ingest_knowledge_base()
    return True

bootstrap_system()

# Authentication Check
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    render_login()
else:
    selected_page = render_sidebar()

    # Route navigation
    # 1. Customer-Facing Enterprise Pages
    if selected_page == "Overview":
        render_dashboard()
    elif selected_page == "My Requests":
        render_tickets_management()
    elif selected_page == "Conversations":
        render_conversations_workspace()
    elif selected_page == "Orders & Services":
        render_orders_page()
    elif selected_page == "Support Tickets":
        render_tickets_management()
    elif selected_page == "Help Center":
        render_knowledge_center()
    elif selected_page == "Contact Support":
        render_contact_support_page()
    elif selected_page == "Profile & Settings":
        render_profile_and_settings()

    # 2. Operations / Internal Admin Pages
    elif selected_page == "Operations Dashboard":
        render_operations_dashboard()
    elif selected_page == "Human Review Queue":
        render_human_review_queue()
    elif selected_page in ["Support Desk", "Ticket Desk"]:
        render_tickets_management()
    elif selected_page in ["Knowledge Management", "Knowledge Index"]:
        render_knowledge_center()
    elif selected_page in ["AI Evaluation", "Model Benchmarks"]:
        render_ai_evaluation()
    elif selected_page in ["Audit & Traceability", "Audit & Compliance"]:
        render_audit_and_traceability()
    elif selected_page in ["Cost & Latency Analytics", "Cost & Latency SRE"]:
        render_cost_and_latency()
    elif selected_page in ["System Settings", "Operational Settings"]:
        render_system_settings()
    else:
        render_dashboard()
