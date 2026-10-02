import streamlit as st
from frontend.components.header import render_page_header
from frontend.utils.api_client import EnterpriseAPIClient
from backend.tools.ticket_api import create_escalation_ticket

def render_tickets_management():
    user = st.session_state.get("user", {})
    customer_id = user.get("id", "CUS-8821")
    customer_name = user.get("full_name", "Valued Customer")

    render_page_header(
        title="My Support Requests",
        subtitle="Track the status of your formal inquiries, escalations, and resolved cases.",
        badge="Case Management",
        badge_type="neutral"
    )

    tickets = EnterpriseAPIClient.get_customer_tickets(customer_id)

    # Top action: Create New Request
    top_c1, top_c2 = st.columns([3, 1])
    with top_c1:
        st.write("Have an issue that requires specialist investigation? Submit a formal support request below.")
    with top_c2:
        with st.popover("➕ Submit New Request", use_container_width=True):
            st.markdown("### Create Support Request")
            new_title = st.text_input("Subject / Title", placeholder="Brief description of the issue")
            new_order_id = st.text_input("Associated Order ID (Optional)", placeholder="e.g. ORD-78231")
            new_category = st.selectbox("Category", ["Orders & Shipping", "Billing & Payment", "Returns & Refunds", "Product Warranty", "Account & Security", "Other"])
            new_priority = st.selectbox("Urgency", ["Medium", "Low", "High", "Critical"])
            new_desc = st.text_area("Detailed Explanation", placeholder="Please provide all relevant details...")
            
            if st.button("Submit Case", type="primary", use_container_width=True):
                if new_title and new_desc:
                    ticket_resp = create_escalation_ticket(
                        customer_id=customer_id,
                        customer_name=customer_name,
                        order_id=new_order_id if new_order_id else None,
                        title=new_title,
                        description=new_desc,
                        intent=new_category.lower().replace(" ", "_"),
                        priority=new_priority.upper()
                    )
                    st.success(f"Request {ticket_resp['ticket_id']} submitted successfully!")
                    st.rerun()
                else:
                    st.error("Please provide both a subject and explanation.")

    st.write("")

    # Status Tabs
    tab_all, tab_open, tab_pending, tab_resolved = st.tabs([
        f"All Requests ({len(tickets)})",
        f"Open & In Progress ({len([t for t in tickets if t['status'] in ['OPEN', 'IN_PROGRESS', 'ESCALATED']])})",
        f"Waiting for Customer ({len([t for t in tickets if t['status'] == 'WAITING_FOR_CUSTOMER'])})",
        f"Resolved & Closed ({len([t for t in tickets if t['status'] in ['RESOLVED', 'CLOSED']])})"
    ])

    def display_ticket_list(filtered_list):
        if not filtered_list:
            with st.container(border=True):
                st.markdown("### No support requests in this category")
                st.caption("You don't have any active cases matching this view.")
            return

        for t in filtered_list:
            status_text = t.get("status", "OPEN").replace("_", " ").title()
            priority_text = t.get("priority", "MEDIUM").capitalize()
            
            p_color = ":red" if priority_text in ["Critical", "High"] else (":orange" if priority_text == "Medium" else ":blue")
            s_color = ":green" if status_text in ["Resolved", "Closed"] else (":orange" if "Waiting" in status_text else ":blue")

            with st.container(border=True):
                col_head1, col_head2 = st.columns([3, 1])
                with col_head1:
                    ref_text = f" | Order Ref: {t.get('order_id')}" if (t.get('order_id') and t.get('order_id') != '—') else ""
                    st.markdown(f"**{t.get('id')}** &nbsp;•&nbsp; **{t.get('title')}**")
                    st.caption(f"{p_color}[● {priority_text} Priority]{ref_text}")
                with col_head2:
                    st.markdown(f"{s_color}[**{status_text}**]")
                
                st.write(t.get('description'))
                st.caption(f"Assigned to: {t.get('assigned_to', 'Support Queue')} | Category: {t.get('intent', 'General')} | Created: {t.get('created_at')}")

    with tab_all:
        display_ticket_list(tickets)

    with tab_open:
        open_list = [t for t in tickets if t["status"] in ["OPEN", "IN_PROGRESS", "ESCALATED"]]
        display_ticket_list(open_list)

    with tab_pending:
        pending_list = [t for t in tickets if t["status"] == "WAITING_FOR_CUSTOMER"]
        display_ticket_list(pending_list)

    with tab_resolved:
        resolved_list = [t for t in tickets if t["status"] in ["RESOLVED", "CLOSED"]]
        display_ticket_list(resolved_list)
