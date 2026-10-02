import streamlit as st
import pandas as pd
from frontend.components.header import render_page_header
from backend.evaluation.llm_evaluation import run_full_system_evaluation, get_latest_evaluation_summary

def render_ai_evaluation():
    render_page_header(
        title="AI Evaluation & Quality Benchmarks",
        subtitle="Empirical evaluation across NLP Intent, NER, Sentiment, RAG Grounding, and Agent Orchestration.",
        badge="Quality Assurance",
        badge_type="info"
    )

    col_btn, col_time = st.columns([1, 2])
    with col_btn:
        if st.button("🧪 Run Full Benchmark Suite", type="primary", use_container_width=True):
            with st.spinner("Executing live evaluation on test datasets..."):
                run_full_system_evaluation()
            st.success("Benchmark suite execution completed!")

    summary = get_latest_evaluation_summary()
    with col_time:
        if summary and summary.last_evaluated_at:
            st.caption(f"Last Evaluated: **{summary.last_evaluated_at}**")

    st.divider()

    # 1. Intent Classification Metrics
    st.markdown("### 1. Intent Classification Performance")
    intent_eval = summary.intent_evaluation
    if intent_eval:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Accuracy", f"{intent_eval.accuracy * 100:.1f}%")
        c2.metric("Precision (Macro)", f"{intent_eval.precision_macro * 100:.1f}%")
        c3.metric("Recall (Macro)", f"{intent_eval.recall_macro * 100:.1f}%")
        c4.metric("Macro F1-Score", f"{intent_eval.f1_macro * 100:.1f}%")
    else:
        st.info("Not evaluated yet.")

    st.divider()

    # 2. NER & Sentiment Quality
    st.markdown("### 2. Named Entity Recognition & Sentiment")
    ner_eval = summary.ner_evaluation
    sent_eval = summary.sentiment_evaluation
    c1, c2, c3, c4 = st.columns(4)
    if ner_eval:
        c1.metric("NER Precision", f"{ner_eval.precision * 100:.1f}%")
        c2.metric("NER Recall", f"{ner_eval.recall * 100:.1f}%")
        c3.metric("NER F1-Score", f"{ner_eval.f1 * 100:.1f}%")
    if sent_eval:
        c4.metric("Sentiment Macro-F1", f"{sent_eval.macro_f1 * 100:.1f}%")

    st.divider()

    # 3. Production RAG & Retrieval Quality
    st.markdown("### 3. RAG Retrieval & Answer Groundedness")
    rag_eval = summary.rag_evaluation
    if rag_eval:
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Recall@3", f"{rag_eval.recall_at_k * 100:.1f}%")
        r2.metric("Precision@3", f"{rag_eval.precision_at_k * 100:.1f}%")
        r3.metric("MRR (Mean Reciprocal Rank)", f"{rag_eval.mrr:.3f}")
        r4.metric("NDCG@3", f"{rag_eval.ndcg:.3f}")

        g1, g2, g3, g4 = st.columns(4)
        g1.metric("Answer Groundedness", f"{rag_eval.answer_groundedness * 100:.1f}%")
        g2.metric("Faithfulness", f"{rag_eval.faithfulness * 100:.1f}%")
        g3.metric("Context Recall", f"{rag_eval.context_recall * 100:.1f}%")
        g4.metric("Answer Relevance", f"{rag_eval.answer_relevance * 100:.1f}%")

        if rag_eval.query_details:
            with st.expander("🔍 Detailed RAG Test Queries Breakdown", expanded=False):
                st.dataframe(pd.DataFrame(rag_eval.query_details), use_container_width=True)

    st.divider()

    # 4. Agentic System & Economics
    st.markdown("### 4. Multi-Agent Orchestration & Tool Execution")
    agent_eval = summary.agent_evaluation
    if agent_eval:
        a1, a2, a3, a4, a5 = st.columns(5)
        a1.metric("Task Success Rate", f"{agent_eval.task_success_rate * 100:.1f}%")
        a2.metric("Valid Tool Call Rate", f"{agent_eval.valid_tool_call_rate * 100:.1f}%")
        a3.metric("Policy Violation Rate", f"{agent_eval.policy_violation_rate * 100:.1f}%")
        a4.metric("Avg Latency", f"{agent_eval.avg_latency_ms:.0f} ms")
        a5.metric("Avg Cost (INR)", f"₹{agent_eval.avg_cost_inr:.4f}")
