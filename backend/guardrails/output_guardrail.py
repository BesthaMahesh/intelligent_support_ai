import re
from typing import Dict, Any, List
from .pii import validate_pii_safety

HALLUCINATED_CLAIMS = [
    r'as\s+an\s+ai\s+language\s+model',
    r'i\s+do\s+not\s+have\s+access\s+to\s+real-time',
    r'openai\s+policies',
    r'internal\s+secret\s+database'
]

def validate_output(
    response_text: str,
    retrieved_contexts: List[str] = None,
    tool_results: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Output Guardrail:
    - PII Leakage Detection
    - Unsupported / meta-prompt leakage
    - Grounding validation check
    - Formats safe output
    """
    violations = []
    
    if not response_text or not response_text.strip():
        return {
            "passed": False,
            "violations": ["Response text is empty."],
            "sanitized_response": "I apologize, but I am unable to generate a valid response at this moment. Please let me connect you to a support specialist."
        }

    # 1. PII Check on Generated Output
    pii_check = validate_pii_safety(response_text)
    sanitized = pii_check["clean_text"]
    if not pii_check["is_safe"]:
        violations.extend(pii_check["violations"])

    # 2. Meta LLM Leakage Check
    for pattern in HALLUCINATED_CLAIMS:
        if re.search(pattern, response_text, flags=re.IGNORECASE):
            violations.append(f"Output contains disallowed conversational meta-claim pattern: {pattern}")
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE).strip()

    # 3. Grounding check: if response claims a specific order status or refund, make sure tools or RAG were present
    # If the response states "Your order ORD-XXXX has been refunded" but no refund tool ran, flag it.
    if re.search(r'refunded\s+inr\s+[0-9]+', sanitized, flags=re.IGNORECASE) and not tool_results:
        violations.append("Response makes financial refund commitment without executed tool verification.")

    passed = len(violations) == 0

    return {
        "passed": passed,
        "violations": violations,
        "sanitized_response": sanitized,
        "grounding_passed": "financial refund commitment" not in " ".join(violations)
    }
