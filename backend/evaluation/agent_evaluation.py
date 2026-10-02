import json
import os
import time
from pathlib import Path
from typing import Dict, Any, List
from backend.graph.workflow import support_graph
from backend.schemas.evaluation import AgentEvalResult

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def evaluate_agent_scenarios() -> AgentEvalResult:
    """
    Evaluate multi-agent orchestration, routing accuracy, and escalation decisions.
    """
    test_file = BASE_DIR / "data" / "evaluation" / "agent_test.json"
    if not os.path.exists(test_file):
        return AgentEvalResult(
            task_success_rate=0.0, valid_tool_call_rate=0.0, policy_violation_rate=0.0,
            avg_latency_ms=0.0, avg_cost_inr=0.0, total_scenarios=0
        )

    with open(test_file, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    successful_tasks = 0
    valid_tool_calls = 0
    total_tool_calls = 0
    policy_violations = 0
    latencies = []
    costs = []

    for scn in scenarios:
        msg = scn["customer_message"]
        expected_route = scn["expected_route"]
        expected_esc = scn["expected_human_escalation"]

        start = time.time()
        initial_state = {
            "request_id": f"EVAL-{scn['scenario_id']}",
            "conversation_id": f"CONV-{scn['scenario_id']}",
            "customer_id": "CUS-8821",
            "customer_name": "Rajesh Kumar",
            "user_email": "eval@support.ai",
            "message": msg,
            "sanitized_message": msg,
            "tool_results": {},
            "tools_executed": [],
            "retrieved_context": "",
            "retrieved_sources": [],
            "entities": {},
            "requires_human": False,
            "escalation_reason": None,
            "ticket_id": None,
            "response": "",
            "guardrails": {},
            "observability": {},
            "audit": {}
        }

        try:
            final_state = support_graph.invoke(initial_state)
            lat = round((time.time() - start) * 1000, 2)
            latencies.append(lat)
            costs.append(final_state.get("cost_inr", 0.04))

            route = final_state.get("route_taken")
            requires_human = final_state.get("requires_human", False)

            # Check correctness
            route_match = (route == expected_route) or (expected_route == "multi_tool" and route in ["multi_tool", "business_tool"])
            esc_match = (requires_human == expected_esc)
            
            if route_match and esc_match:
                successful_tasks += 1

            executed_tools = final_state.get("tools_executed", [])
            for t in executed_tools:
                total_tool_calls += 1
                if hasattr(t, "status") and t.status == "success":
                    valid_tool_calls += 1
                elif isinstance(t, dict) and t.get("status") == "success":
                    valid_tool_calls += 1

            if not final_state.get("guardrails", {}).get("output_passed", True):
                policy_violations += 1

        except Exception as e:
            print(f"Error running agent scenario {scn['scenario_id']}: {e}")

    total_scenarios = len(scenarios)
    success_rate = round(successful_tasks / max(1, total_scenarios), 4)
    valid_tool_rate = round(valid_tool_calls / max(1, total_tool_calls), 4) if total_tool_calls > 0 else 1.0
    violation_rate = round(policy_violations / max(1, total_scenarios), 4)
    avg_lat = round(sum(latencies) / max(1, len(latencies)), 2)
    avg_cost = round(sum(costs) / max(1, len(costs)), 4)

    return AgentEvalResult(
        task_success_rate=success_rate,
        valid_tool_call_rate=valid_tool_rate,
        policy_violation_rate=violation_rate,
        avg_latency_ms=avg_lat,
        avg_cost_inr=avg_cost,
        total_scenarios=total_scenarios
    )
