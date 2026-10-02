import streamlit as st
from backend.database.database import SessionLocal
from backend.auth.authentication import authenticate_user

def render_login():
    col_l, col_center, col_r = st.columns([1, 2, 1])
    with col_center:
        st.markdown("# 💼 INTELLIGENT SUPPORT")
        st.caption("Enterprise Customer Experience Platform")
        st.write("")

        with st.container(border=True):
            st.markdown("### Welcome back")
            st.caption("Sign in to access your enterprise support portal.")
            
            with st.form("login_form"):
                email = st.text_input("Email Address", placeholder="name@company.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")

                if submit:
                    if not email or not password:
                        st.error("Please provide both email and password.")
                    else:
                        db = SessionLocal()
                        try:
                            user = authenticate_user(db, email, password)
                            if user:
                                st.session_state["authenticated"] = True
                                st.session_state["user"] = {
                                    "id": user.id,
                                    "email": user.email,
                                    "full_name": user.full_name,
                                    "role": user.role
                                }
                                st.session_state["customer_active_page"] = "Overview"
                                st.success(f"Welcome back, {user.full_name}!")
                                st.rerun()
                            else:
                                st.error("Invalid credentials. Please verify your email and password.")
                        finally:
                            db.close()

            st.divider()
            st.caption("QUICK DEMO SIGN-IN")
            
            bcol1, bcol2, bcol3 = st.columns(3)
            with bcol1:
                if st.button("👤 Customer", use_container_width=True, type="primary"):
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = {
                        "id": "USR-CUST01",
                        "email": "customer@support.ai",
                        "full_name": "Rajesh Kumar",
                        "role": "customer"
                    }
                    st.session_state["customer_active_page"] = "Overview"
                    st.rerun()
            with bcol2:
                if st.button("🎧 Specialist", use_container_width=True):
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = {
                        "id": "USR-AGENT01",
                        "email": "agent@support.ai",
                        "full_name": "Lead Support Specialist",
                        "role": "agent"
                    }
                    st.session_state["customer_active_page"] = "Overview"
                    st.rerun()
            with bcol3:
                if st.button("👑 Admin", use_container_width=True):
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = {
                        "id": "USR-ADMIN01",
                        "email": "admin@support.ai",
                        "full_name": "System Administrator",
                        "role": "admin"
                    }
                    st.session_state["customer_active_page"] = "Overview"
                    st.rerun()

            st.caption("🔒 Protected by Enterprise SSO & MFA Compliance")
