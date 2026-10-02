import streamlit as st

def render_page_header(title: str, subtitle: str, badge: str = None, badge_type: str = "neutral"):
    """
    Renders a crisp, enterprise-grade page header using native Streamlit text and columns.
    """
    col_title, col_badge = st.columns([4, 1])
    with col_title:
        st.subheader(title)
        st.caption(subtitle)
    with col_badge:
        if badge:
            badge_color = ":green" if badge_type == "success" else (":blue" if badge_type == "info" else (":orange" if badge_type == "warning" else ":gray"))
            st.markdown(f"**Status:** {badge_color}[{badge}]")
    st.divider()
