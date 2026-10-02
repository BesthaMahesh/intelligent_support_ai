import streamlit as st
from frontend.components.header import render_page_header
from backend.tools.ticket_api import create_escalation_ticket

def render_contact_support_page():
    user = st.session_state.get("user", {})
    customer_id = user.get("id", "CUS-8821")
    customer_name = user.get("full_name", "Valued Customer")
    user_email = user.get("email", "customer@support.ai")

    render_page_header(
        title="Contact Support",
        subtitle="Connect with our automated virtual assistant or speak directly with enterprise support specialists.",
        badge="24/7 Global Support",
        badge_type="success"
    )

    # 3 Channel Cards
    c1, c2, c3 = st.columns(3)

    with c1:
        with st.container(border=True):
            st.markdown("### 💬 Virtual Assistant")
            st.write("Instant resolution for order tracking, returns, billing, and FAQs.")
            st.caption(":green[● Response Time: Instant]")
            if st.button("Start Live Chat", key="contact_chat_btn", use_container_width=True, type="primary"):
                st.session_state["customer_active_page"] = "Conversations"
                st.rerun()

    with c2:
        with st.container(border=True):
            st.markdown("### 🎫 Support Ticket")
            st.write("For account issues, complex warranty claims, or enterprise escalations.")
            st.caption(":blue[● Response: Within 10 minutes]")
            if st.button("Create Case", key="contact_ticket_btn", use_container_width=True):
                st.session_state["customer_active_page"] = "My Requests"
                st.rerun()

    with c3:
        with st.container(border=True):
            st.markdown("### 🎧 Specialist Queue")
            st.write("Escalate your active session directly to our senior resolution specialists.")
            st.caption(":orange[● Dedicated Support Tier]")
            if st.button("Request Specialist", key="contact_human_btn", use_container_width=True):
                tkt = create_escalation_ticket(
                    customer_id=customer_id,
                    customer_name=customer_name,
                    title="Specialist Assistance Request from Contact Portal",
                    description="Customer requested human specialist assistance from the Contact Support page.",
                    priority="HIGH"
                )
                st.success(f"Specialist queue ticket {tkt['ticket_id']} logged. A team member is assigned.")

    st.divider()

    # Direct Inquiry Form
    st.markdown("### Send a Message to Support")
    
    with st.form("contact_direct_form"):
        fc1, fc2 = st.columns(2)
        with fc1:
            subject = st.text_input("Subject", placeholder="e.g. Question about warranty coverage")
            email_field = st.text_input("Your Email", value=user_email, disabled=True)
        with fc2:
            department = st.selectbox("Department", ["Customer Care", "Billing & Invoices", "Logistics & Delivery", "Technical Support"])
            order_ref = st.text_input("Order Reference (Optional)", placeholder="e.g. ORD-78231")
        
        message_body = st.text_area("Message / Details", placeholder="Explain your query in detail...")
        
        submit_btn = st.form_submit_button("Send Support Inquiry", type="primary")
        if submit_btn:
            if subject and message_body:
                t = create_escalation_ticket(
                    customer_id=customer_id,
                    customer_name=customer_name,
                    order_id=order_ref if order_ref else None,
                    title=f"[{department}] {subject}",
                    description=message_body,
                    intent=department.lower().replace(" & ", "_").replace(" ", "_"),
                    priority="MEDIUM"
                )
                st.success(f"Inquiry received! Case ID: {t['ticket_id']}. Our support team will follow up at {user_email}.")
            else:
                st.error("Please fill in both the Subject and Message fields.")
