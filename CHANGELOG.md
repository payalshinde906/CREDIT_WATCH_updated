# CreditDataWatch — Complete Changelog

---

## v1.0 — February 11, 2026

### UI & PO Enhancements

#### My Account Page
- Added "Add New PO" and "Clear" buttons under profile section
- Added PO History table matching CSV structure with live updates
- Table columns: PO No, Order Date, Currency, Payment, Supplier, Addresses, Item Summary

#### Purchase Orders CSV Import
- Extended columns support: `order_currency`, `supplier_address`, `item_summary`, `delivery_address`, `invoice_address`, `order_date`, `status`, `notes`, `document_url`

#### Backend
- Added dedicated columns on `PurchaseOrder`: `supplier_address`, `delivery_address`, `invoice_address`
- Startup migration ensures columns exist

#### Email OTP & Security
- Email-based OTP flows for login and email change
- API no longer exposes OTP codes — delivered via SMTP

**Files touched:** `Account.jsx`, `PurchaseOrders.jsx`, `CSVImportModal.jsx`, `Login.jsx`, `core.py`, `main.py`, `auth.py`, `otp_service.py`

---

## v1.1 — February 26, 2026

### Developer/Admin Access & Invitations

#### Developer/Admin Bootstrap
- Permanent developer/admin account reinforced (`payalshinde906@gmail.com`)
- Full access bypass via role/admin flags
- Idempotent bootstrap ensures account, company, flags on every startup
- Added `recreate_dev_admin.py` script
- Admin guard updated in `dependencies.py`

#### Invitation Emails
- HTML email sending for invitations
- Link built from `FRONTEND_URL` with fallback to `localhost:3000`

#### Invitations Management
- `PUT /api/v1/admin/invitations/{id}` — update invitation
- `DELETE /api/v1/admin/invitations/{id}` — delete invitation
- UI: removed Token column, added Actions column with inline Edit/Delete
- Added `adminApi.updateInvitation`, `adminApi.deleteInvitation` to `apiClient.js`

#### Accept Invitation Flow
- `GET /api/v1/invitations/verify?token=...`
- `POST /api/v1/invitations/accept`
- New page `/accept-invite` with token verification and password form
- Clear 4xx errors for invalid/expired/mismatch

#### Database Migrations
- `gstin` set to `NOT NULL`
- Dropped unique indexes on `gstin` to allow multiple employees per company
- Added `subscription_bypass`, `full_access` bypass flags
- Added `drop_users_gstin_unique.py` utility script

---

## v1.2 — March 1, 2026

### Vendor Notifications & BCI

#### Vendor Notifications on PO Creation
- Vendors receive `PO_CREATED` notification when PO is created
- Includes: PO number, vendor name, company name, amount, dates
- Persisted in `notifications` table
- Sent via email using SMTP

#### BCI + Ollama AI Integration
- Verified BCI scoring integrated with Ollama AI
- Raw JSON returned: `score`, `grade`, `risk`
- Timestamp-based aggregation from all POs
- Safe fallback if AI fails

---

## v1.3 — March 4, 2026

### UI Enhancements

#### Purchase Orders Page
- Added Business Credibility Index card on PO page header
- Score progress bar, Grade badge, Risk icons
- Highlighted pending PO rows with amber background
- Quick filters: All, Open, Pending, Closed
- Icon-based actions: Edit, Archive, Delete, Mark Paid
- Dynamic refresh on `poChanged` events

#### Credibility Index Page
- Prominent header card with search and filters
- Extended table: Score (progress bar), Grade (badge), Risk (icons), PO Fulfillment, Performance (stars)
- Populates from PO Management by aggregating unique vendors
- Client-side score/grade/risk/fulfillment/stars computation

#### Email Improvements
- Standardized From header: `CreditDataWatch <no-reply@creditdatawatch.com>`
- Enriched PO emails: PO Number, Vendor, GSTIN, Amount, Due Date, Status, Credibility Index

---

## v1.4 — March 5, 2026

### Vendor Contact Fields & Reminders

