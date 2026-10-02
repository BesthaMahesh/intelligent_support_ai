# Payment Verification & Gateway Policy

**Document ID**: KB-PAY-001  
**Category**: payment  
**Version**: 1.8  
**Last Updated**: 2026-09-10  
**Authoritative Source**: Treasury & Payment Systems  

## Payment Methods Supported
- UPI (Google Pay, PhonePe, Paytm, BHIM)
- Credit & Debit Cards (Visa, MasterCard, RuPay, American Express)
- Net Banking (All major Indian scheduled commercial banks)
- Digital Wallets & No-Cost EMI options

## Payment Deducted but Order Still Pending (Reconciliation Window)
- **15-Minute Webhook Reconciliation**: In rare instances of banking network latency, funds are debited from the customer's account while the webhook takes up to 15 minutes to confirm the merchant order.
- **Within 15 Minutes**: Customers are advised that transaction synchronization is in progress. The order will reflect as 'Confirmed' automatically once webhook ACK is received.
- **Beyond 15 Minutes**: If the order remains pending after 15 minutes despite money debit, our automated payment reconciliation engine verifies the transaction reference with the banking partner and raises a tracking ticket.
- **Failed Transactions**: If the payment gateway marks the transaction as failed, the deducted funds are automatically reversed by the issuing bank within 3 to 7 business days.
