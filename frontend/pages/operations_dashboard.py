import streamlit as st
import pandas as pd
import altair as alt
from frontend.components.header import render_page_header
from frontend.utils.api_client import EnterpriseAPIClient

def render_operations_dashboard():
    render_page_header(
        title="Support Operations Intelligence",
        subtitle="Internal real-time monitoring of AI autonomy, resolution rates, and queue telemetry.",
        badge="Operations Command",
        badge_type="info"
    )

    metrics = EnterpriseAPIClient.get_dashboard_metrics()
    
    if not metrics.get("has_data", False):
        st.info("No operational activity data available yet.")
        return

    # Internal KPI Summary Cards
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Total Conversations", metrics["total_conversations"])
    with col2:
        st.metric("AI-Assisted", metrics["ai_assisted_conversations"])
    with col3:
        st.metric("Open Tickets", metrics["open_tickets"])
    with col4:
        st.metric("Human Escalations", metrics["human_escalations"])
    with col5:
        st.metric("Avg Latency", f"{metrics['avg_response_time_ms']} ms")
    with col6:
        st.metric("Resolution Rate", f"{metrics['resolution_rate_pct']}%")

    st.divider()

    # Charts Layout
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        st.markdown("### Intent Distribution")
        intents_data = metrics.get("intents_distribution", {})
        if intents_data:
            df_intent = pd.DataFrame(list(intents_data.items()), columns=["Intent", "Count"])
            chart_intent = alt.Chart(df_intent).mark_bar(cornerRadius=4, color="#2563EB").encode(
                x=alt.X("Count:Q", title="Volume"),
                y=alt.Y("Intent:N", sort="-x", title="Detected Intent"),
                tooltip=["Intent", "Count"]
            ).properties(height=240)
            st.altair_chart(chart_intent, use_container_width=True)
        else:
            st.caption("No intent data recorded.")

    with row1_col2:
        st.markdown("### Sentiment Breakdown")
        sentiments_data = metrics.get("sentiments_distribution", {})
        if sentiments_data:
            df_sent = pd.DataFrame(list(sentiments_data.items()), columns=["Sentiment", "Count"])
            color_scale = alt.Scale(
                domain=["positive", "neutral", "negative", "highly_negative"],
                range=["#10B981", "#64748B", "#F59E0B", "#EF4444"]
            )
            chart_sent = alt.Chart(df_sent).mark_arc(innerRadius=45).encode(
                theta=alt.Theta("Count:Q"),
                color=alt.Color("Sentiment:N", scale=color_scale),
                tooltip=["Sentiment", "Count"]
            ).properties(height=240)
            st.altair_chart(chart_sent, use_container_width=True)
        else:
            st.caption("No sentiment data recorded.")

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        st.markdown("### AI vs Human Assistance")
        ai_vs_human = metrics.get("ai_vs_human", {})
        if ai_vs_human:
            df_ai = pd.DataFrame(list(ai_vs_human.items()), columns=["Channel", "Count"])
            chart_ai = alt.Chart(df_ai).mark_bar(cornerRadius=4).encode(
                x=alt.X("Channel:N", title="Channel"),
                y=alt.Y("Count:Q", title="Cases"),
                color=alt.Color("Channel:N", scale=alt.Scale(range=["#3B82F6", "#F97316"]))
            ).properties(height=220)
            st.altair_chart(chart_ai, use_container_width=True)

    with row2_col2:
        st.markdown("### Escalation & Resolution Rate")
        rates_df = pd.DataFrame([
            {"Metric": "Resolution Rate", "Percentage": metrics["resolution_rate_pct"]},
            {"Metric": "Escalation Rate", "Percentage": metrics["escalation_rate_pct"]}
        ])
        chart_rates = alt.Chart(rates_df).mark_bar(cornerRadius=4).encode(
            x=alt.X("Metric:N"),
            y=alt.Y("Percentage:Q", scale=alt.Scale(domain=[0, 100])),
            color=alt.Color("Metric:N", scale=alt.Scale(range=["#10B981", "#EF4444"]))
        ).properties(height=220)
        st.altair_chart(chart_rates, use_container_width=True)
