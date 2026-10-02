import re
from typing import Dict, Any

# Unicode ranges for Indian and international scripts
SCRIPT_RANGES = {
    "Tamil": (0x0B80, 0x0BFF),
    "Hindi": (0x0900, 0x097F), # Devanagari
    "Telugu": (0x0C00, 0x0C7F),
    "Kannada": (0x0C80, 0x0CFF),
    "Malayalam": (0x0D00, 0x0D7F),
    "Bengali": (0x0980, 0x09FF),
}

# Romanized / Transliterated keywords
ROMANIZED_KEYWORDS = {
    "Tamil": ["vanakkam", "eppadi", "irukeenga", "enoda", "order", "panam", "thirumba", "vara", "illai", "kedaikala", "romba"],
    "Hindi": ["namaste", "kya", "mera", "paise", "kat", "gaye", "order", "nahi", "aaya", "kab", "milega", "kripya", "madad"],
    "Telugu": ["namaskaram", "naa", "order", "dabbu", "raledu", "eppudu", "vastundi", "sahayam"],
}

def detect_language(text: str) -> Dict[str, Any]:
    """
    Detect the language of the customer query with confidence.
    Supports native scripts (Tamil, Hindi, Telugu, etc.) as well as English and Romanized text.
    """
    if not text or not text.strip():
        return {"language": "English", "confidence": 1.0}
    
    clean_text = text.strip()
    total_chars = len(clean_text)
    
    # 1. Check Unicode script counts
    script_counts = {lang: 0 for lang in SCRIPT_RANGES}
    for char in clean_text:
        code = ord(char)
        for lang, (start, end) in SCRIPT_RANGES.items():
            if start <= code <= end:
                script_counts[lang] += 1
                break
                
    max_script_lang = max(script_counts, key=script_counts.get)
    if script_counts[max_script_lang] > 0:
        confidence = min(0.99, round(script_counts[max_script_lang] / max(1, total_chars - clean_text.count(" ")), 2))
        if confidence > 0.3:
            return {"language": max_script_lang, "confidence": max(0.85, confidence)}

    # 2. Check Romanized / Transliterated text
    lower_text = clean_text.lower()
    words = re.findall(r'\b\w+\b', lower_text)
    total_words = len(words)
    
    if total_words > 0:
        for lang, keywords in ROMANIZED_KEYWORDS.items():
            matches = sum(1 for w in words if w in keywords)
            if matches >= 2 or (matches == 1 and total_words <= 3):
                conf = round(min(0.95, 0.65 + (matches / total_words) * 0.3), 2)
                return {"language": lang, "confidence": conf}

    # Default to English
    return {"language": "English", "confidence": 0.98}
