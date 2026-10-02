import re
from typing import Dict, Any

PROMPT_INJECTION_PATTERNS = [
    r'(?i)\bignore\s+(all\s+)?(previous|prior|above)\s+instructions\b',
    r'(?i)\bdisregard\s+(all\s+)?(previous|system)\s+prompts\b',
    r'(?i)\byou\s+are\s+now\s+(DAN|unrestricted|jailbroken|godmode)\b',
    r'(?i)\bprint\s+(your\s+)?(system\s+prompt|instructions|initial\s+prompt)\b',
    r'(?i)\brepeat\s+the\s+words\s+above\b',
    r'(?i)\breveal\s+(internal|secret|hidden)\s+api\s+keys\b',
    r'(?i)\bbypass\s+(guardrails|safety|security)\s+filters\b',
    r'(?i)\bformat\s*:\s*execute_code\b'
]

def check_prompt_injection(text: str) -> Dict[str, Any]:
    """
    Detect adversarial prompt injection attempts in customer input.
    """
    if not text:
        return {"detected": False, "pattern": None}
        
    for pattern in PROMPT_INJECTION_PATTERNS:
        match = re.search(pattern, text)
        if match:
            return {
                "detected": True,
                "pattern": pattern,
                "matched_text": match.group(0)
            }
            
    return {"detected": False, "pattern": None}
