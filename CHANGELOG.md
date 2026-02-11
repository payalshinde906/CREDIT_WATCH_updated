# Change Log

Date: 2026-02-11

## Enhancements

- My Account page UI:
  - Added "Add New PO" and "Clear" buttons under the profile section
  - Added PO History table that matches the CSV structure and auto-updates
  - Table shows: Purchase_Order_No, Order_Date, Order_Currency, Purchase_Payment, Supplier_Name, Supplier_Address, Item_Summary, Delivery_Address, Invoice_Address
  - Live updates: history refreshes after create/update/delete/archive

- Purchase Orders CSV Import:
  - Accepts extended columns and maps to backend: order_currency, supplier_address, item_summary, delivery_address, invoice_address, order_date, status, notes, document_url

## Backend

- Persistent storage for PO address fields:
  - Added dedicated columns on PurchaseOrder: supplier_address, delivery_address, invoice_address
  - Startup migration ensures columns exist on supported databases
  - Routes return/read these fields directly (no structured notes)
  - Create/Update PO accepts and persists the address fields

## Email OTP and Security

- Email-based OTP flows implemented for login and email change
- API no longer exposes OTP codes; OTP delivered via SMTP

## Files Touched

- Client:
  - client/src/pages/account/Account.jsx
  - client/src/pages/PurchaseOrders.jsx
  - client/src/components/po/CSVImportModal.jsx
  - client/src/pages/auth/Login.jsx (Email OTP mode)

- Server:
  - server/app/models/__init__.py (PurchaseOrder columns)
  - server/app/routes/core.py (PO CRUD with address fields)
  - server/app/main.py (startup migration for new columns)
  - server/app/routes/auth.py (hide otp_code in responses)
  - server/app/services/otp_service.py (SMTP delivery)

## Notes

- To view PO History: visit /account and click "Add New PO"
- To add or import POs: use /purchase-orders page; Account history updates automatically