#### Vendor Contact Fields
- Added Vendor Email ID and Vendor Mobile Number to Add PO and Edit PO forms
- Backend: `vendor_email`, `vendor_phone` columns added to `PurchaseOrder`
- All CRUD endpoints updated to accept/return new fields

#### Manual Send Reminder
- Send Reminder button in Actions column (Open/Pending POs only)
- Confirmation dialog before sending
- `POST /api/v1/purchase-orders/{po_id}/send-reminder` endpoint
- Returns 400 if PO closed/paid or no vendor email

#### Automatic Scheduled Reminders
- Integrated into daily background scheduler (`_daily_tasks_runner`)
- Sends reminder on configured days before due date
- Daily reminder after due date until PO closed

#### Admin PO Reminder Config
- New page `/admin/po-reminders`
- Configure "before due date" days (7, 3, 2, 1 etc.)
- Toggle daily after-due reminders
- `POReminderConfig` model with `before_days` JSON array

#### Bug Fixes
- Fixed CORS error blocking frontend from backend
- Fixed HTTP 500 on Archive PO (missing columns)
- CSV Import: per-row try/catch, descriptive errors, duplicate/invalid checks

---

## v1.5 — March 6, 2026

### Database & AI Chatbot

#### Backend/Database
- Fixed `.env` override to use PostgreSQL consistently
- Dropped UNIQUE index on `purchase_orders(po_number)` to allow duplicates
- Added SQLite → PostgreSQL migration script
- Auth refresh endpoint hardened — always returns JSON

#### AI Chatbot
- Floating 💬 chat button on every page
- Slide-up chat panel with conversation history
- Typing indicator during Ollama response
- New endpoint: `POST /api/v1/chat`
- Full app knowledge system prompt with 14 sections, all roles, all routes
- Graceful fallback if Ollama unavailable

#### Loading Spinner
- Full-screen spinner during Save, Edit, Archive, Delete, Import
- Reusable `LoadingSpinner.jsx` component

---

## v1.6 — March 12, 2026

### SOP PDF Chatbot & Credibility Fixes

#### SOP PDF Chatbot Integration
- Uploaded CreditDataWatch SOP PDF to backend
- Created `pdf_service.py` to extract text from PDF
- Added `/sop-upload` and `/sop-status` endpoints
- Created `SOPUpload.jsx` at `/admin/sop-upload`
- Chatbot answers from actual SOP PDF (8000 char context)
- Correctly answers membership pricing, star ratings, vendor policies

#### Credibility Index Fix
- List now shows vendor names from Purchase Orders
- Unique vendors fetched directly from `purchase_orders` table
- Each vendor shows Score, Grade, Risk, PO Fulfillment, Stars from real PO data

#### Credibility Detail View Redesign
- 5 metric cards: Credit Score ring, Risk badge, PO Fulfillment bar, Stars, Credit Limit
- 3 tabs: Overview, Financials, AI Report
- AI Recommendation: verdict (Recommended/Caution/Not Recommended) + bullet reasons from Ollama
- Fixed detail page to look up vendors by name from POs

#### Bug Fixes
- Fixed Master Admin subscription bypass on credibility routes
- Fixed View button passing company name instead of UUID
- Fixed route conflict on credibility endpoint
- Fixed SOP upload auth error (cookie-based auth)

---

## v2.0 — March 12–13, 2026

### Auto-Sync Vendor to Credibility Index

#### Credibility Debugging & Fixes
- Fixed blank Credibility Index page
- Fixed View button (disabled → MASTER_ADMIN bypass added)
- Fixed View URL (company name → UUID)
- Fixed missing imports in `CredibilityDetail.jsx`
- Fixed fetch URLs (relative → absolute `http://localhost:8000`)
- Fixed AI Recommendation endpoint (`/api/v1/chat` → `/api/v1/credibility/{id}/ai-analysis`)
- Fixed AI fallback verdict logic
- Fixed Master Admin bypass on list + detail endpoints
- Added `POST /api/v1/credibility/recalculate` endpoint
- Fixed `aggregate_metrics` to read vendor POs correctly
- Removed duplicate Test Company from database
- Fixed PO Fulfillment display field names

