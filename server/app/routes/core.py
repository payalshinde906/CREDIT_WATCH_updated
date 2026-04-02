"""
User and feature routes (stub with core endpoints)
"""
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import re
from datetime import datetime, timezone
from app.database import get_db
from app.models import User, PurchaseOrder, DefaulterCase, CreditReport, Settlement
from app.schemas import UpdateProfileRequest, UserProfileResponse, SubscriptionResponse
from app.services import UserService, OTPService, AccessControlService
from app.utils import ResponseFormatter, format_phone_e164
from app.dependencies import get_current_user
from app.exceptions import UnauthorizedFeature
from app.utils.phone import is_valid_phone
import uuid
from sqlalchemy import or_
from app.services.email_service import EmailService, send_email_with_attachment
from app.services.legal_notice_service import generate_legal_notice_pdf
from app.models import Notification
import os

async def sync_vendor_credibility(vendor_name: str, db): 
    try: 
        import asyncpg, uuid as uuid_lib 
        from datetime import datetime
        if not vendor_name or not vendor_name.strip(): 
            return 
        
        vendor_name = vendor_name.strip() 
        print(f"[SYNC] Starting sync for: {vendor_name}") 
        
        conn = await asyncpg.connect('postgresql://postgres:2004@localhost:5432/creditdatawatch') 
        
        # Check if company exists by name or GSTIN
        existing = await conn.fetchrow( 
            'SELECT id, company_name, gstin FROM companies WHERE company_name = $1 OR gstin = $2', 
            vendor_name, 'PENDING' # Placeholder for GSTIN check
        ) 
        
        # If we have a PO, let's get the real GSTIN to check
        po_info = await conn.fetchrow(
            'SELECT gstin FROM purchase_orders WHERE vendor = $1 ORDER BY created_at DESC LIMIT 1',
            vendor_name
        )
        real_gstin = po_info['gstin'] if po_info else 'PENDING'

        # Re-check with real GSTIN if name search failed or we didn't have it
        if not existing and real_gstin != 'PENDING':
            existing = await conn.fetchrow(
                'SELECT id, company_name, gstin FROM companies WHERE gstin = $1',
                real_gstin
            )

        if not existing: 
            domain = f"{vendor_name.lower().replace(' ', '')}.com"
            company_id = str(uuid_lib.uuid4()) 
            now = datetime.utcnow()
            
            await conn.execute( 
                '''INSERT INTO companies (id, company_name, gstin, domain_name, created_at, is_verified) 
                   VALUES ($1, $2, $3, $4, $5, $6)''', 
                company_id, vendor_name, real_gstin, domain, now, False
            ) 
            print(f"[SYNC] Created company: {vendor_name} -> {company_id}") 
        else: 
            company_id = existing['id'] 
            print(f"[SYNC] Company exists: {existing['company_name']} ({existing['gstin']}) -> {company_id}") 
        
        await conn.close() 
        
        # Now recalc using ORM service 
        from app.services.credibility_service import CredibilityService 
        await CredibilityService.recalc_for_company(db, company_id) 
        await db.commit() 
        print(f"[SYNC] Credibility updated for: {vendor_name}") 
        
    except Exception as e: 
        import traceback 
        print(f"[SYNC ERROR] {vendor_name}: {e}") 
        traceback.print_exc() 

# Feature name constants
PO_MANAGEMENT = "PO_MANAGEMENT"
PO_FEATURE_NAME = "PO Management"
REPORT_OVERDUE = "REPORT_OVERDUE"
DEFAULTER_FEATURE_NAME = "Defaulter Reporting"
CREDIT_REPORT = "CREDIT_REPORT"
CREDIT_REPORT_FEATURE_NAME = "Credit Report"
SETTLEMENT = "SETTLEMENT"
SETTLEMENT_FEATURE_NAME = "Settlement"

# Error message constants
NOT_FOUND_ERROR = "not found"
PO_NOT_FOUND_ERROR = "Purchase order not found"
ACCESS_DENIED_ERROR = "Access denied"
CANNOT_UPDATE_REVIEWED = "Cannot update case that has been reviewed"
EITHER_GSTIN_PAN = "Either GSTIN or PAN must be provided"
INVALID_PAN_FORMAT = "Invalid PAN format"

# User routes
user_router = APIRouter()

@user_router.get("/admin/settings")
async def get_admin_settings(db: AsyncSession = Depends(get_db)):
    """Get application settings"""
    from app.models import AppSettings
    stmt = select(AppSettings).where(AppSettings.id == 'default')
    result = await db.execute(stmt)
    settings = result.scalars().first()
    if not settings:
        return ResponseFormatter.create_success(data={"payment_window_days": 50})
    return ResponseFormatter.create_success(data={"payment_window_days": settings.payment_window_days})

