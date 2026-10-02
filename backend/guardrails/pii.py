from backend.nlp.pii_detection import detect_and_protect_pii

def validate_pii_safety(text: str) -> dict:
    """
    Ensure no raw credit cards, bank accounts, or government IDs are present in output text.
    """
    pii_check = detect_and_protect_pii(text)
    is_safe = True
    critical_pii = ["CREDIT_CARD", "BANK_ACCOUNT", "AADHAAR", "SSN"]
    
    violations = []
    for p_type in pii_check["pii_types"]:
        if p_type in critical_pii:
            is_safe = False
            violations.append(f"Unprotected {p_type} detected")
            
    return {
        "is_safe": is_safe,
        "clean_text": pii_check["redacted_text"],
        "violations": violations
    }
