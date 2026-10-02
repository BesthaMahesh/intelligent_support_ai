import streamlit as st
import pandas as pd
import altair as alt
from frontend.components.header import render_page_header
from frontend.utils.api_client import EnterpriseAPIClient

def render_cost_and_latency():
    render_page_header(
        title="Cost, Token & Latency Analytics",
        subtitle="Production telemetry monitoring LLM token consumption, inference expense in INR, and latency distributions.",
        badge="Economics & SRE",
        badge_type="info"
    )

    data = EnterpriseAPIClient.get_cost_and_tokens()

    if not data.get("has_data", False):
        st.info("No LLM interactions recorded yet. Process customer queries to monitor token and latency telemetry.")
        return

    # Top Token & Cost Cards
    st.markdown("### 1. Financial & Token Consumption")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Cost (INR)", f"₹{data['total_cost_inr']:.2f}")
    c2.metric("Total Tokens", f"{data['total_tokens']:,}")
    c3.metric("Input Tokens", f"{data['total_input_tokens']:,}")
    c4.metric("Output Tokens", f"{data['total_output_tokens']:,}")
    c5.metric("Avg Tokens / Interaction", f"{data['avg_tokens_per_interaction']:,}")

    st.divider()

    # Latency Percentiles
    st.markdown("### 2. Latency Distributions (P50 / P95)")
    l1, l2, l3, l4 = st.columns(4)
    l1.metric("Mean Latency", f"{data['latency_avg_ms']} ms")
    l2.metric("P50 Latency (Median)", f"{data['latency_p50_ms']} ms")
    l3.metric("P95 Latency (Tail)", f"{data['latency_p95_ms']} ms")
    l4.metric("Total LLM Calls", data["total_llm_calls"])

    # Latency Chart
    lat_df = pd.DataFrame([
        {"Percentile": "P50 (Median)", "Latency (ms)": data["latency_p50_ms"]},
        {"Percentile": "Mean", "Latency (ms)": data["latency_avg_ms"]},
        {"Percentile": "P95 (95th %ile)", "Latency (ms)": data["latency_p95_ms"]}
    ])
    chart = alt.Chart(lat_df).mark_bar(cornerRadius=4, color="#3B82F6").encode(
        x=alt.X("Percentile:N", sort=None),
        y=alt.Y("Latency (ms):Q"),
        tooltip=["Percentile", "Latency (ms)"]
    ).properties(height=240)
    st.altair_chart(chart, use_container_width=True)
