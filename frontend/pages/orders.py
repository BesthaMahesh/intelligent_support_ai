import streamlit as st
from frontend.components.header import render_page_header
from frontend.utils.api_client import EnterpriseAPIClient

def render_orders_page():
    user = st.session_state.get("user", {})
    customer_id = user.get("id", "CUS-8821")

    render_page_header(
        title="Orders & Services",
        subtitle="Track your active purchases, courier milestones, invoices, and service requests.",
        badge="Fulfillment Center",
        badge_type="info"
    )

    orders = EnterpriseAPIClient.get_customer_orders(customer_id)

    # Search & Filter bar
    search_col, filter_col = st.columns([3, 1])
    with search_col:
        search_query = st.text_input("Search orders by ID or product name...", placeholder="e.g. ORD-78231 or Sony Headphones", label_visibility="collapsed")
    with filter_col:
        status_filter = st.selectbox("Status Filter", ["All Statuses", "Confirmed", "In Progress", "Delivered"], label_visibility="collapsed")

    filtered_orders = orders
    if search_query:
        q = search_query.lower()
        filtered_orders = [o for o in filtered_orders if q in o.get("order_id", "").lower() or q in o.get("product", "").lower()]
    if status_filter != "All Statuses":
        if status_filter == "Confirmed":
            filtered_orders = [o for o in filtered_orders if o.get("order_status") in ["CONFIRMED", "PAYMENT_PENDING"]]
        elif status_filter == "In Progress":
            filtered_orders = [o for o in filtered_orders if o.get("order_status") in ["PROCESSING", "SHIPPED"]]
        elif status_filter == "Delivered":
            filtered_orders = [o for o in filtered_orders if o.get("order_status") == "DELIVERED"]

    if not filtered_orders:
        with st.container(border=True):
            st.markdown("### No matching orders found")
            st.caption("Check your search query or view all your past transactions.")
        return

    st.write("")

    for ord_item in filtered_orders:
        order_id = ord_item.get("order_id", "ORD-00000")
        product = ord_item.get("product", "Product Item")
        amount = ord_item.get("amount", 0.0)
        currency = ord_item.get("currency", "INR")
        order_status = ord_item.get("order_status", "CONFIRMED")
        payment_status = ord_item.get("payment_status", "SUCCESS")
        payment_method = ord_item.get("payment_method", "Standard Payment")
        notes = ord_item.get("notes", "")

        status_color = ":green" if order_status == "DELIVERED" else (":blue" if order_status in ["CONFIRMED", "PROCESSING", "SHIPPED"] else ":orange")

        with st.container(border=True):
            head_col1, head_col2 = st.columns([3, 1])
            with head_col1:
                st.markdown(f"### {order_id} &nbsp; {status_color}[{order_status.replace('_', ' ')}]")
                st.markdown(f"**Product:** {product}")
            with head_col2:
                st.markdown(f"### ₹{amount:,.2f}")
                st.caption(f"Paid via {payment_method}")

            st.markdown("---")
            
            # Step progress text
            st.markdown("**Fulfillment Progress:**")
            if order_status == "DELIVERED":
                st.success("✅ Order Placed ➔ ✅ Payment Confirmed ➔ ✅ Processing ➔ ✅ Shipped ➔ ✅ Delivered")
            elif order_status == "SHIPPED":
                st.info("✅ Order Placed ➔ ✅ Payment Confirmed ➔ ✅ Processing ➔ 🚚 **In Transit / Shipped** ➔ ⏳ Out for Delivery")
            elif order_status == "PROCESSING":
                st.info("✅ Order Placed ➔ ✅ Payment Confirmed ➔ 📦 **Warehouse Processing** ➔ ⏳ Shipping")
            elif order_status == "PAYMENT_PENDING":
                st.warning("⏳ Order Placed ➔ 💳 **Payment Reconciliation Pending** ➔ Processing")
            else:
                st.info("✅ Order Placed ➔ ✅ Payment Confirmed ➔ ⏳ Processing & Dispatch")

            st.info(f"ℹ️ **Status Update:** {notes}")

            btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])
            with btn_col1:
                if st.button(f"💬 Get Help on {order_id}", key=f"help_{order_id}", use_container_width=True):
                    st.session_state["pending_input"] = f"I need assistance regarding my order {order_id} ({product})."
                    st.session_state["customer_active_page"] = "Conversations"
                    st.rerun()
            with btn_col2:
                if st.button(f"📄 Download Invoice", key=f"inv_{order_id}", use_container_width=True):
                    st.success(f"Official Tax Invoice for {order_id} generated.")
            with btn_col3:
                st.caption(f"Order Ref: {order_id} • Verified Transaction")

        st.write("")
