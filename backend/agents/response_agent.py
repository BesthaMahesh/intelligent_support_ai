import json
from typing import Dict, Any
from backend.llm.provider import get_llm_provider
from backend.prompts.system_prompts import (
    CURRENT_PROMPT_VERSION,
    ENTERPRISE_SYSTEM_PROMPT,
    RESPONSE_GENERATION_PROMPT
)

class ResponseAgent:
    """
    Response Agent: Synthesizes verified tools, retrieved policies, and business rules
    into a grounded, professional, and multilingual customer response.
    """
    
    @staticmethod
    def generate(state: Dict[str, Any]) -> Dict[str, Any]:
        llm = get_llm_provider()
        
        # Prepare tool results string
        tool_results_json = json.dumps(state.get("tool_results", {}), indent=2)
        retrieved_context = state.get("retrieved_context", "No direct policy document retrieved.")
        rule_guidance = state.get("business_rule_result", {}).get("policy_guidance", "Provide standard polite support.")
        
        prompt = RESPONSE_GENERATION_PROMPT.format(
            customer_message=state.get("sanitized_message", ""),
            language=state.get("language", "English"),
            intent=state.get("intent", "general_faq"),
            intent_confidence=state.get("intent_confidence", 1.0),
            sentiment=state.get("sentiment", "neutral"),
            urgency=state.get("urgency", "low"),
            entities=json.dumps(state.get("entities", {})),
            tool_results=tool_results_json,
            retrieved_context=retrieved_context,
            business_rule_guidance=rule_guidance
        )

        gen_result = llm.generate(
            prompt=prompt,
            system_prompt=ENTERPRISE_SYSTEM_PROMPT,
            temperature=0.2
        )

        return {
            "response": gen_result.content,
            "llm_result": gen_result,
            "prompt_version": CURRENT_PROMPT_VERSION
        }
