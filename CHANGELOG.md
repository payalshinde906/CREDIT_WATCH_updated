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

---

Date: 2026-02-26

## Developer/Admin Access & Bootstrap

- Permanent developer/admin account reinforced (email: payalshinde906@gmail.com)
  - Full access bypass via role/admin flags and explicit email recognition
  - Idempotent bootstrap ensures account, company, flags, and demotes legacy admin
  - Script added to re‑create/ensure developer admin on demand
    - server/scripts/recreate_dev_admin.py
  - Admin guard updated to allow developer email as admin
    - server/app/dependencies.py

## Invitation Emails

- Added HTML email sending and invitation email function
  - Reuses existing SMTP configuration
  - Link built from FRONTEND_URL with safe fallback http://localhost:3000
  - server/app/services/email_service.py, server/app/config.py
- Invitation creation sends email; failures log warnings without failing request
  - server/app/routes/admin.py

## Invitations Management (Admin)

- Update & Delete invitation endpoints
  - PUT /api/v1/admin/invitations/{id}
  - DELETE /api/v1/admin/invitations/{id}
  - server/app/routes/admin.py
- Client API additions
  - adminApi.updateInvitation, adminApi.deleteInvitation
  - client/src/services/api/apiClient.js
- UI updates (Invitations table)
  - Removed Token column
  - Added Actions column with inline Edit (role, expiry hours) and Delete (with confirm)
  - client/src/pages/admin/TeamManagement.jsx

## Accept Invitation Flow

- Public verification and acceptance APIs
  - GET /api/v1/invitations/verify?token=...
  - POST /api/v1/invitations/accept
  - POST /api/v1/invitations/accept-invitation (strict: token, email, role, company_id, password, confirm_password)
  - Clear 4xx errors for invalid/expired/mismatch/constraint violations (no 500s)
  - server/app/routes/invitations.py
- Frontend page & route
  - New page /accept-invite
  - Verifies token; if valid, shows disabled Email/Role and password form; on success redirects to login
  - client/src/pages/auth/AcceptInvite.jsx, client/src/routes/index.jsx
- Client API additions
  - invitations.verify, invitations.accept, invitations.acceptStrict
  - client/src/services/api/apiClient.js

## Database & Migrations

- Users table migration (idempotent):
  - Ensures gstin is NOT NULL
  - Drops any users‑level unique indexes/constraints involving gstin to allow multiple employees per company GSTIN
  - Creates a non‑unique index on (gstin, company_id) for efficient filtering
  - Adds permanent bypass flags: subscription_bypass, full_access
  - server/app/main.py
- Utility script for DB index adjustment (Postgres)
  - server/scripts/drop_users_gstin_unique.py

## API Mounts & Wiring

- Invitations router mounted under /api/v1
  - server/app/main.py, server/app/routes/__init__.py

## Notes

- Developer/admin bypass recognized in both backend and frontend route protections
- Invitation acceptance handles collisions and constraint errors gracefully
- No UI layout changes beyond Invitations table actions; all existing styles preserved

---

Date: 2026-03-01

## Vendor Notifications on New PO Creation

- When a new Purchase Order is created via POST /api/v1/purchase-orders, vendors now receive a PO_CREATED notification in addition to the company admin.
- Notification includes:
  - PO number
  - Vendor name
  - Company name (who created the PO)
  - Amount
  - Order/creation date
  - Due date
- Persisted in the notifications table (user_id = vendor admin/contact, type = PO_CREATED, related_po_id, is_read = false).
- Optionally sent via email using the existing SMTP/email logic.
- Existing admin notifications remain unchanged.

## Notification System Enhancement

- Notifications now target both company admins and vendors where applicable.
- Maintains server-triggered, DB-persisted logic.
- Ensures full transparency for POs and due dates.
- No client-side-only logic introduced; backend-controlled.

## Testing & Verification Enhancements

- Added test steps for verifying vendor notifications:
  - Check DB persistence (notifications table)
  - Validate correct related_po_id linkage
  - Confirm is_read = false
  - Optional email confirmation via SMTP
  - Ensure no cross-company/vendor leakage
- Ensures company admin notifications remain unchanged.

## BCI Verification / AI Integration

- Verified that BCI scoring is integrated with Ollama AI:
  - Raw JSON returned with score, grade, risk
  - Frontend parses and displays the values in the BCI table
  - Timestamp-based aggregation from all POs (paid_on_time, paid_late, overdue, unpaid)
  - Safe fallback applied if AI fails; page remains crash-free
- No structural changes to BCI logic were needed, but AI-hardened verification added.

