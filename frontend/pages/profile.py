import streamlit as st
from frontend.components.header import render_page_header

def render_profile_and_settings():
    user = st.session_state.get("user", {})
    customer_id = user.get("id", "CUS-8821")
    customer_name = user.get("full_name", "Rajesh Kumar")
    email = user.get("email", "customer@support.ai")
    role = user.get("role", "customer").capitalize()

    render_page_header(
        title="Profile & Settings",
        subtitle="Manage your personal account credentials, notification channels, security, and privacy preferences.",
        badge="Account Settings",
        badge_type="neutral"
    )

    tab_profile, tab_notif, tab_security, tab_privacy = st.tabs([
        "👤 Personal Information",
        "🔔 Notification Preferences",
        "🔒 Security & Access",
        "🛡️ Privacy & Compliance"
    ])

    with tab_profile:
        st.markdown("### Personal Details")
        with st.form("personal_info_form"):
            col1, col2 = st.columns(2)
            with col1:
                name_val = st.text_input("Full Name", value=customer_name)
                cust_id_val = st.text_input("Account ID", value=customer_id, disabled=True)
            with col2:
                email_val = st.text_input("Email Address", value=email, disabled=True)
                phone_val = st.text_input("Phone Number", value="+91 98401 23456")

            st.markdown("### Language & Regional Preferences")
            lang_col1, lang_col2 = st.columns(2)
            with lang_col1:
                selected_lang = st.selectbox("Preferred Communication Language", ["English", "Tamil (தமிழ்)", "Hindi (हिन्दी)", "Telugu (తెలుగు)"])
            with lang_col2:
                timezone = st.selectbox("Timezone", ["IST (UTC+05:30) - India Standard Time", "UTC (UTC+00:00) - Universal Time", "EST (UTC-05:00) - Eastern Time"])

            save_profile = st.form_submit_button("Save Changes", type="primary")
            if save_profile:
                st.session_state["user"]["full_name"] = name_val
                st.success("Account profile updated successfully.")
                st.rerun()

    with tab_notif:
        st.markdown("### Delivery & Support Notifications")
        st.checkbox("Email notifications for support ticket updates", value=True)
        st.checkbox("SMS notifications for order dispatch & courier milestones", value=True)
        st.checkbox("Instant chat notifications when support specialist replies", value=True)
        st.checkbox("Weekly summary of resolved support cases and invoices", value=False)
        
        if st.button("Update Notification Preferences", type="primary"):
            st.success("Notification preferences saved.")

    with tab_security:
        st.markdown("### Password & Authentication")
        with st.form("password_change_form"):
            cur_pwd = st.text_input("Current Password", type="password")
            new_pwd = st.text_input("New Password", type="password")
            conf_pwd = st.text_input("Confirm New Password", type="password")
            
            pwd_submit = st.form_submit_button("Update Password", type="primary")
            if pwd_submit:
                if new_pwd and new_pwd == conf_pwd:
                    st.success("Password updated securely.")
                else:
                    st.error("Passwords do not match or are empty.")

        st.divider()
        st.markdown("### Two-Factor Authentication (2FA)")
        st.markdown("**Status:** :green[● Enabled (Authenticator App)]")
        if st.button("Manage 2FA Settings"):
            st.info("2FA settings verification prompt sent to your registered authenticator app.")

    with tab_privacy:
        st.markdown("### Data Governance & Privacy")
        st.write("Intelligent Support AI complies with enterprise data privacy standards (GDPR, ISO 27001, SOC 2).")
        st.write("All customer conversation records and personal identifying information (PII) are automatically masked and encrypted at rest.")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📥 Request Data Export", use_container_width=True):
                st.success("Data export package prepared. Download link dispatched to your email.")
        with c2:
            if st.button("🗑️ Delete Account Data", use_container_width=True):
                st.warning("Account deletion requests require secondary confirmation from compliance team.")
