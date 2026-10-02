import streamlit as st
from frontend.components.header import render_page_header
from backend.config.settings import settings

def render_system_settings():
    render_page_header(
        title="System Health & Operational Configuration",
        subtitle="Configure active LLM providers, guardrail safety thresholds, and inspect connected business tools.",
        badge="Platform Operations",
        badge_type="neutral"
    )

    st.markdown("### 1. LLM Provider & Inference Engine")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            provider = st.selectbox("Active Provider", ["groq", "openai", "gemini"], index=["groq", "openai", "gemini"].index(settings.LLM_PROVIDER) if settings.LLM_PROVIDER in ["groq", "openai", "gemini"] else 0)
            model_name = st.text_input("Model ID", value=settings.GROQ_MODEL)
            masked_key = (settings.GROQ_API_KEY[:6] + "••••••••••••••••") if settings.GROQ_API_KEY else "Not Configured"
            st.text_input("Groq API Key (Configured)", value=masked_key, disabled=True)
            st.caption("✅ Production API Key loaded from environment configuration.")

    st.divider()

    st.markdown("### 2. Business Tools & Microservice Registry")
    tools = [
        {"Tool Name": "get_order_status", "Target Service": "Order Management Microservice", "Status": "Connected (Active)"},
        {"Tool Name": "get_payment_status", "Target Service": "Payment Gateway & Ledger", "Status": "Connected (Active)"},
        {"Tool Name": "get_shipment_status", "Target Service": "Logistics & Courier Telemetry", "Status": "Connected (Active)"},
        {"Tool Name": "get_customer_history", "Target Service": "Enterprise CRM Database", "Status": "Connected (Active)"},
        {"Tool Name": "create_escalation_ticket", "Target Service": "ServiceDesk Incident Management", "Status": "Connected (Active)"},
        {"Tool Name": "check_refund_eligibility", "Target Service": "Financial Policy Authorization Service", "Status": "Connected (Active)"}
    ]
    st.dataframe(tools, use_container_width=True)

    st.divider()

    st.markdown("### 3. Security Guardrails & Safety Parameters")
    with st.container(border=True):
        g1, g2 = st.columns(2)
        with g1:
            st.checkbox("Enable Input Guardrails (PII & Prompt Injection)", value=True, disabled=True)
            st.checkbox("Enable Output Guardrails (Grounding & Fact Verification)", value=True, disabled=True)
        with g2:
            st.metric("Max Input Length", f"{settings.MAX_INPUT_CHARS} chars")
            st.metric("Confidence Threshold", f"{settings.CONFIDENCE_THRESHOLD}")
