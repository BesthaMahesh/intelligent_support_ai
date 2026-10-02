import re
from typing import Dict, Any, Optional
from backend.schemas.chat import EntitySchema

PRODUCT_CATALOG = [
    "laptop", "smartphone", "phone", "iphone", "macbook", "headphone", "headphones",
    "earbuds", "smartwatch", "watch", "camera", "tablet", "ipad", "television", "tv",
    "electronics", "refrigerator", "shoes", "shirt", "clothing", "ac", "air conditioner"
]

def extract_entities(text: str) -> EntitySchema:
    """
    Extract structured entities from customer message.
    """
    if not text:
        return EntitySchema()

    clean_text = text.strip()
    entities = EntitySchema()
    custom = {}

    # 1. Order ID (ORD-XXXXX or ORD XXXXX with digits, avoid English words like ordered)
    order_match = re.search(r'\b(ORD[-\s]?[0-9][0-9A-Za-z_-]{3,9})\b', clean_text, flags=re.IGNORECASE)
    if not order_match:
        order_match = re.search(r'\b(?:order\s*#?\s*|ord\s*[-#]?\s*)([0-9][0-9A-Za-z_-]{3,9})\b', clean_text, flags=re.IGNORECASE)

    if order_match:
        val = order_match.group(1).upper().replace(" ", "-")
        if not val.startswith("ORD-"):
            val = f"ORD-{val.replace('ORD', '').lstrip('-')}"
        entities.order_id = val

    # 2. Customer ID (CUS-XXXXX or CUS XXXXX with digits)
    cus_match = re.search(r'\b(CUS[-\s]?[0-9][0-9A-Za-z_-]{2,8})\b', clean_text, flags=re.IGNORECASE)
    if not cus_match:
        cus_match = re.search(r'\b(?:cust(?:omer)?\s*#?\s*|cus\s*[-#]?\s*)([0-9][0-9A-Za-z_-]{2,8})\b', clean_text, flags=re.IGNORECASE)
    if cus_match:
        val = cus_match.group(1).upper().replace(" ", "-")
        if not val.startswith("CUS-"):
            val = f"CUS-{val.replace('CUS', '').lstrip('-')}"
        entities.customer_id = val

    # 3. Product
    lower = clean_text.lower()
    for prod in PRODUCT_CATALOG:
        if re.search(rf'\b{prod}\b', lower):
            entities.product = prod
            break

    # 4. Amount & Currency (₹72,999, INR 72999, Rs 2499, 50,000)
    amount_match = re.search(r'(?:₹|INR|Rs\.?)\s*([0-9,]+(?:\.[0-9]+)?)', clean_text, flags=re.IGNORECASE)
    if not amount_match:
        amount_match = re.search(r'(?:paid|amount of|worth)\s*(?:INR|Rs\.?|₹)?\s*([0-9,]+(?:\.[0-9]+)?)', clean_text, flags=re.IGNORECASE)
    
    if amount_match:
        try:
            num_str = amount_match.group(1).replace(",", "")
            entities.amount = float(num_str)
            entities.currency = "INR"
        except ValueError:
            pass

    # 5. Payment Status
    if re.search(r'\b(successful|success|completed|paid|debited|deducted)\b', lower):
        if re.search(r'(deducted|debited).*?(pending)', lower):
            entities.payment_status = "deducted_pending"
        else:
            entities.payment_status = "successful"
    elif re.search(r'\b(failed|declined|error)\b', lower):
        entities.payment_status = "failed"
    elif re.search(r'\b(pending|processing)\b', lower):
        entities.payment_status = "pending"

    # 6. Shipping Status
    if re.search(r'\b(not shipped|hasn\'t shipped|not dispatched|delayed|undelivered)\b', lower):
        entities.shipping_status = "not_shipped"
    elif re.search(r'\b(in transit|out for delivery|shipped|dispatched)\b', lower):
        entities.shipping_status = "in_transit"
    elif re.search(r'\b(delivered|received)\b', lower):
        entities.shipping_status = "delivered"

    # 7. Date & Time context
    date_match = re.search(r'\b(yesterday|today|three days ago|two days ago|last week|[0-9]+\s*days?\s*ago)\b', lower)
    if date_match:
        entities.date = date_match.group(1)

    # 8. Issue Summary
    issues = []
    if "payment deducted" in lower or "deducted" in lower:
        issues.append("payment deducted")
    if "order pending" in lower or "still pending" in lower:
        issues.append("order pending")
    if "not shipped" in lower or "hasn't shipped" in lower:
        issues.append("shipment delayed")
    if "nobody helped" in lower or "contacted support" in lower:
        issues.append("unresolved prior contact")
    if issues:
        entities.issue = ", ".join(issues)

    entities.custom_entities = custom
    return entities
