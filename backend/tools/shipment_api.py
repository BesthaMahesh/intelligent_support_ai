from typing import Dict, Any

MOCK_SHIPMENTS: Dict[str, Dict[str, Any]] = {
    "ORD-78231": {
        "order_id": "ORD-78231",
        "shipment_status": "PROCESSING",
        "carrier": "BlueDart Express",
        "tracking_number": "PENDING_DISPATCH",
        "expected_dispatch": "2026-10-03",
        "expected_delivery": "2026-10-05",
        "is_dispatch_overdue": False,
        "warehouse_location": "Bengaluru Hub 2"
    },
    "ORD-91245": {
        "order_id": "ORD-91245",
        "shipment_status": "NOT_SHIPPED",
        "carrier": "Delhivery Express",
        "tracking_number": "DEL-99214022",
        "expected_dispatch": "2026-10-01", # Past dispatch date!
        "expected_delivery": "2026-10-03",
        "is_dispatch_overdue": True,
        "delay_reason": "Regional warehouse inventory reconciliation bottleneck",
        "warehouse_location": "Chennai Fulfillment Center"
    },
    "ORD-10022": {
        "order_id": "ORD-10022",
        "shipment_status": "DELIVERED",
        "carrier": "BlueDart Express",
        "tracking_number": "BD-88410291",
        "expected_dispatch": "2026-09-21",
        "delivered_on": "2026-09-24 16:30:00",
        "is_dispatch_overdue": False,
        "warehouse_location": "Mumbai Mega Center"
    }
}

def get_shipment_status(order_id: str) -> Dict[str, Any]:
    """
    Retrieve live logistics and shipment telemetry for an order.
    """
    clean_id = order_id.upper().strip()
    if clean_id in MOCK_SHIPMENTS:
        return {
            "found": True,
            **MOCK_SHIPMENTS[clean_id]
        }
        
    return {
        "found": True,
        "order_id": clean_id,
        "shipment_status": "IN_TRANSIT",
        "carrier": "BlueDart Express",
        "tracking_number": f"TRK-{abs(hash(clean_id)) % 10000000}",
        "expected_dispatch": "2026-10-02",
        "expected_delivery": "2026-10-06",
        "is_dispatch_overdue": False,
        "warehouse_location": "Bengaluru Central Hub"
    }
