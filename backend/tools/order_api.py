from typing import Dict, Any, Optional

MOCK_ORDERS: Dict[str, Dict[str, Any]] = {
    "ORD-78231": {
        "order_id": "ORD-78231",
        "customer_id": "CUS-8821",
        "customer_name": "Rajesh Kumar",
        "product": "Sony WH-1000XM5 Wireless Headphones",
        "category": "Electronics",
        "amount": 24990.0,
        "currency": "INR",
        "order_status": "PAYMENT_PENDING",
        "payment_status": "SUCCESS",
        "payment_method": "UPI - HDFC Bank",
        "order_date": "2026-10-02T14:45:00",
        "minutes_since_placed": 45,
        "notes": "Payment gateway received transaction confirmation. Order status synchronization in progress."
    },
    "ORD-91245": {
        "order_id": "ORD-91245",
        "customer_id": "CUS-8821",
        "customer_name": "Rajesh Kumar",
        "product": "Apple MacBook Air M3 (16GB, 512GB SSD)",
        "category": "Electronics",
        "amount": 72999.0,
        "currency": "INR",
        "order_status": "CONFIRMED",
        "payment_status": "SUCCESS",
        "payment_method": "Credit Card - ICICI",
        "order_date": "2026-09-29T10:15:00",
        "minutes_since_placed": 4320, # 3 days ago
        "notes": "Paid in full. Awaiting warehouse dispatch."
    },
    "ORD-10022": {
        "order_id": "ORD-10022",
        "customer_id": "CUS-9410",
        "customer_name": "Priya Sharma",
        "product": "Samsung Galaxy S24 Ultra",
        "category": "Electronics",
        "amount": 119999.0,
        "currency": "INR",
        "order_status": "DELIVERED",
        "payment_status": "SUCCESS",
        "payment_method": "NetBanking",
        "order_date": "2026-09-20T11:00:00",
        "delivery_date": "2026-09-24T16:30:00",
        "notes": "Delivered in original packaging. Eligible for return until 2026-10-24."
    },
    "ORD-45100": {
        "order_id": "ORD-45100",
        "customer_id": "CUS-7712",
        "customer_name": "Anand Venkatesh",
        "product": "Ergonomic Office Chair",
        "category": "Furniture",
        "amount": 14500.0,
        "currency": "INR",
        "order_status": "SHIPPED",
        "payment_status": "SUCCESS",
        "payment_method": "Debit Card",
        "order_date": "2026-09-30T09:00:00",
        "notes": "In transit via BlueDart Courier."
    }
}

def get_order_status(order_id: str) -> Dict[str, Any]:
    """
    Retrieve authoritative order status and transactional metadata.
    """
    clean_id = order_id.upper().strip()
    if clean_id in MOCK_ORDERS:
        return {
            "found": True,
            **MOCK_ORDERS[clean_id]
        }
    
    # Return simulated record for test IDs
    return {
        "found": True,
        "order_id": clean_id,
        "customer_id": "CUS-8821",
        "customer_name": "Rajesh Kumar",
        "product": "Standard Retail Item",
        "category": "General",
        "amount": 2499.0,
        "currency": "INR",
        "order_status": "CONFIRMED",
        "payment_status": "SUCCESS",
        "payment_method": "UPI",
        "order_date": "2026-10-01T12:00:00",
        "notes": "Order recorded in active database."
    }
