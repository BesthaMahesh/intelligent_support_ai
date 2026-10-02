import re
import unicodedata

def normalize_text(text: str) -> str:
    """
    Normalize customer input:
    - Standardize Unicode characters
    - Standardize currency symbols (₹, Rs, Rs. -> INR)
    - Normalize Order IDs (e.g. ord 78231 -> ORD-78231)
    - Clean excessive whitespace
    """
    if not text:
        return ""
    
    # Unicode NFKD normalization
    norm = unicodedata.normalize("NFKC", text)
    
    # Currency normalization
    norm = re.sub(r'₹\s*([0-9,]+(\.[0-9]+)?)', r'INR \1', norm)
    norm = re.sub(r'(?:rs\.?|rupees|inr)\s*([0-9,]+(\.[0-9]+)?)', r'INR \1', norm, flags=re.IGNORECASE)
    
    # Order ID normalization (only when followed by digits/alphanumeric code, NOT english words like ordered)
    norm = re.sub(r'\b(?:order\s*#?|ord\s*[-#]?)\s*([0-9][A-Za-z0-9_-]{3,9})\b', r'ORD-\1', norm, flags=re.IGNORECASE)
    
    # Customer ID normalization
    norm = re.sub(r'\b(?:cust(?:omer)?\s*#?|cus\s*[-#]?)\s*([0-9][A-Za-z0-9_-]{2,8})\b', r'CUS-\1', norm, flags=re.IGNORECASE)
    
    # Normalize excessive whitespaces
    norm = re.sub(r'\s+', ' ', norm).strip()
    
    return norm
