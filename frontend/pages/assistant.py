import streamlit as st
from frontend.components.header import render_page_header
from frontend.utils.api_client import EnterpriseAPIClient

def render_ai_assistant():
    render_page_header(
        title="AI Support Assistant",
        subtitle="Ask questions, resolve customer requests, retrieve business information, and assist with support operations.",
        badge="Autonomous Agent",
        badge_type="info"
    )

    if "assistant_messages" not in st.session_state:
        st.session_state["assistant_messages"] = [
            {
                "role": "assistant",
                "content": "Hello! I am your Intelligent Support AI assistant. How can I assist you with orders, returns, payments, or policy inquiries today?",
                "metadata": {}
            }
        ]

    st.caption("Recommended Prompts:")
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        if st.button("📦 Return Policy for Electronics (FAQ/RAG)", use_container_width=True):
            st.session_state["selected_prompt"] = "What is the return policy for electronics?"
        if st.button("💳 Payment Pending Reconciliation (Order/Payment API)", use_container_width=True):
            st.session_state["selected_prompt"] = "My payment was deducted but my order is still showing Payment Pending. Order ID is ORD-78231."
    with p_col2:
        if st.button("🚚 Where is order ORD-78231? (Logistics API)", use_container_width=True):
            st.session_state["selected_prompt"] = "Where is order ORD-78231?"
        if st.button("🚨 Complex Delay & Escalation Scenario (Multi-Tool + Human Review)", use_container_width=True):
            st.session_state["selected_prompt"] = "I ordered a laptop three days ago and paid ₹72,999. The payment was successful but the order hasn't shipped. I contacted support yesterday and nobody helped me. Order ID ORD-91245."

    st.divider()

    for msg in st.session_state["assistant_messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
            meta = msg.get("metadata", {})
            if meta:
                with st.expander("🔍 View AI Processing Details (Multi-Agent Trace)", expanded=False):
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Intent", meta.get("intent", "N/A"))
                    c2.metric("Sentiment", meta.get("sentiment", "N/A"))
                    c3.metric("Urgency", meta.get("urgency", "N/A"))
                    c4.metric("Latency", f"{meta.get('observability', {}).get('total_latency_ms', 0)} ms")

                    if meta.get("route_taken"):
                        st.markdown(f"**Route Taken**: `{meta.get('route_taken')}`")
                    if meta.get("ticket_id"):
                        st.markdown(f"**Escalation Ticket Generated**: `{meta.get('ticket_id')}`")
                    if meta.get("retrieved_sources"):
                        st.markdown("**Retrieved Knowledge Sources**:")
                        for src in meta.get("retrieved_sources", []):
                            st.markdown(f"- 📄 **{src.get('title')}** ({src.get('document_id')}) - Score: `{src.get('relevance_score')}`")
                    if meta.get("tools_executed"):
                        st.markdown("**Executed Business Tools**:")
                        for t in meta.get("tools_executed", []):
                            t_dict = t if isinstance(t, dict) else t.dict()
                            st.markdown(f"- ⚙️ Tool: `{t_dict.get('tool_name')}` (Status: `{t_dict.get('status')}`)")
                            if t_dict.get('result'):
                                st.json(t_dict.get('result'))

    prompt_to_send = st.session_state.pop("selected_prompt", None)
    user_input = st.chat_input("What can I help you with?") or prompt_to_send

    if user_input:
        st.session_state["assistant_messages"].append({"role": "user", "content": user_input, "metadata": {}})
        
        with st.chat_message("user"):
            st.write(user_input)
            
        with st.spinner("Analyzing request through NLP & Multi-Agent orchestration..."):
            res = EnterpriseAPIClient.send_chat_message(
                message=user_input,
                customer_id="CUS-8821",
                customer_name="Rajesh Kumar"
            )
            
        st.session_state["assistant_messages"].append({
            "role": "assistant",
            "content": res.get("response", ""),
            "metadata": res
        })
        st.rerun()
