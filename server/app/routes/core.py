"""
User and feature routes (stub with core endpoints)
"""
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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
    stmt = select(Subscription).where(Subscription.user_id == current_user.id)
    result = await db.execute(stmt)
    sub = result.scalars().first()
    if not sub:
        # User has no subscription yet - this is OK for new users
        return ResponseFormatter.create_success(data=None)
    return ResponseFormatter.create_success(data=SubscriptionResponse.model_validate(sub).__dict__)

# Purchase Order routes
po_router = APIRouter()

@po_router.post("")
async def create_po(req: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Create purchase order"""
    if not await AccessControlService.can_access_feature(current_user.id, PO_MANAGEMENT, db):
        raise UnauthorizedFeature(PO_FEATURE_NAME)
    due_val = req.get("due_date")
    if isinstance(due_val, str):
        try:
            if len(due_val) == 10:
                # Date only; keep naive UTC date (midnight) to match TIMESTAMP WITHOUT TIME ZONE
                due_val = datetime.fromisoformat(due_val)
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
    po = PurchaseOrder(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        number=req["number"],
        vendor_name=req["vendor_name"],
        vendor_gstin=req["vendor_gstin"].upper(),
        amount=amt_val,
        due_date=due_val,
        status=req.get("status", "Open"),
        notes=req.get("notes"),
        document_url=req.get("document_url"),
        supplier_address=req.get("supplier_address"),
        delivery_address=req.get("delivery_address"),
        invoice_address=req.get("invoice_address"),
    )
    db.add(po)
    await db.commit()
    return ResponseFormatter.create_success(data={"id": po.id}, message="PO created")

@po_router.get("")
async def list_pos(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 20, include_archived: bool = False):
    """List user's purchase orders"""
    stmt = select(PurchaseOrder).where(PurchaseOrder.user_id == current_user.id)
    if not include_archived:
        stmt = stmt.where(PurchaseOrder.is_archived == False)
    stmt = stmt.offset(skip).limit(limit).order_by(PurchaseOrder.created_at.desc())
    result = await db.execute(stmt)
    pos = result.scalars().all()
    return ResponseFormatter.create_success(data=[{
        "id": p.id,
        "number": p.number,
        "vendor_name": p.vendor_name,
        "vendor_gstin": p.vendor_gstin,
        "amount": p.amount,
        "due_date": p.due_date.isoformat() if p.due_date else None,
        "status": p.status,
        "is_archived": p.is_archived,
        "document_url": p.document_url,
        "notes": p.notes,
        "supplier_address": p.supplier_address,
        "delivery_address": p.delivery_address,
        "invoice_address": p.invoice_address,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    } for p in pos])

# Purchase history routes
purchase_history_router = APIRouter()

@purchase_history_router.get("/purchase-history")
async def purchase_history(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """List user's completed or archived purchase orders"""
    stmt = (
        select(PurchaseOrder)
        .where(
            (PurchaseOrder.user_id == current_user.id) &
            (or_(PurchaseOrder.status == "Completed", PurchaseOrder.is_archived == True))
        )
        .order_by(PurchaseOrder.created_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return ResponseFormatter.create_success(data=[{
        "id": p.id,
        "number": p.number,
        "vendor_name": p.vendor_name,
        "vendor_gstin": p.vendor_gstin,
        "amount": p.amount,
        "due_date": p.due_date.isoformat() if p.due_date else None,
        "status": p.status,
        "is_archived": p.is_archived,
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
        "number": po.number,
        "vendor_name": po.vendor_name,
        "vendor_gstin": po.vendor_gstin,
        "amount": po.amount,
        "due_date": po.due_date.isoformat() if po.due_date else None,
        "status": po.status,
        "is_archived": po.is_archived,
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
    if "number" in req:
        po.number = req["number"]
    if "vendor_name" in req:
        po.vendor_name = req["vendor_name"]
    if "vendor_gstin" in req:
        po.vendor_gstin = req["vendor_gstin"].upper()
    if "amount" in req:
        try:
            po.amount = float(req["amount"])
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid amount")
    if "due_date" in req:
        val = req["due_date"]
        if isinstance(val, str):
            try:
                if len(val) == 10:
                    val = datetime.fromisoformat(val)
                else:
                    dv = datetime.fromisoformat(val.replace("Z", "+00:00"))
                    val = dv.astimezone(timezone.utc).replace(tzinfo=None)
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid due_date format")
        po.due_date = val
    if "status" in req:
        po.status = req["status"]
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
    
    po.updated_at = datetime.utcnow()
    await db.commit()
    return ResponseFormatter.create_success(data={"id": po.id}, message="PO updated successfully")

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
    
    po.is_archived = not po.is_archived
    po.updated_at = datetime.utcnow()
    await db.commit()
    return ResponseFormatter.create_success(data={"is_archived": po.is_archived}, message="PO archive status updated")

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