#### Auto-Sync Pipeline
- Fixed HTTP 500 on PO creation (removed broken credibility trigger)
- Added `sync_vendor_credibility` helper using direct `asyncpg` connection
- Auto-creates company in `companies` table when PO is created
- Auto-calculates credibility score after every PO save/update/pay
- Added `recalc_for_company` static method to `CredibilityService`
- Backfilled all existing vendors into `companies` + credibility index

#### Ollama AI Scoring
- Connected Ollama `llama3` to `score_with_ai` in `credibility_service.py`
- Sends vendor PO metrics to `llama3`
- Returns Score, Grade, Risk, Stars, AI Summary
- Math-based fallback if Ollama fails
- Fixed score calculation (2/2 paid → Score 100, Grade A)

---

## v2.1 — April 1, 2026

### New Features

#### Feature 1 — Days Left Column
- Added Days Left column in PO table
- Formula: `effective_due_date = due_date + payment_window_days`
- `Days Left = effective_due_date - today`
- Colors: 🟢 green → 🟠 orange → 🔴 red (overdue/due today)

#### Feature 2 — Payment Window per PO
- Added `payment_window_days` column to `purchase_orders` (default 50)
- Inline editable column with ✏️ → ✅ ❌
- Disabled for Paid/Closed POs
- Extending window removes overdue status dynamically

#### Feature 3 — Dynamic Status Display
- Status badge calculated dynamically using effective due date
- Extended payment window → "Open" not "Overdue"
- Paid POs always show "Paid"

#### Feature 4 — Admin Settings
- Added `app_settings` table
- `GET/POST /api/v1/admin/settings` endpoints
- Global payment window threshold for color coding

#### Feature 5 — Legal Notice in Reminder
- Legal notice checkbox in reminder modal
- Admin edits template before sending
- Legal notice sent as PDF attachment (ReportLab)
- Legal notice text removed from email body
- Added `legal_notice_sent_at` column to `purchase_orders`
- ⚖️ badge on PO row when legal notice sent

#### Feature 6 — Legal Support Button
- ⚖️ advocate icon button between Archive and Delete
- Sends all PO details to `payalshinde906@gmail.com`
- Confirmation popup before sending
- Auto-triggers when PO becomes overdue (background scheduler)
- Button turns green when already sent
- Disabled for Paid POs
- Added `legal_support_requested_at` column

#### Feature 7 — Legal Notice PDF
- Created `server/app/services/legal_notice_service.py`
- Professional PDF via ReportLab
- Auto-fills: Vendor, PO Number, Amount, Due Date, Company, Date
- Sent as `Legal_Notice_{po_number}.pdf` attachment
- Temp PDF deleted after sending

---

## v2.2 — April 2, 2026

### Fixes & Infrastructure

#### Scheduled Reminders Fix
- Moved to frequent runner (every 60 seconds)
- Fixed lifespan integration in `main.py`

#### Email Service Fix
- Port 465 → SSL (`smtplib.SMTP_SSL`)
- Added `send_email_with_attachment` function
- All SMTP config from `.env`

#### .env Team Support
- Created `server/.env.example`
- `config.py` updated with `extra = "allow"`
- All hardcoded values → `.env` with fallbacks
- Fixed `SECRET_KEY` as static value (prevents token invalidation on restart)
- Updated `.gitignore`
- Created `README_SETUP.md` for team onboarding

#### Ollama Auto-Start
- `ensure_ollama_running()` — auto-starts if not running
- `ensure_model_available()` — auto-pulls `llama3` if missing
- Added Ollama to Windows startup via registry
- Both called in lifespan startup

#### Post Fresh-Clone Fixes
- Fixed credibility index 500 (UUID not company name)
- Fixed PO creation 400 (missing `payment_window_days`)
- Verified all DB columns exist after clone
- OTP email fixed with correct SSL settings