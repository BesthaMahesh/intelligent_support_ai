from typing import Dict, Any, Optional

MOCK_PAYMENTS: Dict[str, Dict[str, Any]] = {
    "ORD-78231": {
        "order_id": "ORD-78231",
        "payment_gateway_ref": "PG_TXN_99812401",
        "payment_status": "SUCCESS",
        "amount": 24990.0,
        "currency": "INR",
        "gateway_response": "AUTHORIZED_CAPTURED",
        "minutes_since_payment": 45,
        "is_refund_eligible": True,
        "refund_status": "NONE"
    },
    "ORD-91245": {
        "order_id": "ORD-91245",
        "payment_gateway_ref": "PG_TXN_88192300",
        "payment_status": "SUCCESS",
        "amount": 72999.0,
        "currency": "INR",
        "gateway_response": "CAPTURED",
        "minutes_since_payment": 4320,
        "is_refund_eligible": True,
        "refund_status": "NONE"
    },
    "ORD-10022": {
        "order_id": "ORD-10022",
        "payment_gateway_ref": "PG_TXN_77263510",
        "payment_status": "SUCCESS",
        "amount": 119999.0,
        "currency": "INR",
        "gateway_response": "SETTLED",
        "minutes_since_payment": 17280,
        "is_refund_eligible": True,
        "refund_status": "NONE"
    }
}

def get_payment_status(order_id: str) -> Dict[str, Any]:
    """
    Retrieve authoritative payment status directly from payment gateway ledger.
    """
    clean_id = order_id.upper().strip()
    if clean_id in MOCK_PAYMENTS:
        return {
            "found": True,
            **MOCK_PAYMENTS[clean_id]
        }
        
    return {
        "found": True,
        "order_id": clean_id,
        "payment_gateway_ref": f"PG_TXN_{abs(hash(clean_id)) % 10000000}",
        "payment_status": "SUCCESS",
        "amount": 2499.0,
        "currency": "INR",
        "gateway_response": "CAPTURED",
        "minutes_since_payment": 60,
        "is_refund_eligible": True,
        "refund_status": "NONE"
    }

def check_refund_eligibility(order_id: str, amount: Optional[float] = None, reason: str = "") -> Dict[str, Any]:
    """
    Evaluate policy-based refund eligibility without executing payment transfer.
    """
    clean_id = order_id.upper().strip()
    payment = get_payment_status(clean_id)
    
    amount_to_refund = amount if amount is not None else payment.get("amount", 0.0)
    
    # Financial safety check: High refund requires supervisor
    requires_supervisor = amount_to_refund > 10000.0
    
    return {
        "order_id": clean_id,
        "eligible": payment.get("payment_status") == "SUCCESS",
        "max_refundable_amount": payment.get("amount", 0.0),
        "requested_amount": amount_to_refund,
        "requires_supervisor_approval": requires_supervisor,
        "reason_code": "CUSTOMER_CANCELLATION_OR_DISPUTE",
        "estimated_settlement_days": "3-5 business days"
    }
