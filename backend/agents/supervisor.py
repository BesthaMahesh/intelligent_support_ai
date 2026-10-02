from typing import Dict, Any, List

class SupervisorAgent:
    """
    Supervisor Agent: Orchestrates the multi-agent system by selecting
    the optimal path and specialized agents for any customer interaction.
    """
    
    @staticmethod
    def plan(state: Dict[str, Any]) -> Dict[str, Any]:
        intent = state.get("intent", "general_faq")
        sentiment = state.get("sentiment", "neutral")
        urgency = state.get("urgency", "low")
        entities = state.get("entities", {})
        message = state.get("sanitized_message", "")

        required_agents: List[str] = []
        route_taken = "rag"

        # Case 1: Explicit Human Request or Critical Sentiment
        if intent == "human_agent_request" or urgency == "critical":
            route_taken = "human_escalation"
            required_agents = ["customer_agent", "escalation_agent", "response_agent"]
            return {
                "route_taken": route_taken,
                "required_agents": required_agents
            }

        has_order = bool(entities.get("order_id"))
        
        # Case 2: Complex multi-tool inquiry (e.g. payment + shipping + delay + previous contact)
        is_complex = (
            has_order and (
                (intent in ["delivery_delay", "complaint"] and ("payment" in message.lower() or "paid" in message.lower())) or
                (intent in ["payment_pending", "refund_request"] and ("ship" in message.lower() or "delayed" in message.lower())) or
                ("nobody helped" in message.lower() or "yesterday" in message.lower())
            )
        )

        if is_complex:
            route_taken = "multi_tool"
            required_agents = ["order_agent", "shipment_agent", "payment_agent", "customer_agent", "knowledge_agent", "response_agent"]
        
        # Case 3: Specific Transactional Inquiry
        elif has_order or intent in ["order_status", "delivery_delay", "payment_pending", "payment_failed", "cancellation", "refund_request"]:
            route_taken = "business_tool"
            if intent in ["order_status"]:
                required_agents = ["order_agent", "shipment_agent", "response_agent"]
            elif intent in ["payment_pending", "payment_failed"]:
                required_agents = ["order_agent", "payment_agent", "knowledge_agent", "response_agent"]
            elif intent in ["delivery_delay"]:
                required_agents = ["order_agent", "shipment_agent", "knowledge_agent", "response_agent"]
            elif intent in ["refund_request", "cancellation"]:
                required_agents = ["order_agent", "payment_agent", "customer_agent", "knowledge_agent", "response_agent"]
            else:
                required_agents = ["order_agent", "knowledge_agent", "response_agent"]

        # Case 4: Pure Policy / FAQ / Informational Inquiry
        else:
            route_taken = "rag"
            required_agents = ["knowledge_agent", "response_agent"]

        return {
            "route_taken": route_taken,
            "required_agents": required_agents
        }
