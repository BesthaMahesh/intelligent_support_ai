from langgraph.graph import StateGraph, END
from backend.graph.state import AgentState
from backend.graph.nodes import (
    nlp_and_input_guardrail_node,
    supervisor_routing_node,
    tool_execution_node,
    knowledge_retrieval_node,
    business_rules_node,
    response_generation_node,
    output_guardrails_node
)

def create_support_graph():
    """
    Build the enterprise LangGraph workflow for Intelligent Support AI.
    """
    workflow = StateGraph(AgentState)

    # 1. Add nodes
    workflow.add_node("nlp_and_guardrails", nlp_and_input_guardrail_node)
    workflow.add_node("supervisor_router", supervisor_routing_node)
    workflow.add_node("tool_executor", tool_execution_node)
    workflow.add_node("knowledge_retriever", knowledge_retrieval_node)
    workflow.add_node("business_rules_engine", business_rules_node)
    workflow.add_node("response_generator", response_generation_node)
    workflow.add_node("output_guardrails", output_guardrails_node)

    # 2. Add edges
    workflow.set_entry_point("nlp_and_guardrails")
    workflow.add_edge("nlp_and_guardrails", "supervisor_router")
    workflow.add_edge("supervisor_router", "tool_executor")
    workflow.add_edge("tool_executor", "knowledge_retriever")
    workflow.add_edge("knowledge_retriever", "business_rules_engine")
    workflow.add_edge("business_rules_engine", "response_generator")
    workflow.add_edge("response_generator", "output_guardrails")
    workflow.add_edge("output_guardrails", END)

    return workflow.compile()

support_graph = create_support_graph()
