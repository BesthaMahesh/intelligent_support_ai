import streamlit as st
from frontend.components.header import render_page_header
from frontend.utils.api_client import EnterpriseAPIClient

def render_dashboard():
    user = st.session_state.get("user", {})
    customer_name = user.get("full_name", "Valued Customer")
    customer_id = user.get("id", "CUS-8821")

    # Header section
    render_page_header(
        title=f"Welcome back, {customer_name}",
        subtitle="Manage your support requests, conversations, and services from one place.",
        badge="Active",
        badge_type="success"
    )

    # Fetch real data
    data = EnterpriseAPIClient.get_customer_dashboard_data(customer_id)
    if not data.get("has_data", False):
        st.info("No customer activity records found. Use the quick actions below to submit a request or start a conversation.")
        return

    # Top Action Banner
    col_msg, col_act1, col_act2, col_act3 = st.columns([4, 2, 2, 2])
    with col_msg:
        st.markdown("#### How can we help you today?")
    with col_act1:
        if st.button("💬 Start Conversation", use_container_width=True, type="primary"):
            st.session_state["customer_active_page"] = "Conversations"
            st.rerun()
    with col_act2:
        if st.button("📥 View My Requests", use_container_width=True):
            st.session_state["customer_active_page"] = "My Requests"
            st.rerun()
    with col_act3:
        if st.button("📦 Check an Order", use_container_width=True):
            st.session_state["customer_active_page"] = "Orders & Services"
            st.rerun()

    st.write("")

    # 1. CUSTOMER KEY METRICS (6 KPI CARDS)
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)
    with kpi_col1:
        st.metric("Active Requests", data.get("active_requests_count", 0))
    with kpi_col2:
        st.metric("Open Tickets", data.get("open_tickets_count", 0))
    with kpi_col3:
        st.metric("Orders in Progress", data.get("orders_in_progress_count", 0))
    with kpi_col4:
        st.metric("Pending Actions", data.get("pending_actions_count", 0))
    with kpi_col5:
        st.metric("Resolved Requests", data.get("resolved_count", 0))
    with kpi_col6:
        st.metric("Support Response", data.get("avg_response_time", "~3 min"))

    st.divider()

    # 2. QUICK ACTIONS (4 CLEAN ENTERPRISE CARDS)
    st.markdown("### Quick Actions")
    q1, q2, q3, q4 = st.columns(4)
    
    with q1:
        with st.container(border=True):
            st.markdown("**💬 Start Conversation**")
            st.caption("Get quick answers or connect with our support team.")
            if st.button("Open Chat", key="qa_chat", use_container_width=True):
                st.session_state["customer_active_page"] = "Conversations"
                st.rerun()

    with q2:
        with st.container(border=True):
            st.markdown("**📦 Track an Order**")
            st.caption("Check order and real-time delivery status.")
            if st.button("Track Orders", key="qa_track", use_container_width=True):
                st.session_state["customer_active_page"] = "Orders & Services"
                st.rerun()

    with q3:
        with st.container(border=True):
            st.markdown("**📋 View Requests**")
            st.caption("Manage your open and resolved support cases.")
            if st.button("Manage Requests", key="qa_reqs", use_container_width=True):
                st.session_state["customer_active_page"] = "My Requests"
                st.rerun()

    with q4:
        with st.container(border=True):
            st.markdown("**📖 Help Center**")
            st.caption("Find answers and helpful customer guides.")
            if st.button("Search Articles", key="qa_kb", use_container_width=True):
                st.session_state["customer_active_page"] = "Help Center"
                st.rerun()

    st.divider()

    # 3. ACTIVE REQUESTS & RECENT CONVERSATIONS (2 COLUMNS)
    grid_col1, grid_col2 = st.columns(2)

    with grid_col1:
        st.markdown("### Active Support Requests")
        requests = data.get("recent_requests", [])
        if requests:
            for req in requests:
                with st.container(border=True):
                    rc1, rc2 = st.columns([3, 1])
                    with rc1:
                        st.markdown(f"**{req['id']}** &nbsp;•&nbsp; **{req['subject']}**")
                    with rc2:
                        p_color = ":red" if req["priority"] == "Critical" else (":orange" if req["priority"] == "High" else ":blue")
                        st.markdown(f"{p_color}[{req['status']}]")
                    st.caption(f"Updated: {req['updated_at']} | Category: {req['category']} | Priority: {req['priority']}")
            
            if st.button("View All Requests →", key="view_all_reqs", use_container_width=True):
                st.session_state["customer_active_page"] = "My Requests"
                st.rerun()
        else:
            with st.container(border=True):
                st.markdown("**No active support requests**")
                st.caption("You don't have any open tickets right now.")

    with grid_col2:
        st.markdown("### Recent Conversations")
        conversations = data.get("recent_conversations", [])
        if conversations:
            for conv in conversations:
                with st.container(border=True):
                    cc1, cc2 = st.columns([3, 1])
                    with cc1:
                        st.markdown(f"**{conv['title']}**")
                    with cc2:
                        st.caption(conv['date'])
                    st.write(conv['last_message'])
            
            if st.button("Continue Conversation →", key="view_all_convs", use_container_width=True):
                st.session_state["customer_active_page"] = "Conversations"
                st.rerun()
        else:
            with st.container(border=True):
                st.markdown("**No recent conversations**")
                st.caption("Start a chat to get immediate answers.")

    st.divider()

    # 4. RECENT ORDERS & HELP CENTER GUIDES (2 COLUMNS)
    sec_col1, sec_col2 = st.columns(2)

    with sec_col1:
        st.markdown("### Recent Orders & Services")
        orders = data.get("recent_orders", [])
        if orders:
            for ord_item in orders:
                with st.container(border=True):
                    oc1, oc2 = st.columns([3, 1])
                    with oc1:
                        st.markdown(f"**Order #{ord_item.get('order_id')}** — {ord_item.get('product', 'Product')}")
                    with oc2:
                        st.markdown(f"**₹{ord_item.get('amount', 0):,.2f}**")
                    st.caption(f"Payment: {ord_item.get('payment_status', 'SUCCESS')} | Status: {ord_item.get('order_status', 'CONFIRMED')}")
            
            if st.button("View All Orders →", key="dash_view_orders", use_container_width=True):
                st.session_state["customer_active_page"] = "Orders & Services"
                st.rerun()
        else:
            st.caption("No recent orders recorded.")

    with sec_col2:
        st.markdown("### Recommended Help Guides")
        articles = data.get("recommended_articles", [])
        for art in articles:
            with st.container(border=True):
                st.markdown(f"**📖 {art['title']}**")
                st.caption(f"{art['category']} • {art['read_time']}")
        
        if st.button("Browse Help Center →", key="dash_browse_kb", use_container_width=True):
            st.session_state["customer_active_page"] = "Help Center"
            st.rerun()