## Summary of Newly Added Features

- Vendor notifications on PO creation.
- Enhanced notification system (admin + vendor).
- Test steps for verifying notifications and email delivery.
- BCI + Ollama AI integration verification and safety checks.

---

Date: 2026-03-04

## UI Enhancements – Purchase Orders

- Added prominent Business Credibility Index card on PO page header
  - Score progress bar with color bands
  - Grade badge
  - Risk icons: ✅ Low, ⚠️ Medium, ❌ High
  - Inline tooltips to explain Score/Grade
  - Fulfillment mini-stats within the card: Total, Completed, Pending (mini bars)
- Highlighted pending PO rows with subtle amber background and ⏳ icon
- Added quick filters: All, Open, Pending, Closed
- Replaced textual actions with intuitive icons for Edit, Archive, Delete, and Mark Paid
- Dynamic refresh on poChanged events for stats and card
- File: client/src/pages/PurchaseOrders.jsx

## UI Enhancements – Credibility Index

- Prominent header/card with accent border, subtle shadow, and icon
- Search and filters (All risks, sort by Top/Lowest) integrated into the card
- Table columns expanded:
  - Score (mini progress bar + number)
  - Grade (badge)
  - Risk (icons)
  - PO Fulfillment (green = paid, amber = pending, with “x/y Paid”)
  - Performance (1–5 star rating based on completion rate)
- Populates companies from PO Management by aggregating unique vendors
- Client-side computation of score/grade/risk/fulfillment/stars
- Real-time updates wired to poChanged without extra API calls
- File: client/src/pages/CredibilityIndex.jsx

## Emails – Sender Consistency and Content

- Standardized From header for all emails:
  - From: CreditDataWatch <no-reply@creditdatawatch.com> (via SENDER_NAME/SENDER_EMAIL)
  - Applies to registration, OTPs, invitations, and PO notifications
- Enriched PO emails on create and update:
  - Content includes PO Number, Vendor, GSTIN, Amount, Due Date, Status
  - Includes Credibility Index when available and “Pending” alert if applicable
  - Sent to buyer company admins and vendor admins (where applicable)
- Files:
  - server/app/services/email_service.py
  - server/app/config.py
  - server/app/routes/core.py
  - server/scripts/test_registration_sender.py (utility for local sender verification)

## Notes

- No changes to PO creation logic or SMTP configuration; only From header standardization and email content additions
- All UI additions adhere to existing Tailwind design system and avoid new libraries


Date: 2026-03-05

### Purchase Orders — Vendor Contact Fields
- Added **Vendor Email ID** (email input with format validation) and **Vendor Mobile Number** 
  (tel input with E.164 formatting) to the Add PO form in `PurchaseOrders.jsx`, 
  placed below Vendor Name field
- Added same fields to `EditPOModal.jsx`, pre-populated from existing PO data on open
- Backend: added `vendor_email` and `vendor_phone` columns to `PurchaseOrder` model
- Backend: idempotent startup migration in `main.py` ensures columns exist without 
  breaking existing data
- Backend: `create_po`, `list_pos`, `get_po`, `update_po` in `core.py` all updated 
  to accept, validate, and return the new fields

### Purchase Orders — Manual Send Reminder
- Added **Send Reminder** button to the Actions column on each PO row in the list
- Button is visible only on Open and Pending POs — hidden on Closed and Paid POs
- On click: shows confirmation dialog with vendor email before sending
- On confirm: sends immediate reminder email to vendor via existing `EmailService`
- If no vendor email is set on the PO: shows warning, no API call is made
- Backend: new endpoint `POST /api/v1/purchase-orders/{po_id}/send-reminder`
  - Returns 400 if PO is closed or paid
  - Returns 400 if no vendor email is configured
  - Returns 200 on successful email dispatch
- Frontend: added `sendPOReminder(poId)` function to `apiClient.js`

### Purchase Orders — Automatic Scheduled Reminders
- Integrated vendor reminder emails into existing daily background scheduler 
  (`main.py: _daily_tasks_runner`)
- Sends reminder email to vendor on each configured day before PO due date
- Sends daily reminder email after due date if enabled, until PO is closed or paid
- All existing user notification emails remain unchanged

### Admin — PO Reminder Configuration Page
- New admin page at `/admin/po-reminders` (admin-protected route)
- Admin can add and remove "before due date" day entries dynamically (e.g. 7, 3, 2, 1 days)
- Admin can toggle daily "after due date" reminders on or off
- Config is persisted globally and applied to all POs
- Backend: new `POReminderConfig` model with `before_days` (JSON array) and 
  `after_due_daily_enabled` (boolean), created on startup via SQLAlchemy
