from typing import Dict, Any, List
from backend.config.settings import settings
from .prompt_injection import check_prompt_injection
from .pii import validate_pii_safety

def validate_input(text: str) -> Dict[str, Any]:
    """
    Input Guardrail:
    - Empty / whitespace check
    - Maximum character length limit
    - Prompt injection detection
    - Harmful / malicious patterns
    """
    violations: List[str] = []
    
    if not text or not text.strip():
        return {
            "passed": False,
            "violations": ["Input message cannot be empty."],
            "sanitized_text": ""
        }

    if len(text) > settings.MAX_INPUT_CHARS:
        violations.append(f"Input exceeds maximum allowed length of {settings.MAX_INPUT_CHARS} characters.")

    injection_res = check_prompt_injection(text)
    if injection_res["detected"]:
        violations.append(f"Adversarial prompt injection pattern detected: '{injection_res['pattern']}'")

    # Clean PII
    pii_res = validate_pii_safety(text)
    sanitized_text = pii_res["clean_text"]

    passed = len(violations) == 0

    return {
        "passed": passed,
        "violations": violations,
        "sanitized_text": sanitized_text,
        "prompt_injection_detected": injection_res["detected"]
    }
