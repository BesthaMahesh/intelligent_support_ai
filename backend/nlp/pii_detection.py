import re
from typing import Dict, Any, List

# Regex patterns for various PII classes
PII_PATTERNS = {
    "CREDIT_CARD": r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|6(?:011|5[0-9][0-9])[0-9]{12}|3[47][0-9]{13}|(?:[0-9]{4}[-\s]){3}[0-9]{4})\b',
    "BANK_ACCOUNT": r'\b(?:acc(?:ount)?\s*(?:no|number|#)?\s*[:\-]?\s*)(\d{9,18})\b',
    "AADHAAR": r'\b\d{4}\s\d{4}\s\d{4}\b',
    "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "PHONE": r'(?:\+?91[\-\s]?)?[6-9]\d{9}\b|\b(?:\+?1[\-\s]?)?\(?\d{3}\)?[\-\s]?\d{3}[\-\s]?\d{4}\b',
    "SSN": r'\b\d{3}-\d{2}-\d{4}\b'
}

def detect_and_protect_pii(text: str) -> Dict[str, Any]:
    """
    Detect PII entities in customer query, redact them, and produce safety metadata.
    Returns:
    {
        "pii_detected": bool,
        "redacted_text": str,
        "pii_types": List[str],
        "matches_count": int
    }
    """
    if not text:
        return {
            "pii_detected": False,
            "redacted_text": "",
            "pii_types": [],
            "matches_count": 0
        }
    
    redacted = text
    detected_types = []
    total_matches = 0
    
    # 1. Credit Card Numbers
    if re.search(PII_PATTERNS["CREDIT_CARD"], redacted):
        detected_types.append("CREDIT_CARD")
        redacted, count = re.subn(PII_PATTERNS["CREDIT_CARD"], "[REDACTED_CARD]", redacted)
        total_matches += count
        
    # 2. Bank Account
    if re.search(PII_PATTERNS["BANK_ACCOUNT"], redacted, flags=re.IGNORECASE):
        detected_types.append("BANK_ACCOUNT")
        redacted, count = re.subn(PII_PATTERNS["BANK_ACCOUNT"], r"acc [REDACTED_BANK_ACCOUNT]", redacted, flags=re.IGNORECASE)
        total_matches += count
        
    # 3. Aadhaar Number
    if re.search(PII_PATTERNS["AADHAAR"], redacted):
        detected_types.append("AADHAAR")
        redacted, count = re.subn(PII_PATTERNS["AADHAAR"], "[REDACTED_GOVT_ID]", redacted)
        total_matches += count

    # 4. SSN
    if re.search(PII_PATTERNS["SSN"], redacted):
        detected_types.append("SSN")
        redacted, count = re.subn(PII_PATTERNS["SSN"], "[REDACTED_SSN]", redacted)
        total_matches += count

    # 5. Email addresses (masked partially or redacted)
    # We redact if customer sends credentials or emails in chat
    if re.search(PII_PATTERNS["EMAIL"], redacted):
        detected_types.append("EMAIL")
        redacted, count = re.subn(PII_PATTERNS["EMAIL"], "[REDACTED_EMAIL]", redacted)
        total_matches += count
        
    # 6. Phone Numbers
    if re.search(PII_PATTERNS["PHONE"], redacted):
        detected_types.append("PHONE")
        redacted, count = re.subn(PII_PATTERNS["PHONE"], "[REDACTED_PHONE]", redacted)
        total_matches += count

    return {
        "pii_detected": len(detected_types) > 0,
        "redacted_text": redacted,
        "pii_types": detected_types,
        "matches_count": total_matches
    }