- Backend: `GET /api/v1/admin/po-reminders` returns current config or creates default
- Backend: `PUT /api/v1/admin/po-reminders` saves updated config
- Frontend: `POReminderConfig.jsx` — new admin config page
- Frontend: `getPOReminderConfig()` and `updatePOReminderConfig(data)` added to `apiClient.js`
- Frontend: route registered and admin-protected in `routes/index.jsx`

### Bug Fixes
- Fixed CORS error blocking frontend (`localhost:3000`) from reaching backend (`localhost:8000`) 
  — added `CORSMiddleware` in `main.py`
- Fixed HTTP 500 on Archive PO — caused by missing `vendor_email` and `vendor_phone` 
  columns in database; corrected startup migration in `main.py` to run reliably before 
  the app serves requests

### CSV Import Fix
- Added per-row try/catch so a single failing row no longer crashes the entire import
- Added descriptive error messages per row instead of generic HTTP 500
- Added defensive checks: duplicate PO number, invalid GSTIN, amount formatting 
  (strips ₹ and commas), date format validation, vendor not found

---

Date: 2026-03-06

## Backend – Database & Environment

- Fixed environment precedence so server/.env overrides OS env and uses PostgreSQL
  - Updated settings loader to `override=True` for `.env`
  - File: server/app/config.py
- Idempotent startup continues to create/verify PurchaseOrder columns on PostgreSQL
  - File: server/app/main.py
- Dropped any UNIQUE index on `purchase_orders(po_number)` to allow duplicates
  - Idempotent and PostgreSQL-safe block
  - File: server/app/main.py

## Data Migration – SQLite → PostgreSQL

- Added one-time migration script to move data from `server/test.db` to PostgreSQL
  - Migrates `purchase_orders`, `companies`, `users`, `invitations` by ID, skipping existing rows
  - File: server/scripts/migrate_sqlite_to_postgres.py

## Auth – Refresh Endpoint Hardening

- Wrapped refresh token route with JSON error handling
  - Always returns JSON for errors (no plain text)
  - Works with PostgreSQL user lookup and validates token type/payload
  - File: server/app/routes/auth.py

## Purchase Orders – UI Columns

- Added Email and Mobile columns after Vendor in the PO list table
  - Shows `vendor_email` / `vendor_phone` or “—” if empty
  - Files: client/src/pages/PurchaseOrders.jsx

## CSV Import – Logging

- Added per-row `console.error('[PO Import]', ...)` logging for failed rows
  - File: client/src/components/po/CSVImportModal.jsx

## Duplicate PO Numbers

- Allowed multiple POs with the same PO number (non-unique reference)
  - Removed duplicate check in storage flow while preserving all validations
  - Files: server/app/routes/core.py, server/app/main.py


## [2026-03-06] — AI Chatbot (Ollama) + UI Improvements

### AI Chatbot — CreditDataWatch Assistant
- Added floating 💬 chat button fixed to bottom-right corner of every page
- Chat panel slides up with header "CreditDataWatch Assistant"
- User messages aligned right, bot messages aligned left
- Typing indicator (animated dots) while waiting for response
- Conversation history kept in session, clears on close and reopen
- If Ollama is unavailable, shows friendly message instead of crashing
- New file: client/src/components/common/ChatAssistant.jsx
- New function in apiClient.js: sendChatMessage(message)
- New backend endpoint: POST /api/v1/chat
- Added to MainLayout.jsx so it appears on every page

### AI Chatbot — Full App Knowledge System Prompt
- Updated system prompt in core.py with complete CreditDataWatch knowledge:
  - All 14 sections: Home, Auth, Dashboard, POs, Invoices, Credibility 
    Index, Defaulters, Credit Reports, Wallet, Membership, Account, Admin
  - All user roles explained: Master Admin, Company Admin, Finance, 
    Operations, Standard User, Guest
  - Background tasks: daily 2 AM automation (BCI recalc, overdue 
    alerts, vendor reminders)
  - All route paths included (/dashboard, /wallet, /admin/team etc.)
- Enforced clean numbered-step response format — no asterisks or markdown
- Off-topic questions redirect politely back to app features
- Ollama model: llama3 running locally at http://localhost:11434

### Loading Spinner
- Added centered full-screen spinner with semi-transparent overlay
- Appears during: Save PO, Edit PO, Archive, Delete, Send Reminder,
  Import CSV, page load, Admin Reminder Config save
- Spinner always hides on both success and error — user never gets stuck
- New reusable component: LoadingSpinner.jsx

