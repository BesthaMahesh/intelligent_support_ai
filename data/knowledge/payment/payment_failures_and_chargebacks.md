# Payment Failures, Double Debits & Chargeback Handling

**Document ID**: KB-PAY-002  
**Category**: payment  
**Version**: 2.5  
**Last Updated**: 2026-09-25  
**Authoritative Source**: Treasury & Payment Systems Operations  

## 1. Multiple Debits for Single Order Placement
When a customer experiences multiple debits from their bank account or card for a single order attempt:
- **Primary Transaction**: The successfully captured transaction reference will link to the confirmed Order ID.
- **Secondary / Ghost Authorizations**: Uncaptured duplicate authorizations are automatically released by our payment gateway within 2 hours.
- **Bank Settlement Turnaround**: Funds will reflect back in the customer's account within 3 to 5 business days without requiring manual support intervention.

## 2. UPI Transaction Timeouts
- UPI network time-outs occur when the National Payments Corporation of India (NPCI) switch experiences peak latency.
- If the amount is deducted from customer UPI VPA but no Order ID is displayed within 15 minutes, our auto-refund engine issues a reverse credit command (RRN-linked).

## 3. Disputed Charges & Chargebacks
- Customers are encouraged to contact Intelligent Support AI prior to raising bank chargebacks to avoid account security flags.
- Any legitimate claim is resolved within 24 hours via instant reversal or replacement credit.
