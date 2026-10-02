import streamlit as st
import json
from frontend.components.header import render_page_header
from backend.database.database import SessionLocal
from backend.database.models import AuditLog

def render_audit_and_traceability():
    render_page_header(
        title="Audit & Traceability",
        subtitle="Immutable transaction audit trail for security compliance, guardrail verification, and AI accountability.",
        badge="Enterprise Compliance",
        badge_type="neutral"
    )

    db = SessionLocal()
    try:
        logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(50).all()
    finally:
        db.close()

    if not logs:
        st.info("No audit logs recorded yet. Support interactions will automatically populate this compliance ledger.")
        return

    st.caption(f"Displaying latest **{len(logs)}** audit traces")

    for log in logs:
        with st.container(border=True):
            h1, h2, h3 = st.columns([2, 1, 1])
            with h1:
                st.markdown(f"**Request**: `{log.request_id}`  |  **Session**: `{log.conversation_id}`")
                st.caption(f"User: `{log.user_email}` | Timestamp: {log.created_at.strftime('%Y-%m-%d %H:%M:%S UTC') if log.created_at else ''}")
            with h2:
                st.metric("Latency", f"{log.latency_ms:.0f} ms")
            with h3:
                st.metric("Cost", f"₹{log.cost_inr:.4f}")

            st.markdown(f"**Customer Input**: *\"{log.input_text}\"*")
            st.markdown(f"**Grounded Response**: *\"{log.final_response}\"*")

            with st.expander("🔍 Inspect Complete Execution Trace & Telemetry", expanded=False):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Model**: `{log.model}` | **Prompt Version**: `{log.prompt_version}`")
                    st.markdown("**Input Classification & NLP**:")
                    st.code(log.classification_json, language="json")
                    
                    st.markdown("**Guardrail Verifications**:")
                    st.code(log.guardrail_results_json, language="json")
                with c2:
                    st.markdown("**Executed Tools & Authoritative Data**:")
                    st.code(log.tool_results_json, language="json")
                    
                    st.markdown("**Retrieved Knowledge Sources**:")
                    st.code(log.retrieved_docs_json, language="json")

                    st.markdown("**Token Consumption**:")
                    st.code(log.token_usage_json, language="json")
