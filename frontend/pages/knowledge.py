import streamlit as st
from frontend.components.header import render_page_header
from backend.rag.retriever import retrieve_knowledge

HELP_CATEGORIES = [
    {"id": "orders", "name": "Orders & Delivery", "icon": "📦", "desc": "Tracking, dispatch timelines, and shipping options"},
    {"id": "payments", "name": "Payments & Billing", "icon": "💳", "desc": "UPI, cards, netbanking, invoice downloads, and charges"},
    {"id": "returns", "name": "Returns & Refunds", "icon": "🔄", "desc": "30-day return policy, pickups, and refund processing"},
    {"id": "products", "name": "Products & Warranty", "icon": "🛡️", "desc": "Warranty claims, replacements, and electronics care"},
    {"id": "account", "name": "Account & Security", "icon": "👤", "desc": "Profile updates, password reset, and verification"},
    {"id": "troubleshooting", "name": "Troubleshooting & FAQs", "icon": "⚙️", "desc": "Device connectivity, app issues, and common questions"},
]

POPULAR_ARTICLES = [
    {"id": "art_1", "title": "How do I return an item or request a replacement?", "category": "Returns & Refunds", "read_time": "3 min read", "summary": "Eligible items can be returned within 30 days of delivery through your order portal. Doorstep courier pickup will be scheduled automatically upon submission."},
    {"id": "art_2", "title": "Why was my payment debited while the order shows pending?", "category": "Payments & Billing", "read_time": "2 min read", "summary": "Banking gateway settlements can take up to 15-30 minutes during peak hours. If the order cannot be confirmed, the full amount is auto-refunded to your original payment method within 3-5 business days."},
    {"id": "art_3", "title": "How do I track courier dispatch and delivery schedules?", "category": "Orders & Delivery", "read_time": "2 min read", "summary": "Once dispatched from our fulfillment warehouse, live tracking IDs and courier partner links are sent via SMS and email, and are continuously updated in your Orders tab."},
    {"id": "art_4", "title": "How to claim warranty for electronics & accessories?", "category": "Products & Warranty", "read_time": "4 min read", "summary": "Submit your digital invoice copy along with the product serial number to register a claim. Authorized service center visits and manufacturer repairs are completely free during warranty."},
]

def render_knowledge_center():
    render_page_header(
        title="Help Center",
        subtitle="Find answers, operational guides, warranty information, and troubleshooting steps.",
        badge="Self-Service Portal",
        badge_type="info"
    )

    # Search Bar
    st.markdown("### What can we help you with?")
    search_query = st.text_input("Search Help Center", placeholder="Type keywords like 'return policy', 'track order', 'payment failed'...", label_visibility="collapsed")

    # If Search Query is Entered
    if search_query:
        st.markdown(f"### Search Results for \"{search_query}\"")
        with st.spinner("Searching Help Center..."):
            sources, _ = retrieve_knowledge(search_query, top_k=4)
        
        if sources:
            for idx, res in enumerate(sources, 1):
                doc_title = res.get("title", "Help Guide").replace("_", " ").replace(".md", "").title()
                snippet = res.get("snippet", "")
                
                with st.container(border=True):
                    st.markdown(f"**📄 {doc_title}**")
                    st.write(snippet)
        else:
            st.info("No matching articles found. You can start a conversation with our Support Assistant for dedicated assistance.")
        return

    # Category Grid
    st.markdown("### Browse by Category")
    c_cols = st.columns(3)
    for idx, cat in enumerate(HELP_CATEGORIES):
        with c_cols[idx % 3]:
            with st.container(border=True):
                st.markdown(f"### {cat['icon']} {cat['name']}")
                st.caption(cat['desc'])

    st.write("")

    # Popular Articles
    st.markdown("### Popular Articles")
    for art in POPULAR_ARTICLES:
        with st.container(border=True):
            st.markdown(f"**📖 {art['title']}** &nbsp; :blue[[{art['category']} • {art['read_time']}]]")
            st.write(art['summary'])
            
            if st.button(f"Ask Assistant about this", key=f"kb_ask_{art['id']}"):
                st.session_state["pending_input"] = f"Tell me more about: {art['title']}"
                st.session_state["customer_active_page"] = "Conversations"
                st.rerun()

    st.divider()

    # Need Help Banner
    with st.container(border=True):
        st.markdown("### Can't find what you are looking for?")
        st.caption("Our Support Assistant is available 24/7 to resolve complex inquiries.")
        if st.button("💬 Contact Support Assistant", key="help_chat_btn", type="primary"):
            st.session_state["customer_active_page"] = "Conversations"
            st.rerun()
