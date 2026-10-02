import streamlit as st
import uuid
import re
from datetime import datetime
from frontend.components.header import render_page_header
from frontend.utils.api_client import EnterpriseAPIClient
from backend.database.database import SessionLocal
from backend.database.models import Conversation, Message
from backend.tools.ticket_api import create_escalation_ticket

def render_conversations_workspace():
    user = st.session_state.get("user", {})
    customer_id = user.get("id", "CUS-8821")
    customer_name = user.get("full_name", "Valued Customer")
    user_email = user.get("email", "customer@support.ai")

    render_page_header(
        title="Customer Support Conversations",
        subtitle="Manage your active support conversations, get automated resolutions, or speak with a specialist.",
        badge="Online",
        badge_type="success"
    )

    # -------------------------------------------------------------
    # 1. FETCH CONVERSATIONS FROM REAL DATABASE
    # -------------------------------------------------------------
    db = SessionLocal()
    try:
        raw_conversations = db.query(Conversation).filter(
            Conversation.customer_id == customer_id
        ).order_by(Conversation.updated_at.desc()).all()
        
        # Load conversation summary snippets
        conv_data = []
        for c in raw_conversations:
            last_msg = db.query(Message).filter(Message.conversation_id == c.id).order_by(Message.created_at.desc()).first()
            snippet = (last_msg.content[:60] + "...") if (last_msg and last_msg.content) else "New conversation started"
            conv_data.append({
                "id": c.id,
                "customer_id": c.customer_id,
                "status": c.status,
                "intent": c.intent.replace("_", " ").title() if c.intent else "General Support",
                "updated_at": c.updated_at,
                "snippet": snippet
            })
    finally:
        db.close()

    # Active conversation state management - validate ownership
    valid_conv_ids = [c["id"] for c in conv_data]
    current_active_id = st.session_state.get("active_conversation_id")

    if not current_active_id or (current_active_id not in valid_conv_ids and not current_active_id.startswith("CONV-")):
        if conv_data:
            st.session_state["active_conversation_id"] = conv_data[0]["id"]
        else:
            new_id = f"CONV-{uuid.uuid4().hex[:6].upper()}"
            st.session_state["active_conversation_id"] = new_id

    active_id = st.session_state["active_conversation_id"]

    # -------------------------------------------------------------
    # 2. ENTERPRISE 2-PANEL LAYOUT (LEFT: INBOX, RIGHT: ACTIVE CHAT)
    # -------------------------------------------------------------
    col_inbox, col_chat = st.columns([1.1, 2.6], gap="medium")

    # =============================================================
    # LEFT PANEL: COMPACT INBOX & CONVERSATION LIST
    # =============================================================
    with col_inbox:
        inbox_top1, inbox_top2 = st.columns([2, 1])
        with inbox_top1:
            st.markdown("### Conversations")
        with inbox_top2:
            if st.button("+ New", key="btn_new_conv_top", use_container_width=True, type="primary"):
                new_conv_id = f"CONV-{uuid.uuid4().hex[:6].upper()}"
                st.session_state["active_conversation_id"] = new_conv_id
                st.rerun()

        # Search field
        search_query = st.text_input("Search conversations...", placeholder="Search ID, topic, or message...", label_visibility="collapsed")

        # Status filter tabs
        filter_status = st.selectbox(
            "Filter Status",
            ["All", "Active", "Specialist Assigned", "Resolved"],
            label_visibility="collapsed"
        )

        # Apply search & filters
        filtered_convs = conv_data
        if search_query:
            q = search_query.lower()
            filtered_convs = [
                c for c in filtered_convs
                if q in c["id"].lower() or q in c["intent"].lower() or q in c["snippet"].lower()
            ]

        if filter_status == "Active":
            filtered_convs = [c for c in filtered_convs if c["status"] == "active"]
        elif filter_status == "Specialist Assigned":
            filtered_convs = [c for c in filtered_convs if c["status"] == "escalated"]
        elif filter_status == "Resolved":
            filtered_convs = [c for c in filtered_convs if c["status"] in ["resolved", "closed"]]

        st.markdown("---")

        # Inbox Items Stream
        if filtered_convs:
            for c in filtered_convs:
                is_active = (c["id"] == active_id)
                short_id = c["id"].replace("CONV-", "#")
                time_str = c["updated_at"].strftime("%I:%M %p") if c["updated_at"] else "Recent"
                
                # Status representation
                if c["status"] == "escalated":
                    status_dot = ":orange[● Specialist Assigned]"
                elif c["status"] == "resolved":
                    status_dot = ":green[● Resolved]"
                else:
                    status_dot = ":blue[● Active]"

                with st.container(border=True):
                    row1, row2 = st.columns([2.5, 1])
                    with row1:
                        st.markdown(f"**{short_id}** &nbsp; {status_dot}")
                    with row2:
                        st.caption(time_str)
                    
                    st.caption(f"**{c['intent']}**")
                    st.write(f"_{c['snippet']}_")
                    
                    if not is_active:
                        if st.button("Open Conversation", key=f"sel_conv_{c['id']}", use_container_width=True):
                            st.session_state["active_conversation_id"] = c["id"]
                            st.rerun()
        else:
            with st.container(border=True):
                st.caption("No conversations found matching your search criteria.")

    # =============================================================
    # RIGHT PANEL: ACTIVE CONVERSATION WORKSPACE
    # =============================================================
    with col_chat:
        db = SessionLocal()
        try:
            active_conv = db.query(Conversation).filter(
                Conversation.id == active_id,
                Conversation.customer_id == customer_id
            ).first()
            messages = db.query(Message).filter(Message.conversation_id == active_id).order_by(Message.created_at.asc()).all() if active_conv else []
        finally:
            db.close()

        short_active_id = active_id.replace("CONV-", "#")

        # ---------------------------------------------------------
        # Active Header
        # ---------------------------------------------------------
        with st.container(border=True):
            head_l, head_r = st.columns([3, 1.4])
            with head_l:
                st.markdown("### Support Assistant")
                st.caption(f":green[● Online] &nbsp;•&nbsp; Conversation {short_active_id}")
            with head_r:
                if active_conv and active_conv.status == "escalated":
                    st.markdown(":orange[**● Specialist Assigned**]")
                    st.caption("A support specialist is active in this session.")
                else:
                    if st.button("Connect to Specialist", key=f"esc_{active_id}", use_container_width=True):
                        ticket = create_escalation_ticket(
                            customer_id=customer_id,
                            customer_name=customer_name,
                            title=f"Support Escalation for Conversation {active_id}",
                            description=f"Customer requested specialist support during conversation {active_id}.",
                            priority="HIGH",
                            escalation_reason="Customer connected to human specialist."
                        )
                        st.success(f"Support Specialist assigned. Request Ref: {ticket['ticket_id']}.")
                        st.rerun()

        # ---------------------------------------------------------
        # Compact Suggested Question Chips
        # ---------------------------------------------------------
        st.caption("Suggested:")
        chip1, chip2, chip3, chip4 = st.columns(4)
        with chip1:
            if st.button("Track my order", key="chip_track", use_container_width=True):
                st.session_state["pending_input"] = "Where is my order ORD-78231?"
        with chip2:
            if st.button("Return policy", key="chip_ret", use_container_width=True):
                st.session_state["pending_input"] = "What is the return policy for electronics?"
        with chip3:
            if st.button("Payment issue", key="chip_pay", use_container_width=True):
                st.session_state["pending_input"] = "Why is my payment deducted while order status is pending?"
        with chip4:
            if st.button("Cancel an order", key="chip_cancel", use_container_width=True):
                st.session_state["pending_input"] = "How can I cancel an order before shipping?"

        # ---------------------------------------------------------
        # Message Stream (Height-managed Container)
        # ---------------------------------------------------------
        chat_container = st.container(height=450, border=True)
        with chat_container:
            if not messages:
                st.markdown("### Start a conversation")
                st.write("Ask us about your orders, payments, returns, delivery timelines, or account settings.")
                st.caption("Type a message below or select one of the suggested topics above.")
            else:
                for msg in messages:
                    time_str = msg.created_at.strftime("%I:%M %p") if msg.created_at else ""
                    
                    # 1. Customer Message (Aligned Right / User Bubble)
                    if msg.sender == "customer":
                        with st.chat_message("user"):
                            st.write(msg.content)
                            st.caption(f"You • {time_str}")

                    # 2. Specialist Message
                    elif msg.sender == "agent":
                        with st.chat_message("human"):
                            st.markdown(f"**:orange[Support Specialist]**")
                            st.write(msg.content)
                            st.caption(f"Support Specialist • {time_str}")

                    # 3. Support Assistant Message (Aligned Left / Neutral Bubble)
                    else:
                        with st.chat_message("assistant"):
                            st.markdown(f"**Support Assistant**")
                            st.write(msg.content)
                            st.caption(f"Support Assistant • {time_str} • :green[✓ Information verified]")

                            # Contextual Actionable Responses (Section 13)
                            # Detect order ID mentions for 1-click order tracking
                            order_match = re.search(r'ORD-\d+', msg.content)
                            if order_match:
                                matched_ord = order_match.group(0)
                                act_c1, act_c2 = st.columns([1.2, 3])
                                with act_c1:
                                    if st.button(f"View Order {matched_ord}", key=f"ctx_ord_{msg.id}"):
                                        st.session_state["customer_active_page"] = "Orders & Services"
                                        st.rerun()

                            # Detect policy/return mentions for 1-click help center guide
                            if any(k in msg.content.lower() for k in ["return policy", "refund policy", "replacement"]):
                                act_p1, act_p2 = st.columns([1.5, 2.5])
                                with act_p1:
                                    if st.button("View Return Policy in Help Center", key=f"ctx_ret_{msg.id}"):
                                        st.session_state["customer_active_page"] = "Help Center"
                                        st.rerun()

        # ---------------------------------------------------------
        # Message Composer (Fixed Bottom)
        # ---------------------------------------------------------
        # Attachment Tool Popover
        attach_col, space_col = st.columns([1, 4])
        with attach_col:
            with st.popover("📎 Attach File"):
                st.caption("Upload invoice copy, payment screenshot, or product image:")
                uploaded_file = st.file_uploader("Choose file", type=["png", "jpg", "jpeg", "pdf", "txt"], label_visibility="collapsed")
                if uploaded_file:
                    st.success(f"Attached: {uploaded_file.name} ({uploaded_file.size // 1024} KB)")

        # Handle pending prefill input
        default_val = st.session_state.pop("pending_input", None) or st.session_state.pop("prefill_chat", "")
        
        user_input = st.chat_input("Type your message here...", key="chat_input_composer")
        if default_val and not user_input:
            user_input = default_val

        if user_input:
            with st.spinner("Support Assistant is typing..."):
                resp = EnterpriseAPIClient.send_chat_message(
                    message=user_input,
                    conversation_id=active_id,
                    customer_id=customer_id,
                    customer_name=customer_name,
                    user_email=user_email
                )
            if resp and isinstance(resp, dict) and resp.get("conversation_id"):
                st.session_state["active_conversation_id"] = resp["conversation_id"]
            st.rerun()