@user_router.post("/admin/settings")
async def update_admin_settings(req: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Update application settings (MASTER_ADMIN only)"""
    if current_user.role != "MASTER_ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")
    
    payment_window_days = req.get("payment_window_days")
    if payment_window_days is None:
        raise HTTPException(status_code=400, detail="payment_window_days is required")
        
    from app.models import AppSettings
    stmt = select(AppSettings).where(AppSettings.id == 'default')
    result = await db.execute(stmt)
    settings = result.scalars().first()
    
    if not settings:
        settings = AppSettings(id='default', payment_window_days=payment_window_days)
        db.add(settings)
    else:
        settings.payment_window_days = payment_window_days
        settings.updated_at = datetime.utcnow()
        
    await db.commit()
    return ResponseFormatter.create_success(message="Settings updated successfully")

@user_router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return ResponseFormatter.create_success(data=UserProfileResponse.model_validate(current_user).__dict__)

@user_router.options("/profile")
async def profile_options():
    # Empty response; CORSMiddleware will add CORS headers
    return JSONResponse(content={})

@user_router.put("/profile")
async def update_profile(req: UpdateProfileRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Update user profile"""
    user = await UserService.update_profile(current_user.id, req, db)
    return ResponseFormatter.create_success(data=UserProfileResponse.model_validate(user).__dict__)

@user_router.post("/phone-change/send-otp")
async def send_phone_change_otp(req: dict, current_user: User = Depends(get_current_user)):
    """Send OTP for phone change"""
    # Accept both 'new_phone' (from frontend) and 'phone' (for compatibility)
    new_phone = (req.get("new_phone") or req.get("phone") or "").strip()
    
    if not new_phone:
        from app.exceptions import InvalidPhone
        raise InvalidPhone("Phone number is required")
    
    # Try to format to E.164 first, then validate
    phone_e164 = format_phone_e164(new_phone)
    if not phone_e164:
        # If E.164 formatting fails, try validating as-is
        if not is_valid_phone(new_phone):
            from app.exceptions import InvalidPhone
            raise InvalidPhone(f"Invalid phone number format: {new_phone}. Please use format: +91XXXXXXXXXX")
        # If validation passes but formatting fails, use the original
        phone_e164 = new_phone
    
    # Send OTP via SMS (if configured) or email
    # Pass user email so OTP can be sent via email if SMS fails
    result = await OTPService.send_otp(phone_e164, purpose="phone_change", email=current_user.email)
    
    return ResponseFormatter.create_success(data={"sent": result["sent"], "message": result.get("message", "OTP sent")})

@user_router.post("/phone-change/verify-otp")
async def verify_phone_change_otp(req: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Verify OTP and change phone"""
    # Accept both 'new_phone' (from frontend) and 'phone' (for compatibility)
    new_phone = (req.get("new_phone") or req.get("phone") or "").strip()
    otp_code = (req.get("otp_code") or "").strip()
    
    if not new_phone:
        from app.exceptions import InvalidPhone
        raise InvalidPhone("Phone number is required")
    
    if not otp_code:
        from app.exceptions import InvalidOTP
        raise InvalidOTP("OTP code is required")
    
    # Format to E.164
    phone_e164 = format_phone_e164(new_phone) or new_phone
    
    # Verify OTP
    await OTPService.verify_otp(phone_e164, otp_code, purpose="phone_change")
    
    # Change phone
    await UserService.change_phone(current_user.id, phone_e164, db)
    return ResponseFormatter.create_success(message="Phone changed successfully")

@user_router.post("/email-change/send-otp")
async def send_email_change_otp(req: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Send OTP for email change"""
    new_email = (req.get("new_email") or req.get("email") or "").strip().lower()
    
    if not new_email or "@" not in new_email:
        from app.exceptions import InvalidEmail
        raise InvalidEmail("Valid email address is required")
    
    # Check if email is already in use
    from sqlalchemy import select
    stmt = select(User).where(User.email == new_email, User.id != current_user.id)
    result = await db.execute(stmt)
    if result.scalars().first():
        from app.exceptions import InvalidEmail
        raise InvalidEmail("Email address already in use")
    
    # Send OTP to both current and new email addresses
    result = await OTPService.send_otp_for_email_change(new_email, current_user.email)
    
    return ResponseFormatter.create_success(
        data={"sent": result["sent"]},
        message=result.get("message", "OTP sent to both email addresses")
    )

@user_router.post("/email-change/verify-otp")
async def verify_email_change_otp(req: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Verify OTP and change email"""
    new_email = (req.get("new_email") or req.get("email") or "").strip().lower()
    otp_code = (req.get("otp_code") or "").strip()
    
    if not new_email or "@" not in new_email:
        from app.exceptions import InvalidEmail
        raise InvalidEmail("Valid email address is required")
    
    if not otp_code:
        from app.exceptions import InvalidOTP
        raise InvalidOTP("OTP code is required")
    
    # Verify OTP
    await OTPService.verify_otp_for_email_change(new_email, otp_code)
    
    # Change email
    from app.services import UserService
    from app.schemas import UpdateProfileRequest
    await UserService.update_profile(
        current_user.id,
        UpdateProfileRequest(email=new_email),
        db
    )
    
    return ResponseFormatter.create_success(message="Email changed successfully")

@user_router.get("/subscription")
async def get_subscription(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get user subscription"""
    from app.models import Subscription
    role = str(getattr(current_user, "role", "")).upper()
    if role == "MASTER_ADMIN" or getattr(current_user, "subscription_bypass", False) or getattr(current_user, "full_access", False):
        from datetime import datetime
        data = {
            "id": current_user.id,
            "plan": "ADMIN_FREE",
            "is_active": True,
            "start_date": datetime.utcnow(),
            "expiry_date": None,
        }
        return ResponseFormatter.create_success(data=data)
    stmt = select(Subscription).where(Subscription.user_id == current_user.id)
    result = await db.execute(stmt)
    sub = result.scalars().first()
    if not sub:
        return ResponseFormatter.create_success(data=None)
    return ResponseFormatter.create_success(data=SubscriptionResponse.model_validate(sub).__dict__)

# Purchase Order routes
po_router = APIRouter()

@po_router.post("")
async def create_po(req: dict, request: Request, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Create purchase order"""
    print("CREATE_PO FUNCTION REACHED")
    raw_body = await request.body()
    print("RAW BODY:", raw_body)
    print("PARSED PAYLOAD:", req)
    # ADDED: Map CSV-style fields to expected keys (additive only)
    try:
        if "po_number" not in req and (req.get("number") or req.get("purchase_order_no")):
            req["po_number"] = req.get("number") or req.get("purchase_order_no")
        if "vendor" not in req and (req.get("vendor_name") or req.get("supplier_name")):
            req["vendor"] = req.get("vendor_name") or req.get("supplier_name")
        # Clean amount strings like "₹50,000" -> "50000"
        if "amount" in req and isinstance(req.get("amount"), str):
            amt_str = req.get("amount")
            amt_str = amt_str.replace("₹", "").replace(",", "").strip()
            req["amount"] = amt_str
        # Defensive vendor presence check
        vname_check = (req.get("vendor") or "").strip()
        if not vname_check:
            raise HTTPException(status_code=400, detail=f"Vendor not found: {(req.get('vendor_name') or '').strip()}")
    except HTTPException:
        # Bubble up descriptive errors
        raise
    except Exception as _map_err:
        # Do not modify flow; just log and continue
        import traceback; print("CSV FIELD MAP ERROR:"); traceback.print_exc()
    if not await AccessControlService.can_access_feature(current_user.id, PO_MANAGEMENT, db):
        raise UnauthorizedFeature(PO_FEATURE_NAME)
    gstin_raw = (req.get("gstin") or req.get("vendor_gstin") or "")
    print("Received GSTIN:", gstin_raw)
    gstin_norm = str(gstin_raw).strip().upper()
    print("Normalized GSTIN:", gstin_norm)
    try:
        GSTIN_REGEX = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[0-9A-Z]{1}Z[0-9A-Z]{1}$'
        if not re.match(GSTIN_REGEX, gstin_norm):
            raise HTTPException(status_code=400, detail="Enter a valid vendor GSTIN to proceed.")
    except Exception as e:
        import traceback; print("GSTIN VALIDATION ERROR"); traceback.print_exc(); raise
    due_val = req.get("due_date")
    if isinstance(due_val, str):
        try:
            if len(due_val) == 10:
                # Accept multiple common date formats and normalize to naive UTC date
                parsed = None
                for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y"):
                    try:
                        parsed = datetime.strptime(due_val, fmt)
                        break
                    except Exception:
                        continue
                if parsed is None:
                    # Try ISO as last resort
                    parsed = datetime.fromisoformat(due_val)
                # Keep naive date (midnight)
                due_val = parsed.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                # Normalize to UTC then drop tzinfo to keep naive
                dv = datetime.fromisoformat(due_val.replace("Z", "+00:00"))
                due_val = dv.astimezone(timezone.utc).replace(tzinfo=None)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid due_date format")
    amt_val = req.get("amount")
    try:
        amt_val = float(amt_val)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid amount")
    v_email = (req.get("vendor_email") or "").strip().lower() or None
    if v_email and "@" not in v_email:
        raise HTTPException(status_code=400, detail="Invalid vendor email")
    v_phone_raw = (req.get("vendor_phone") or "").strip() or None
    v_phone = None
    if v_phone_raw:
        v = v_phone_raw
        # Accept Indian 10-digit numbers by normalizing to +91
        if v.isdigit() and len(v) == 10:
            v = "+91" + v
        v_phone_fmt = format_phone_e164(v) or v
        if not is_valid_phone(v_phone_fmt):
            raise HTTPException(status_code=400, detail="Invalid vendor phone")
        v_phone = v_phone_fmt
    # REMOVED (ADDED WRAP): Allow duplicate PO numbers by bypassing previous duplicate checks
    # This block intentionally no-ops to preserve additive-only rule while removing restriction.
    po = PurchaseOrder(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        company_id=current_user.company_id,
        po_number=req["po_number"],
        vendor=req["vendor"],
        gstin=gstin_norm,
        vendor_email=v_email,
        vendor_phone=v_phone,
        amount=amt_val,
        due_date=due_val,
        status=req.get("status", "Open"),
        notes=req.get("notes"),
        document_url=req.get("document_url"),
        supplier_address=req.get("supplier_address"),
        delivery_address=req.get("delivery_address"),
        invoice_address=req.get("invoice_address"),
        payment_window_days=req.get("payment_window_days", 50),
    )
    try:
        db.add(po)
        print("Before commit")
        await db.commit()
        print("After commit")
        await db.refresh(po)
        print("Created PO ID:", po.id)
        check_stmt = select(PurchaseOrder).where(PurchaseOrder.id == po.id)
        check_res = await db.execute(check_stmt)
        check_po = check_res.scalars().first()
        print("Stored PO found:", bool(check_po))
    except Exception as e:
        import traceback; print("PURCHASE ORDER ERROR:"); traceback.print_exc()
        raise HTTPException(status_code=400, detail="Failed to create purchase order")
    # Notification: PO Created
    try:
        from app.models import Notification
        note = Notification(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            type="PO_CREATED",
            message=f"PO {po.po_number} created",
            related_po_id=po.id,
        )
        db.add(note)
        await db.commit()
    except Exception:
        pass
    try:
        svc = EmailService()
        rec_stmt = select(User.email).where(
            (User.company_id == current_user.company_id) &
            (User.is_active == True) &
            (User.role.in_(["MASTER_ADMIN", "COMPANY_ADMIN"]))
        )
        rec_res = await db.execute(rec_stmt)
        recipients = [r[0] for r in rec_res.all()]
        if current_user.email and current_user.email not in recipients:
            recipients.append(current_user.email)
        # Credibility index for this company (if available)
        try:
            from app.models import CompanyCredibilityIndex
            idx_stmt = select(CompanyCredibilityIndex).where(CompanyCredibilityIndex.company_id == current_user.company_id)
            idx_res = await db.execute(idx_stmt)
            idx = idx_res.scalars().first()
        except Exception:
            idx = None
        subj = f"PO {po.po_number} created"
        pending_alert = ""
        if str(po.status or "").lower().find("pending") >= 0:
            pending_alert = "\nPending alert: This PO is currently pending."
        body_lines = [
            f"PO Number: {po.po_number}",
            f"Vendor: {po.vendor}",
            f"GSTIN: {po.gstin}",
            f"Amount: {po.amount}",
            f"Due Date: {po.due_date.date() if po.due_date else ''}",
            f"Status: {po.status}",
        ]
        if idx:
            body_lines.append(f"Credibility Index: {idx.score} (Grade {idx.grade}, Risk {idx.risk_level})")
        body = "\n".join(body_lines) + pending_alert
        for to in recipients:
            svc.send_email(to, subj, body)
    except Exception:
        pass
    # Vendor notifications
    try:
        from app.models import Company
        vendor_company_stmt = select(Company).where(Company.gstin == po.gstin)
        vres = await db.execute(vendor_company_stmt)
        vcompany = vres.scalars().first()
        if vcompany:
            admin_stmt = select(User).where(
                (User.company_id == vcompany.id) &
                (User.is_active == True) &
                (User.role.in_(["MASTER_ADMIN", "COMPANY_ADMIN"]))
            )
            admin_res = await db.execute(admin_stmt)
            admins = admin_res.scalars().all()
            created_at_display = (po.created_at.isoformat() if po.created_at else datetime.utcnow().isoformat())
            for admin in admins:
                from app.models import Notification
                note_vendor = Notification(
                    id=str(uuid.uuid4()),
                    user_id=admin.id,
                    type="PO_CREATED",
                    message=f"PO {po.po_number} from {current_user.company_name} to {po.vendor} amount {po.amount} due {po.due_date.date() if po.due_date else ''}",
                    related_po_id=po.id,
                )
                db.add(note_vendor)
            await db.commit()
            try:
                svc = EmailService()
                subj_v = f"New PO {po.po_number} from {current_user.company_name}"
                # Credibility of buyer company
                try:
                    from app.models import CompanyCredibilityIndex
                    idx_stmt = select(CompanyCredibilityIndex).where(CompanyCredibilityIndex.company_id == current_user.company_id)
                    idx_res = await db.execute(idx_stmt)
                    idx_buyer = idx_res.scalars().first()
                except Exception:
                    idx_buyer = None
                body_v_lines = [
                    f"PO Number: {po.po_number}",
                    f"Vendor: {po.vendor}",
                    f"Company: {current_user.company_name}",
                    f"GSTIN: {po.gstin}",
                    f"Amount: {po.amount}",
                    f"Order Date: {created_at_display}",
                    f"Due Date: {po.due_date.date() if po.due_date else ''}",
                    f"Status: {po.status}",
                ]
                if idx_buyer:
                    body_v_lines.append(f"Buyer Credibility Index: {idx_buyer.score} (Grade {idx_buyer.grade}, Risk {idx_buyer.risk_level})")
                if str(po.status or '').lower().find('pending') >= 0:
                    body_v_lines.append("Pending alert: This PO is currently pending.")
                body_v = "\n".join(body_v_lines)
                for admin in admins:
                    if admin.email:
                        svc.send_email(admin.email, subj_v, body_v)
            except Exception:
                pass
    except Exception:
        pass

    await sync_vendor_credibility(po.vendor, db)

    return ResponseFormatter.create_success(data={"id": po.id}, message="PO created")

@po_router.get("")
async def list_pos(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = 1,
    page_size: int = 20,
    include_archived: bool = False,
    skip: int = 0,
    limit: int = 20,
):
    """List user's purchase orders"""
    try:
        print("LIST_PO REACHED")
        # Support both page/page_size and skip/limit
        if page_size and page_size > 0:
            limit = min(int(page_size), 1000)
        if page and page > 1:
            skip = (int(page) - 1) * limit
        stmt = select(PurchaseOrder).where(PurchaseOrder.company_id == current_user.company_id)
        print(f"LIST_PO QUERY FOR COMPANY: {current_user.company_id}")
        if not include_archived:
            stmt = stmt.where(PurchaseOrder.archived == False)
        stmt = stmt.order_by(PurchaseOrder.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        pos = result.scalars().all()
        print("LIST_PO COUNT:", len(pos))
        rows = [{
            "id": p.id,
            "po_number": p.po_number,
            "vendor": p.vendor,
            "gstin": p.gstin,
            "vendor_email": p.vendor_email,
            "vendor_phone": p.vendor_phone,
            "amount": p.amount,
            "due_date": p.due_date.isoformat() if p.due_date else None,
            "status": p.status,
            "archived": p.archived,
            "payment_completed_at": p.payment_completed_at.isoformat() if p.payment_completed_at else None,
            "payment_window_days": getattr(p, "payment_window_days", 50),
            "legal_notice_sent_at": p.legal_notice_sent_at.isoformat() if p.legal_notice_sent_at else None,
            "document_url": p.document_url,
            "notes": p.notes,
            "supplier_address": p.supplier_address,
            "delivery_address": p.delivery_address,
            "invoice_address": p.invoice_address,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        } for p in pos]
        return ResponseFormatter.create_success(data=rows)
    except Exception as e:
        import traceback; print("PURCHASE ORDER LIST ERROR (fallback without archived filter):"); traceback.print_exc()
        try:
            # Fallback: run without archived filter to avoid column mismatch errors
            if page_size and page_size > 0:
                limit = min(int(page_size), 1000)
            if page and page > 1:
                skip = (int(page) - 1) * limit
            stmt2 = select(PurchaseOrder).where(PurchaseOrder.company_id == current_user.company_id).order_by(PurchaseOrder.created_at.desc()).offset(skip).limit(limit)
            result2 = await db.execute(stmt2)
            pos2 = result2.scalars().all()
            rows2 = [{
                "id": p.id,
                "po_number": p.po_number,
                "vendor": p.vendor,
                "gstin": p.gstin,
                "vendor_email": p.vendor_email,
                "vendor_phone": p.vendor_phone,
                "amount": p.amount,
                "due_date": p.due_date.isoformat() if p.due_date else None,
                "status": p.status,
                "archived": getattr(p, "archived", False),
                "payment_completed_at": p.payment_completed_at.isoformat() if p.payment_completed_at else None,
                "payment_window_days": getattr(p, "payment_window_days", 50),
                "legal_notice_sent_at": p.legal_notice_sent_at.isoformat() if p.legal_notice_sent_at else None,
                "document_url": p.document_url,
                "notes": p.notes,
                "supplier_address": p.supplier_address,
                "delivery_address": p.delivery_address,
                "invoice_address": p.invoice_address,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            } for p in pos2]
            return ResponseFormatter.create_success(data=rows2)
        except Exception:
            # Final fallback: empty list
            return ResponseFormatter.create_success(data=[])

# Purchase history routes
purchase_history_router = APIRouter()

@purchase_history_router.get("/purchase-history")
async def purchase_history(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """List user's completed or archived purchase orders"""
    stmt = (
        select(PurchaseOrder)
        .where(
            (PurchaseOrder.user_id == current_user.id) &
            (or_(PurchaseOrder.status == "Completed", PurchaseOrder.archived == True))
        )
        .order_by(PurchaseOrder.created_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return ResponseFormatter.create_success(data=[{
        "id": p.id,
        "po_number": p.po_number,
        "vendor": p.vendor,
        "gstin": p.gstin,
        "amount": p.amount,
        "due_date": p.due_date.isoformat() if p.due_date else None,
        "status": p.status,
        "archived": p.archived,
        "document_url": p.document_url,
        "notes": p.notes,
        "supplier_address": p.supplier_address,
        "delivery_address": p.delivery_address,
        "invoice_address": p.invoice_address,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    } for p in rows])

@po_router.get("/{po_id}")
async def get_po(po_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get single purchase order"""
    stmt = select(PurchaseOrder).where((PurchaseOrder.id == po_id) & (PurchaseOrder.user_id == current_user.id))
    result = await db.execute(stmt)
    po = result.scalars().first()
    if not po:
        raise HTTPException(status_code=404, detail=PO_NOT_FOUND_ERROR)
    return ResponseFormatter.create_success(data={
        "id": po.id,
        "po_number": po.po_number,
        "vendor": po.vendor,
        "gstin": po.gstin,
        "vendor_email": po.vendor_email,
        "vendor_phone": po.vendor_phone,
        "amount": po.amount,
        "due_date": po.due_date.isoformat() if po.due_date else None,
        "status": po.status,
        "archived": po.archived,
        "document_url": po.document_url,
        "notes": po.notes,
        "supplier_address": po.supplier_address,
        "delivery_address": po.delivery_address,
        "invoice_address": po.invoice_address,
        "created_at": po.created_at.isoformat() if po.created_at else None,
        "updated_at": po.updated_at.isoformat() if po.updated_at else None
    })

@po_router.put("/{po_id}")
async def update_po(po_id: str, req: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Update purchase order"""
    if not await AccessControlService.can_access_feature(current_user.id, PO_MANAGEMENT, db):
        raise UnauthorizedFeature(PO_FEATURE_NAME)
    
    stmt = select(PurchaseOrder).where((PurchaseOrder.id == po_id) & (PurchaseOrder.user_id == current_user.id))
    result = await db.execute(stmt)
    po = result.scalars().first()
    if not po:
        raise HTTPException(status_code=404, detail=PO_NOT_FOUND_ERROR)
    
    # Update fields
    if po.payment_completed_at is not None:
        # Financially locked: prevent changes to critical fields
        locked_fields = {"status", "amount", "due_date"}
        attempted = locked_fields.intersection(set(req.keys()))
        if attempted:
            raise HTTPException(status_code=400, detail="Cannot modify paid purchase order")
    if "po_number" in req:
        po.po_number = req["po_number"]
    if "vendor" in req:
        po.vendor = req["vendor"]
    if "gstin" in req:
        po.gstin = req["gstin"].upper()
    if "vendor_email" in req:
        email_val = (req.get("vendor_email") or "").strip().lower()
        if email_val and "@" not in email_val:
            raise HTTPException(status_code=400, detail="Invalid vendor email")
        po.vendor_email = email_val or None
    if "vendor_phone" in req:
        phone_raw = (req.get("vendor_phone") or "").strip()
        if phone_raw:
            phone_fmt = format_phone_e164(phone_raw) or phone_raw
            if not is_valid_phone(phone_fmt):
                raise HTTPException(status_code=400, detail="Invalid vendor phone")
            po.vendor_phone = phone_fmt
        else:
            po.vendor_phone = None
    if "amount" in req:
        try:
            po.amount = float(req["amount"])
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid amount")
    if "status" in req:
        prev_status = po.status
        po.status = req["status"]
        if po.payment_completed_at is not None:
            raise HTTPException(status_code=400, detail="Cannot change status of paid purchase order")
    if "notes" in req:
        po.notes = req.get("notes")
    if "document_url" in req:
        po.document_url = req["document_url"]
    if "supplier_address" in req:
        po.supplier_address = req["supplier_address"]
    if "delivery_address" in req:
        po.delivery_address = req["delivery_address"]
    if "invoice_address" in req:
        po.invoice_address = req["invoice_address"]
    if "payment_window_days" in req:
        po.payment_window_days = req["payment_window_days"]
    
    po.updated_at = datetime.utcnow()
    await db.commit()
    # Send update notifications to both companies, include pending alert and credibility
    try:
        svc = EmailService()
        # Company admins (buyer)
        rec_stmt = select(User.email).where(
            (User.company_id == current_user.company_id) &
            (User.is_active == True) &
            (User.role.in_(["MASTER_ADMIN", "COMPANY_ADMIN"]))
        )
        rec_res = await db.execute(rec_stmt)
        recipients = [r[0] for r in rec_res.all()]
        if current_user.email and current_user.email not in recipients:
            recipients.append(current_user.email)
        from app.models import CompanyCredibilityIndex, Company
        idx_stmt = select(CompanyCredibilityIndex).where(CompanyCredibilityIndex.company_id == current_user.company_id)
        idx_res = await db.execute(idx_stmt)
        idx = idx_res.scalars().first()
        subj = f"PO {po.po_number} updated"
        pending_alert = ""
        if str(po.status or "").lower().find("pending") >= 0:
            pending_alert = "\nPending alert: This PO is currently pending."
        body_lines = [
            f"PO Number: {po.po_number}",
            f"Vendor: {po.vendor}",
            f"GSTIN: {po.gstin}",
            f"Amount: {po.amount}",
            f"Due Date: {po.due_date.date() if po.due_date else ''}",
            f"Status: {po.status}",
        ]
        if idx:
            body_lines.append(f"Credibility Index: {idx.score} (Grade {idx.grade}, Risk {idx.risk_level})")
        body = "\n".join(body_lines) + pending_alert
        for to in recipients:
            svc.send_email(to, subj, body)
        # Vendor admins
        vendor_company_stmt = select(Company).where(Company.gstin == po.gstin)
        vres = await db.execute(vendor_company_stmt)
        vcompany = vres.scalars().first()
        if vcompany:
            admin_stmt = select(User).where(
                (User.company_id == vcompany.id) &
                (User.is_active == True) &
                (User.role.in_(["MASTER_ADMIN", "COMPANY_ADMIN"]))
            )
            admin_res = await db.execute(admin_stmt)
            admins = admin_res.scalars().all()
            subj_v = f"PO {po.po_number} updated by {current_user.company_name}"
            body_v_lines = [
                f"PO Number: {po.po_number}",
                f"Vendor: {po.vendor}",
                f"Company: {current_user.company_name}",
                f"GSTIN: {po.gstin}",
                f"Amount: {po.amount}",
                f"Due Date: {po.due_date.date() if po.due_date else ''}",
                f"Status: {po.status}",
            ]
            if idx:
                body_v_lines.append(f"Buyer Credibility Index: {idx.score} (Grade {idx.grade}, Risk {idx.risk_level})")
            if str(po.status or '').lower().find('pending') >= 0:
                body_v_lines.append("Pending alert: This PO is currently pending.")
            body_v = "\n".join(body_v_lines)
            for admin in admins:
                if admin.email:
                    svc.send_email(admin.email, subj_v, body_v)
    except Exception:
        pass

    await sync_vendor_credibility(po.vendor, db)

    return ResponseFormatter.create_success(data={"id": po.id}, message="PO updated successfully")

@po_router.post("/{po_id}/mark-paid")
async def mark_paid(po_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Mark purchase order as paid (immutable financial action)"""
    role = str(current_user.role or "").upper()
    allowed_roles = {"MASTER_ADMIN", "COMPANY_ADMIN", "FINANCE"}
    if role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Not authorized")
    stmt = select(PurchaseOrder).where((PurchaseOrder.id == po_id) & (PurchaseOrder.user_id == current_user.id))
    result = await db.execute(stmt)
    po = result.scalars().first()
    if not po:
        raise HTTPException(status_code=404, detail=PO_NOT_FOUND_ERROR)
    if po.payment_completed_at is not None:
        raise HTTPException(status_code=400, detail="Already marked paid")
    po.status = "Closed"
    po.payment_completed_at = datetime.utcnow()
    po.updated_at = datetime.utcnow()
    from app.models import PurchaseOrderAuditLog
    from uuid import uuid4
    audit = PurchaseOrderAuditLog(
        id=str(uuid4()),
        purchase_order_id=po.id,
        action="MARK_PAID",
        performed_by_user_id=current_user.id,
        timestamp=datetime.utcnow(),
        details={"user_email": current_user.email},
    )
    db.add(audit)
    await db.commit()
    # Notification: Mark Paid
    try:
        from app.models import Notification
        note = Notification(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            type="PO_MARK_PAID",
            message=f"PO {po.po_number} marked as paid",
            related_po_id=po.id,
        )
        db.add(note)
        await db.commit()
    except Exception:
        pass
    try:
        svc = EmailService()
        rec_stmt = select(User.email).where(
            (User.company_id == current_user.company_id) &
            (User.is_active == True) &
            (User.role.in_(["MASTER_ADMIN", "COMPANY_ADMIN"]))
        )
        rec_res = await db.execute(rec_stmt)
        recipients = [r[0] for r in rec_res.all()]
        if current_user.email and current_user.email not in recipients:
            recipients.append(current_user.email)
        subj = f"PO {po.po_number} marked paid"
        body = f"PO {po.po_number} marked paid on {po.payment_completed_at.date() if po.payment_completed_at else ''}"
        for to in recipients:
            svc.send_email(to, subj, body)
    except Exception:
        pass

    await sync_vendor_credibility(po.vendor, db)

    return ResponseFormatter.create_success(message="Marked as paid")

@po_router.delete("/{po_id}")
async def delete_po(po_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Delete purchase order"""
    if not await AccessControlService.can_access_feature(current_user.id, PO_MANAGEMENT, db):
        raise UnauthorizedFeature(PO_FEATURE_NAME)
    
    stmt = select(PurchaseOrder).where((PurchaseOrder.id == po_id) & (PurchaseOrder.user_id == current_user.id))
    result = await db.execute(stmt)
    po = result.scalars().first()
    if not po:
        raise HTTPException(status_code=404, detail=PO_NOT_FOUND_ERROR)
    
    await db.delete(po)
    await db.commit()
    return ResponseFormatter.create_success(message="PO deleted successfully")

@po_router.post("/{po_id}/archive")
async def archive_po(po_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Archive/unarchive purchase order"""
    stmt = select(PurchaseOrder).where((PurchaseOrder.id == po_id) & (PurchaseOrder.user_id == current_user.id))
    result = await db.execute(stmt)
    po = result.scalars().first()
    if not po:
        raise HTTPException(status_code=404, detail=PO_NOT_FOUND_ERROR)
    
    po.archived = not po.archived
    po.updated_at = datetime.utcnow()
    await db.commit()
    return ResponseFormatter.create_success(data={"is_archived": po.archived}, message="PO archive status updated")

@po_router.post("/{po_id}/send-reminder")
async def send_vendor_reminder(po_id: str, req: dict = None, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Manually send or schedule reminder email to vendor for a specific PO"""
    # Fetch PO for current user
    stmt = select(PurchaseOrder, User).join(User, PurchaseOrder.user_id == User.id).where(
        (PurchaseOrder.id == po_id) & (PurchaseOrder.user_id == current_user.id)
    )
    res = await db.execute(stmt)
    row = res.first()
    if not row:
        raise HTTPException(status_code=404, detail=PO_NOT_FOUND_ERROR)
    po, owner = row
    
    # Require vendor email
    v_email = (po.vendor_email or "").strip()
    if not v_email:
        raise HTTPException(status_code=400, detail="No vendor email configured for this PO")

    # Use custom content if provided, otherwise fallback to template
    subject = (req or {}).get("subject")
    body = (req or {}).get("body")
    scheduled_at = (req or {}).get("scheduled_at")
    include_legal_notice = (req or {}).get("include_legal_notice", False)
    legal_notice_content = (req or {}).get("legal_notice_content", "")

    if not subject or not body:
        # Compose email from template if not provided in request
        try:
            from app.models import POReminderConfig
            cfg_res = await db.execute(select(POReminderConfig))
            cfg = cfg_res.scalars().first()
        except Exception:
            cfg = None

        due_date_str = po.due_date.date().isoformat() if po.due_date else "N/A"
        amount_str = f"₹{po.amount:,.2f}"
        
        def format_val(template, default_val):
            if not template:
                return default_val
            return template.replace("{vendor_name}", po.vendor or "") \
                           .replace("{amount}", amount_str) \
                           .replace("{due_date}", due_date_str) \
                           .replace("{po_number}", po.po_number or "")

        if not subject:
            subject = format_val(cfg.reminder_subject if cfg else None, f"Payment Reminder: PO {po.po_number} due on {due_date_str}")
        if not body:
            body = format_val(cfg.reminder_body if cfg else None, (
                f"Dear {po.vendor or 'Vendor'},\n\n"
                f"This is a reminder that Purchase Order {po.po_number} for amount {amount_str} "
                f"is due on {due_date_str}. Please arrange payment at the earliest.\n\n"
                f"Regards,\n{owner.company_name or 'Your Customer'}"
            ))

    # Append legal notice if requested
    if include_legal_notice and legal_notice_content:
        # The legal notice is sent as a PDF, so we don't append it to the body here.
        pass

    if scheduled_at:
        try:
            # Parse datetime-local format (YYYY-MM-DDTHH:MM) or ISO
            s = str(scheduled_at).replace("Z", "+00:00")
            if "T" in s and "+" not in s and s.count(":") == 1:
                # Add seconds if missing from datetime-local
                s += ":00"
            
            sched_dt = datetime.fromisoformat(s)
            if sched_dt.tzinfo:
                sched_dt = sched_dt.astimezone(timezone.utc).replace(tzinfo=None)
            
            from app.models import ScheduledReminder
            import uuid
            sr = ScheduledReminder(
                id=str(uuid.uuid4()),
                purchase_order_id=po.id,
                user_id=current_user.id,
                subject=subject,
                body=body,
                scheduled_at=sched_dt
            )
            db.add(sr)
            await db.commit()
            return ResponseFormatter.create_success(message=f"Reminder scheduled for {sched_dt.isoformat()}")
        except Exception as e:
            import traceback; traceback.print_exc()
            raise HTTPException(status_code=400, detail=f"Invalid scheduled_at format: {e}")

    # Send email NOW
    try:
        if include_legal_notice:
            # Generate PDF
            pdf_path = f"uploads/temp/legal_notice_{po_id}.pdf"
            po_data = {
                "vendor": po.vendor,
                "po_number": po.po_number,
                "amount": po.amount,
                "due_date": str(po.due_date),
                "company_name": owner.company_name or "Company"
            }
            generate_legal_notice_pdf(po_data, pdf_path, legal_notice_content)
            
            # Send with attachment
            await send_email_with_attachment(
                to_email=v_email,
                subject=subject,
                body=body,
                attachment_path=pdf_path,
                attachment_name=f"Legal_Notice_{po.po_number}.pdf"
            )
            
            # Cleanup
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                
            po.legal_notice_sent_at = datetime.utcnow()
            await db.commit()
        else:
            EmailService().send_email(v_email, subject, body)
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to send reminder email: {str(e)}")

    # Optional: emit notification record
    try:
        note = Notification(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            type="PO_VENDOR_REMINDER",
            message=f"Manual reminder sent to vendor for PO {po.po_number}",
            related_po_id=po.id,
        )
        db.add(note)
        await db.commit()
    except Exception:
        pass
    return ResponseFormatter.create_success(message="Reminder sent successfully")

@po_router.post("/{po_id}/send-to-legal")
async def send_to_legal_support(po_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Send legal support request for a PO"""
    # Fetch PO details
    stmt = select(PurchaseOrder).where((PurchaseOrder.id == po_id) & (PurchaseOrder.user_id == current_user.id))
    result = await db.execute(stmt)
    po = result.scalars().first()
    
    if not po:
        raise HTTPException(status_code=404, detail=PO_NOT_FOUND_ERROR)
    
    # Calculate days overdue
    from datetime import date
    today = date.today()
    due = po.due_date.date() if hasattr(po.due_date, 'date') else po.due_date
    days_diff = (today - due).days
    overdue_text = f"{days_diff} days overdue" if days_diff > 0 else f"{abs(days_diff)} days remaining"
    
    subject = f"⚖️ Legal Support Required - PO {po.po_number} - {po.vendor}"
    
    body = f"""
LEGAL SUPPORT REQUEST
=====================

Dear Legal Support Team,

Admin has requested legal assistance for the following Purchase Order:

PO DETAILS:
-----------
PO Number     : {po.po_number}
Vendor Name   : {po.vendor}
Vendor Email  : {po.vendor_email}
Vendor Phone  : {po.vendor_phone}
Vendor GSTIN  : {po.gstin}
Amount Due    : Rs.{po.amount}
Due Date      : {po.due_date}
Payment Status: {po.status}
Days Status   : {overdue_text}
Payment Window: {po.payment_window_days} days

ADDITIONAL INFO:
----------------
Legal Notice Sent : {"Yes - " + str(po.legal_notice_sent_at) if po.legal_notice_sent_at else "No"}
PO Created On     : {po.created_at}
Requested By      : {current_user.name} ({current_user.email})

Please take appropriate legal action at the earliest.

This is an automated request from CreditDataWatch platform.
    """
    
    # Send to legal support team
    try:
        from app.services.email_service import EmailService
        svc = EmailService()
        svc.send_email(
            to_email="payalshinde906@gmail.com",
            subject=subject,
            body=body
        )
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to notify legal support team: {str(e)}")
    
    # Update DB - mark legal support requested
    po.legal_support_requested_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "Legal support team has been notified successfully"}

@po_router.post("/{po_id}/send-legal-notice")
async def send_legal_notice(po_id: str, request: Request, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    body = await request.json()
    include_legal = body.get("include_legal_notice", False)
    custom_text = body.get("legal_notice_content", None)

    # Fetch PO from DB
    stmt = select(PurchaseOrder).where((PurchaseOrder.id == po_id) & (PurchaseOrder.user_id == current_user.id))
    result = await db.execute(stmt)
    po = result.scalars().first()
    if not po:
        raise HTTPException(status_code=404, detail=PO_NOT_FOUND_ERROR)

    # Clean email body - NO legal notice text here
    email_body = f"""Dear {po.vendor},

This is a reminder that PO {po.po_number} for the amount of Rs.{po.amount} is due on {po.due_date}.

Please ensure payment is processed on time.

Regards,
Team CreditWatch"""

    if include_legal:
        print(f"[DEBUG] include_legal_notice: {include_legal}")
        print(f"[DEBUG] vendor_email: {po.vendor_email}")
        # Generate PDF
        pdf_path = f"uploads/temp/legal_notice_{po_id}.pdf"
        print(f"[DEBUG] Generating PDF at: {pdf_path}")
        po_data = {
            "vendor": po.vendor,
            "po_number": po.po_number,
            "amount": po.amount,
            "due_date": str(po.due_date),
            "company_name": current_user.company_name or "Company"
        }
        generate_legal_notice_pdf(po_data, pdf_path, custom_text)
        print(f"[DEBUG] PDF generated. File exists: {os.path.exists(pdf_path)}")

        # Send with PDF attachment
        await send_email_with_attachment(
            to_email=po.vendor_email,
            subject=f"Payment Reminder - PO {po.po_number}",
            body=email_body,
            attachment_path=pdf_path,
            attachment_name=f"Legal_Notice_{po.po_number}.pdf"
        )
        print(f"[DEBUG] Email sent with attachment")

        # Delete temp PDF
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        # Update DB
        po.legal_notice_sent_at = datetime.utcnow()
        await db.commit()

        return {"message": f"Email with legal notice PDF sent to {po.vendor_email}"}
    else:
        # Send normal reminder without attachment
        await EmailService().send_email(po.vendor_email, f"Payment Reminder - PO {po.po_number}", email_body)
        return {"message": f"Reminder sent to {po.vendor_email}"}
# Defaulter routes
defaulter_router = APIRouter()

@defaulter_router.post("")
async def file_defaulter(req: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """File defaulter case - GSTIN or PAN required"""
    if not await AccessControlService.can_access_feature(current_user.id, REPORT_OVERDUE, db):
        raise UnauthorizedFeature(DEFAULTER_FEATURE_NAME)
    
    gstin = req.get("business_gstin", "").strip().upper()
    pan = req.get("pan", "").strip().upper()
    
    if not gstin and not pan:
        raise HTTPException(status_code=400, detail="Either GSTIN or PAN must be provided")
    
    if pan and (len(pan) != 10 or not pan[:5].isalpha() or not pan[5:9].isdigit() or not pan[9].isalpha()):
        raise HTTPException(status_code=400, detail="Invalid PAN format")
    
    case = DefaulterCase(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        business_name=req["business_name"],
        business_gstin=gstin if gstin else None,
        pan=pan if pan else None,
        invoice_number=req["invoice_number"],
        amount=req["amount"],
        due_date=req["due_date"],
        approval_status="pending",
        notes=req.get("notes", ""),
        documents_drive_folder=req.get("documents_drive_folder", ""),
    )
    db.add(case)
    await db.commit()
    return ResponseFormatter.create_success(data={"id": case.id}, message="Defaulter case filed")

@defaulter_router.get("")
async def list_defaulters(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """List user's defaulter cases"""
    stmt = select(DefaulterCase).where(
        DefaulterCase.user_id == current_user.id
    ).order_by(DefaulterCase.created_at.desc())
    result = await db.execute(stmt)
    cases = result.scalars().all()
    
    data = [{
        "id": c.id,
        "business_name": c.business_name,
        "business_gstin": c.business_gstin,
        "pan": c.pan,
        "invoice_number": c.invoice_number,
        "amount": c.amount,
        "due_date": c.due_date.isoformat() if c.due_date else None,
        "approval_status": c.approval_status,
        "notes": c.notes,
        "documents_drive_folder": c.documents_drive_folder,
        "ledger_url": c.ledger_url,
        "ca_certificate_url": c.ca_certificate_url,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "verified_by": c.verified_by,
        "verification_date": c.verification_date.isoformat() if c.verification_date else None,
    } for c in cases]
    
    return ResponseFormatter.create_success(data=data)

# Notifications routes
notifications_router = APIRouter()

@notifications_router.get("/notifications")
async def list_notifications(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 50):
    stmt = select(Notification).where(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).offset(skip).limit(limit)
    res = await db.execute(stmt)
    notes = res.scalars().all()
    return ResponseFormatter.create_success(data=[{
        "id": n.id,
        "type": n.type,
        "message": n.message,
        "related_po_id": n.related_po_id,
        "is_read": n.is_read,
        "created_at": n.created_at.isoformat() if n.created_at else None,
    } for n in notes])

@notifications_router.post("/notifications/{note_id}/read")
async def mark_notification_read(note_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(Notification).where(Notification.id == note_id, Notification.user_id == current_user.id)
    res = await db.execute(stmt)
    note = res.scalars().first()
    if not note:
        raise HTTPException(status_code=404, detail="Notification not found")
    note.is_read = True
    await db.commit()
    return ResponseFormatter.create_success(message="Notification marked as read")

@defaulter_router.get("/{case_id}")
async def get_defaulter(case_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get single defaulter case details"""
    stmt = select(DefaulterCase).where(DefaulterCase.id == case_id)
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(status_code=404, detail="Defaulter case not found")
    
    if case.user_id != current_user.id:
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_ERROR)
    
    return ResponseFormatter.create_success(data={
        "id": case.id,
        "business_name": case.business_name,
        "business_gstin": case.business_gstin,
        "pan": case.pan,
        "invoice_number": case.invoice_number,
        "amount": case.amount,
        "due_date": case.due_date.isoformat() if case.due_date else None,
        "approval_status": case.approval_status,
        "notes": case.notes,
        "documents_drive_folder": case.documents_drive_folder,
        "ledger_url": case.ledger_url,
        "ca_certificate_url": case.ca_certificate_url,
        "created_at": case.created_at.isoformat() if case.created_at else None,
        "updated_at": case.updated_at.isoformat() if case.updated_at else None,
        "verified_by": case.verified_by,
        "verification_date": case.verification_date.isoformat() if case.verification_date else None,
    })

def _validate_pan(pan: str) -> bool:
    """Validate PAN format: 5 letters, 4 digits, 1 letter"""
    return len(pan) == 10 and pan[:5].isalpha() and pan[5:9].isdigit() and pan[9].isalpha()

def _validate_gstin_pan(gstin: str, pan: str) -> bool:
    """Validate that at least one of GSTIN or PAN is provided and PAN is valid if provided"""
    if not gstin and not pan:
        return False
    if pan and not _validate_pan(pan):
        return False
    return True

def _apply_defaulter_updates(case: DefaulterCase, req: dict) -> None:
    """Apply field updates to defaulter case from request"""
    fields_to_update = [
        "business_name", "business_gstin", "pan", "invoice_number",
        "amount", "due_date", "notes", "documents_drive_folder",
        "ledger_url", "ca_certificate_url",
    ]
    
    for field in fields_to_update:
        if field in req:
            value = req[field]
            if field in ("business_gstin", "pan"):
                value = value.upper().strip() if value else None
            setattr(case, field, value)

@defaulter_router.put("/{case_id}")
async def update_defaulter(case_id: str, req: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Update defaulter case (only if pending)"""
    if not await AccessControlService.can_access_feature(current_user.id, REPORT_OVERDUE, db):
        raise UnauthorizedFeature(DEFAULTER_FEATURE_NAME)
    
    stmt = select(DefaulterCase).where(DefaulterCase.id == case_id)
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(status_code=404, detail=f"Defaulter case {NOT_FOUND_ERROR}")
    
    if case.user_id != current_user.id:
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_ERROR)
    
    if case.approval_status != "pending":
        raise HTTPException(status_code=400, detail=CANNOT_UPDATE_REVIEWED)
    
    # Validate GSTIN or PAN
    gstin = req.get("business_gstin", "").strip().upper() if "business_gstin" in req else case.business_gstin
    pan = req.get("pan", "").strip().upper() if "pan" in req else case.pan
    
    if not _validate_gstin_pan(gstin, pan):
        if not gstin and not pan:
            raise HTTPException(status_code=400, detail=EITHER_GSTIN_PAN)
        raise HTTPException(status_code=400, detail=INVALID_PAN_FORMAT)
    
    _apply_defaulter_updates(case, req)
    case.updated_at = datetime.utcnow()
    await db.commit()
    
    return ResponseFormatter.create_success(message="Defaulter case updated")

@defaulter_router.delete("/{case_id}")
async def delete_defaulter(case_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Delete defaulter case (only if pending)"""
    if not await AccessControlService.can_access_feature(current_user.id, REPORT_OVERDUE, db):
        raise UnauthorizedFeature(DEFAULTER_FEATURE_NAME)
    
    stmt = select(DefaulterCase).where(DefaulterCase.id == case_id)
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(status_code=404, detail=f"Defaulter case {NOT_FOUND_ERROR}")
    
    if case.user_id != current_user.id:
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_ERROR)
    
    # Only allow deletion of pending cases
    if case.approval_status != "pending":
        raise HTTPException(status_code=400, detail="Cannot delete case that has been reviewed")
    
    await db.delete(case)
    await db.commit()
    
    return ResponseFormatter.create_success(message="Defaulter case deleted")

@defaulter_router.post("/{case_id}/upload-document")
async def upload_defaulter_document(
    case_id: str,
    req: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload document links (Drive folder / ledger / CA certificate)"""
    stmt = select(DefaulterCase).where(DefaulterCase.id == case_id)
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(status_code=404, detail="Defaulter case not found")
    
    if case.user_id != current_user.id:
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_ERROR)
    
    if "drive_folder_id" in req:
        case.documents_drive_folder = req.get("drive_folder_id", "")
    if "ledger_url" in req:
        case.ledger_url = req.get("ledger_url", "")
    if "ca_certificate_url" in req:
        case.ca_certificate_url = req.get("ca_certificate_url", "")
    
    case.updated_at = datetime.utcnow()
    await db.commit()
    
    return ResponseFormatter.create_success(message="Document links updated")
# Credit Report routes
credit_router = APIRouter()

@credit_router.post("")
async def request_credit_report(req: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Request credit report"""
    if not await AccessControlService.can_access_feature(current_user.id, "CREDIT_REPORTS", db):
        raise UnauthorizedFeature("Credit Reports")
    report = CreditReport(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        entity_name=req["entity_name"],
        entity_gstin=req["entity_gstin"].upper(),
        status="Requested",
    )
    db.add(report)
    await db.commit()
    return ResponseFormatter.create_success(data={"id": report.id}, message="Report requested")

@credit_router.get("")
async def list_credit_reports(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """List credit reports"""
    stmt = select(CreditReport).where(CreditReport.user_id == current_user.id).order_by(CreditReport.created_at.desc())
    result = await db.execute(stmt)
    reports = result.scalars().all()
    return ResponseFormatter.create_success(data=[{
        "id": r.id,
        "entity_name": r.entity_name,
        "entity_gstin": r.entity_gstin,
        "credit_score": r.credit_score,
        "status": r.status,
        "report_url": r.report_url,
        "last_updated": r.last_updated.isoformat() if r.last_updated else None,
        "requested_at": r.requested_at.isoformat() if r.requested_at else None,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    } for r in reports])

@credit_router.get("/{report_id}")
async def get_credit_report(report_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get credit report details"""
    stmt = select(CreditReport).where(CreditReport.id == report_id)
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Credit report not found")
    
    if report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_ERROR)
    
    return ResponseFormatter.create_success(data={
        "id": report.id,
        "entity_name": report.entity_name,
        "entity_gstin": report.entity_gstin,
        "credit_score": report.credit_score,
        "status": report.status,
        "report_url": report.report_url,
        "last_updated": report.last_updated.isoformat() if report.last_updated else None,
        "requested_at": report.requested_at.isoformat() if report.requested_at else None,
        "created_at": report.created_at.isoformat() if report.created_at else None,
        "updated_at": report.updated_at.isoformat() if report.updated_at else None,
    })

@credit_router.put("/{report_id}")
async def update_credit_report(report_id: str, req: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Update credit report (admin upload results)"""
    stmt = select(CreditReport).where(CreditReport.id == report_id)
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Credit report not found")
    
    if report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_ERROR)
    
    if "credit_score" in req:
        report.credit_score = req["credit_score"]
    if "status" in req:
        report.status = req["status"]
    if "report_url" in req:
        report.report_url = req["report_url"]
    if "last_updated" in req:
        report.last_updated = datetime.fromisoformat(req["last_updated"])
    
    report.updated_at = datetime.utcnow()
    await db.commit()
    
    return ResponseFormatter.create_success(message="Credit report updated")

# Settlement routes
settlement_router = APIRouter()

@settlement_router.post("")
async def create_settlement(req: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Create settlement record"""
    if not await AccessControlService.can_access_feature(current_user.id, "SETTLEMENT", db):
        raise UnauthorizedFeature("Settlement")
    settlement = Settlement(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        case_reference=req["case_reference"],
        status="Open",
        notes=req.get("notes"),
    )
    db.add(settlement)
    await db.commit()
    return ResponseFormatter.create_success(data={"id": settlement.id}, message="Settlement created")

@settlement_router.get("")
async def list_settlements(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """List settlements"""
    stmt = select(Settlement).where(Settlement.user_id == current_user.id).order_by(Settlement.created_at.desc())
    result = await db.execute(stmt)
    settlements = result.scalars().all()
    return ResponseFormatter.create_success(data=[{
        "id": s.id,
        "case_reference": s.case_reference,
        "status": s.status,
        "notes": s.notes,
        "documents_drive_folder": s.documents_drive_folder,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "updated_at": s.updated_at.isoformat() if s.updated_at else None,
    } for s in settlements])

@settlement_router.get("/{settlement_id}")
async def get_settlement(settlement_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get settlement details"""
    stmt = select(Settlement).where(Settlement.id == settlement_id)
    result = await db.execute(stmt)
    settlement = result.scalar_one_or_none()
    
    if not settlement:
        raise HTTPException(status_code=404, detail="Settlement not found")
    
    if settlement.user_id != current_user.id:
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_ERROR)
    
    return ResponseFormatter.create_success(data={
        "id": settlement.id,
        "case_reference": settlement.case_reference,
        "status": settlement.status,
        "notes": settlement.notes,
        "documents_drive_folder": settlement.documents_drive_folder,
        "created_at": settlement.created_at.isoformat() if settlement.created_at else None,
        "updated_at": settlement.updated_at.isoformat() if settlement.updated_at else None,
    })

@settlement_router.put("/{settlement_id}")
async def update_settlement(settlement_id: str, req: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Update settlement"""
    stmt = select(Settlement).where(Settlement.id == settlement_id)
    result = await db.execute(stmt)
    settlement = result.scalar_one_or_none()
    
    if not settlement:
        raise HTTPException(status_code=404, detail="Settlement not found")
    
    if settlement.user_id != current_user.id:
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_ERROR)
    
    if "case_reference" in req:
        settlement.case_reference = req["case_reference"]
    if "status" in req:
        settlement.status = req["status"]
    if "notes" in req:
        settlement.notes = req["notes"]
    if "documents_drive_folder" in req:
        settlement.documents_drive_folder = req["documents_drive_folder"]
    
    settlement.updated_at = datetime.utcnow()
    await db.commit()
    
    return ResponseFormatter.create_success(message="Settlement updated")
