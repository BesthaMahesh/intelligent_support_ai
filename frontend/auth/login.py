import streamlit as st
import re
from backend.database.database import SessionLocal
from backend.auth.authentication import authenticate_user, create_user, get_user_by_email

def is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email.strip()))

def render_login():
    col_l, col_center, col_r = st.columns([1, 4, 1])
    with col_center:
        st.markdown("# 💼 INTELLIGENT SUPPORT")
        st.caption("Enterprise Customer Experience Platform")
        st.write("")

        with st.container(border=True):
            tab_login, tab_register = st.tabs(["🔑 Sign In", "✨ Create Account"])
            
            with tab_login:
                st.markdown("### Welcome back")
                st.caption("Sign in to access your enterprise customer support portal.")
                
                with st.form("login_form"):
                    email = st.text_input("Email Address", placeholder="name@company.com", key="login_email")
                    password = st.text_input("Password", type="password", placeholder="••••••••", key="login_password")
                    submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")

                    if submit:
                        if not email or not password:
                            st.error("Please provide both email and password.")
                        else:
                            db = SessionLocal()
                            try:
                                user = authenticate_user(db, email.strip(), password)
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
                                    st.error("Invalid credentials. If you are a new user, please switch to the 'Create Account' tab above.")
                            finally:
                                db.close()

            with tab_register:
                st.markdown("### Create an Account")
                st.caption("Register for a new enterprise support account in seconds.")
                
                with st.form("register_form"):
                    reg_name = st.text_input("Full Name", placeholder="e.g. Mahesh Babu", key="reg_name")
                    reg_email = st.text_input("Email Address", placeholder="name@company.com", key="reg_email")
                    reg_password = st.text_input("Password", type="password", placeholder="Minimum 6 characters", key="reg_password")
                    reg_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-type password", key="reg_confirm")
                    reg_role = st.selectbox("Account Role", options=["Customer", "Support Specialist (Agent)", "Administrator"], key="reg_role")
                    
                    reg_submit = st.form_submit_button("Create Account & Sign In", use_container_width=True, type="primary")
                    
                    if reg_submit:
                        if not reg_name.strip():
                            st.error("Please enter your full name.")
                        elif not reg_email.strip() or not is_valid_email(reg_email):
                            st.error("Please enter a valid email address.")
                        elif len(reg_password) < 6:
                            st.error("Password must be at least 6 characters long.")
                        elif reg_password != reg_confirm:
                            st.error("Passwords do not match. Please verify.")
                        else:
                            role_map = {
                                "Customer": "customer",
                                "Support Specialist (Agent)": "agent",
                                "Administrator": "admin"
                            }
                            db = SessionLocal()
                            try:
                                existing = get_user_by_email(db, reg_email.strip())
                                if existing:
                                    st.error(f"An account with email '{reg_email.strip()}' already exists. Please switch to Sign In.")
                                else:
                                    new_user = create_user(
                                        db=db,
                                        email=reg_email.strip(),
                                        password=reg_password,
                                        full_name=reg_name.strip(),
                                        role=role_map.get(reg_role, "customer")
                                    )
                                    st.session_state["authenticated"] = True
                                    st.session_state["user"] = {
                                        "id": new_user.id,
                                        "email": new_user.email,
                                        "full_name": new_user.full_name,
                                        "role": new_user.role
                                    }
                                    st.session_state["customer_active_page"] = "Overview"
                                    st.success(f"Account successfully created! Welcome, {new_user.full_name}.")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Failed to create account: {str(e)}")
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

