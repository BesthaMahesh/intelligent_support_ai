from typing import Dict, Any

MOCK_CUSTOMERS: Dict[str, Dict[str, Any]] = {
    "CUS-8821": {
        "customer_id": "CUS-8821",
        "name": "Rajesh Kumar",
        "email": "customer@support.ai",
        "tier": "Gold Enterprise",
        "total_orders": 12,
        "lifetime_spend": 245000.0,
        "currency": "INR",
        "previous_tickets": 1,
        "last_ticket_id": "TKT-331002",
        "last_ticket_status": "OPEN",
        "last_ticket_topic": "Shipment Inquiry",
        "sentiment_history": ["neutral", "negative"],
        "account_standing": "IN_GOOD_STANDING"
    },
    "CUS-9410": {
        "customer_id": "CUS-9410",
        "name": "Priya Sharma",
        "email": "priya.sharma@example.com",
        "tier": "Platinum VIP",
        "total_orders": 24,
        "lifetime_spend": 580000.0,
        "currency": "INR",
        "previous_tickets": 0,
        "last_ticket_status": "NONE",
        "account_standing": "VIP"
    },
    "CUS-7712": {
        "customer_id": "CUS-7712",
        "name": "Anand Venkatesh",
        "email": "anand.v@example.com",
        "tier": "Standard",
        "total_orders": 3,
        "lifetime_spend": 32000.0,
        "currency": "INR",
        "previous_tickets": 0,
        "last_ticket_status": "NONE",
        "account_standing": "IN_GOOD_STANDING"
    }
}

def get_customer_history(customer_id: str) -> Dict[str, Any]:
    """
    Retrieve customer CRM profile, history, prior tickets, and tier status.
    """
    clean_id = customer_id.upper().strip()
    if clean_id in MOCK_CUSTOMERS:
        return {
            "found": True,
            **MOCK_CUSTOMERS[clean_id]
        }
        
    return {
        "found": True,
        "customer_id": clean_id,
        "name": "Valued Customer",
        "tier": "Standard",
        "total_orders": 2,
        "lifetime_spend": 15000.0,
        "currency": "INR",
        "previous_tickets": 0,
        "last_ticket_status": "NONE",
        "account_standing": "IN_GOOD_STANDING"
    }
