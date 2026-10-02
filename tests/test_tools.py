import pytest
from backend.tools.order_api import get_order_status
from backend.tools.payment_api import get_payment_status, check_refund_eligibility
from backend.tools.shipment_api import get_shipment_status
from backend.tools.crm_api import get_customer_history

def test_order_api():
    order = get_order_status("ORD-78231")
    assert order["found"] is True
    assert order["order_id"] == "ORD-78231"
    assert order["payment_status"] == "SUCCESS"

def test_payment_api():
    payment = get_payment_status("ORD-78231")
    assert payment["payment_status"] == "SUCCESS"

def test_refund_guardrail_eligibility():
    # Refund > 10,000 must require supervisor
    res = check_refund_eligibility("ORD-91245", amount=72999.0)
    assert res["requires_supervisor_approval"] is True

def test_shipment_api():
    shipment = get_shipment_status("ORD-91245")
    assert shipment["found"] is True
    assert shipment["is_dispatch_overdue"] is True

def test_crm_api():
    crm = get_customer_history("CUS-8821")
    assert crm["found"] is True
    assert crm["name"] == "Rajesh Kumar"
