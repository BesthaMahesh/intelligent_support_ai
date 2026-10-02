import streamlit as st
from frontend.components.header import render_page_header
from backend.database.database import SessionLocal
from backend.database.models import Ticket

def render_human_review_queue():
    render_page_header(
        title="Human Review & Escalation Desk",
        subtitle="Review high-risk cases, approve AI recommendations, and execute supervisor interventions.",
        badge="Human-in-the-Loop",
        badge_type="warning"
    )

    db = SessionLocal()
    try:
        escalated_tickets = db.query(Ticket).filter(Ticket.status.in_(["OPEN", "ESCALATED"])).order_by(Ticket.created_at.desc()).all()
    finally:
        db.close()

    if not escalated_tickets:
        st.success("🎉 No pending human review escalations! All customer interactions are operating normally.")
        return

    st.markdown(f"**Pending review cases:** `{len(escalated_tickets)}`")

    for ticket in escalated_tickets:
        with st.container(border=True):
            h_col1, h_col2 = st.columns([3, 1])
            with h_col1:
                st.markdown(f"### Ticket `{ticket.id}` - {ticket.title}")
                st.markdown(f"**Customer**: {ticket.customer_name} (`{ticket.customer_id}`) | **Order ID**: `{ticket.order_id or 'N/A'}`")
            with h_col2:
                p_badge = ":red" if ticket.priority in ["HIGH", "CRITICAL"] else ":orange"
                st.markdown(f"{p_badge}[**● {ticket.priority} PRIORITY**]")

            st.divider()

            c1, c2, c3 = st.columns(3)
            c1.markdown(f"**Intent**: `{ticket.intent}`")
            c2.markdown(f"**Status**: `{ticket.status}`")
            c3.markdown(f"**Assigned Desk**: `{ticket.assigned_to}`")

            st.markdown(f"**Escalation Reason / Business Rule**:\n> {ticket.escalation_reason or 'Risk threshold exceeded'}")
            st.markdown(f"**AI Recommended Action**:\n```\n{ticket.ai_recommended_action or 'Investigate transaction with logistics/finance lead'}\n```")

            st.markdown("#### Agent Review & Decision")
            custom_response = st.text_area(
                "Modify or approve response to customer:",
                value=f"Dear {ticket.customer_name}, we have escalated order {ticket.order_id or ''} to our senior desk. A specialist is actively prioritizing your case.",
                key=f"resp_{ticket.id}"
            )

            b1, b2, b3, b4 = st.columns(4)
            with b1:
                if st.button("✅ Accept Recommendation", key=f"accept_{ticket.id}", use_container_width=True, type="primary"):
                    db = SessionLocal()
                    try:
                        t = db.query(Ticket).filter(Ticket.id == ticket.id).first()
                        if t:
                            t.status = "RESOLVED"
                            t.ai_recommended_action = "Approved by Support Agent: " + custom_response
                            db.commit()
                        st.success(f"Ticket {ticket.id} approved and resolved.")
                    finally:
                        db.close()
                    st.rerun()

            with b2:
                if st.button("✏️ Send Modified Response", key=f"mod_{ticket.id}", use_container_width=True):
                    db = SessionLocal()
                    try:
                        t = db.query(Ticket).filter(Ticket.id == ticket.id).first()
                        if t:
                            t.status = "IN_PROGRESS"
                            t.ai_recommended_action = "Modified: " + custom_response
                            db.commit()
                        st.info(f"Custom response dispatched for {ticket.id}.")
                    finally:
                        db.close()
                    st.rerun()

            with b3:
                if st.button("✔️ Mark Resolved", key=f"res_{ticket.id}", use_container_width=True):
                    db = SessionLocal()
                    try:
                        t = db.query(Ticket).filter(Ticket.id == ticket.id).first()
                        if t:
                            t.status = "RESOLVED"
                            db.commit()
                        st.success(f"Ticket {ticket.id} marked as resolved.")
                    finally:
                        db.close()
                    st.rerun()

            with b4:
                if st.button("🚨 Escalate to Tier-3", key=f"esc_{ticket.id}", use_container_width=True):
                    db = SessionLocal()
                    try:
                        t = db.query(Ticket).filter(Ticket.id == ticket.id).first()
                        if t:
                            t.status = "ESCALATED"
                            t.priority = "CRITICAL"
                            t.assigned_to = "Tier-3 Operations Management"
                            db.commit()
                        st.warning(f"Ticket {ticket.id} escalated to Tier-3 Management.")
                    finally:
                        db.close()
                    st.rerun()
