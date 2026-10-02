import streamlit as st

def get_initials(name: str) -> str:
    """Extract up to 2 uppercase initials from a full name."""
    if not name:
        return "U"
    parts = name.strip().split()
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()

def render_sidebar() -> str:
    """
    Redesigned Enterprise Customer-Facing Sidebar Navigation using pure Streamlit widgets.
    """
    user = st.session_state.get("user", {
        "id": "USR-CUST01",
        "email": "customer@support.ai",
        "full_name": "Rajesh Kumar",
        "role": "customer"
    })
    role = user.get("role", "customer").lower()
    full_name = user.get("full_name", "Valued Customer")
    initials = get_initials(full_name)

    if "customer_active_page" not in st.session_state:
        st.session_state["customer_active_page"] = "Overview"
    if "admin_mode" not in st.session_state:
        st.session_state["admin_mode"] = False

    with st.sidebar:
        # 1. BRAND AREA (Pure Streamlit Markdown)
        st.markdown("### 💼 INTELLIGENT SUPPORT")
        st.caption("Enterprise Customer Experience")
        st.divider()

        # 2. USER PROFILE CARD
        role_display = "Administrator" if role == "admin" else ("Support Specialist" if role == "agent" else "Customer")
        role_badge = ":gray" if role == "admin" else (":blue" if role == "agent" else ":green")
        
        with st.container(border=True):
            st.markdown(f"**{full_name}**")
            st.markdown(f"{role_badge}[● {role_display}]")

        # View Mode Toggle for Admin/Agent roles
        if role in ["admin", "agent"]:
            st.caption("PORTAL VIEW")
            mode_cols = st.columns(2)
            with mode_cols[0]:
                if st.button("👤 Customer", use_container_width=True, type="primary" if not st.session_state["admin_mode"] else "secondary"):
                    st.session_state["admin_mode"] = False
                    st.rerun()
            with mode_cols[1]:
                if st.button("⚙️ Operations", use_container_width=True, type="primary" if st.session_state["admin_mode"] else "secondary"):
                    st.session_state["admin_mode"] = True
                    st.rerun()
            st.write("")

        # 3. CUSTOMER PORTAL NAVIGATION
        if not st.session_state["admin_mode"]:
            st.caption("WORKSPACE")
            
            nav_items_workspace = [
                ("Overview", "🏠 Overview"),
                ("My Requests", "📥 My Requests"),
                ("Conversations", "💬 Conversations"),
                ("Orders & Services", "📦 Orders & Services"),
                ("Support Tickets", "🎫 Support Tickets"),
            ]
            
            for page_key, label in nav_items_workspace:
                is_active = (st.session_state["customer_active_page"] == page_key)
                if st.button(label, key=f"nav_{page_key}", use_container_width=True, type="primary" if is_active else "secondary"):
                    st.session_state["customer_active_page"] = page_key
                    st.rerun()

            st.caption("HELP & RESOURCES")
            nav_items_help = [
                ("Help Center", "📖 Help Center"),
                ("Contact Support", "🎧 Contact Support"),
            ]
            for page_key, label in nav_items_help:
                is_active = (st.session_state["customer_active_page"] == page_key)
                if st.button(label, key=f"nav_{page_key}", use_container_width=True, type="primary" if is_active else "secondary"):
                    st.session_state["customer_active_page"] = page_key
                    st.rerun()

            st.caption("ACCOUNT")
            is_active = (st.session_state["customer_active_page"] == "Profile & Settings")
            if st.button("⚙️ Profile & Settings", key="nav_Profile & Settings", use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state["customer_active_page"] = "Profile & Settings"
                st.rerun()

        # 4. OPERATIONS NAVIGATION
        else:
            st.caption("OPERATIONS & GOVERNANCE")
            admin_nav = [
                ("Operations Dashboard", "📊 Operations Dashboard"),
                ("Human Review Queue", "🛡️ Human Review Queue"),
                ("Support Desk", "🎫 Ticket Desk"),
                ("Knowledge Management", "📚 Knowledge Index"),
                ("AI Evaluation", "🧪 Model Benchmarks"),
                ("Audit & Traceability", "📜 Audit & Compliance"),
                ("Cost & Latency Analytics", "💰 Cost & Latency SRE"),
                ("System Settings", "⚙️ Operational Settings"),
            ]
            for page_key, label in admin_nav:
                is_active = (st.session_state["customer_active_page"] == page_key)
                if st.button(label, key=f"admin_nav_{page_key}", use_container_width=True, type="primary" if is_active else "secondary"):
                    st.session_state["customer_active_page"] = page_key
                    st.rerun()

        # 5. BOTTOM SECTION
        st.divider()
        if st.button("🚪 Sign Out", key="sidebar_sign_out", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.session_state["customer_active_page"] = "Overview"
            for key in ["active_conversation_id", "pending_input", "prefill_chat", "admin_mode"]:
                st.session_state.pop(key, None)
            st.rerun()

    return st.session_state["customer_active_page"]
