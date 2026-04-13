"""
Admin routes - for plan management and system configuration
"""
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, Plan, Subscription, Invitation, Company
from app.schemas import UpdateProfileRequest, UserProfileResponse
from app.services import AccessControlService
from app.utils import ResponseFormatter
from app.dependencies import get_current_user, require_admin
from app.exceptions import UnauthorizedFeature
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)

JSON_MEDIA_TYPE = "application/json"
router = APIRouter()


# ============ PLAN MANAGEMENT ============



@router.post("/plans")
async def create_plan(
    req: dict,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new membership plan (admin only)"""
    plan = Plan(
        id=str(uuid.uuid4()),
        name=req.get("name", "").lower(),
        display_name=req.get("display_name", ""),
        description=req.get("description", ""),
        price=float(req.get("price", 0)),
        validity_days=int(req.get("validity_days", 30)),
        follow_up_limit=int(req.get("follow_up_limit", 10)),
        legal_assistance_limit=int(req.get("legal_assistance_limit", 2)),
        is_active=True,
    )
    db.add(plan)
    await db.commit()
    logger.info(f"Plan created: {plan.id} ({plan.name}) by admin {admin.id}")
    return ResponseFormatter.create_success(data={"id": plan.id}, message="Plan created successfully")


@router.put("/plans/{plan_id}")
async def update_plan(
    plan_id: str,
    req: dict,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update a membership plan (admin only)"""
    stmt = select(Plan).where(Plan.id == plan_id)
    result = await db.execute(stmt)
    plan = result.scalars().first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    if "display_name" in req:
        plan.display_name = req["display_name"]
    if "description" in req:
        plan.description = req["description"]
    if "price" in req:
        plan.price = float(req["price"])
    if "validity_days" in req:
        plan.validity_days = int(req["validity_days"])
    if "follow_up_limit" in req:
        plan.follow_up_limit = int(req["follow_up_limit"])
    if "legal_assistance_limit" in req:
        plan.legal_assistance_limit = int(req["legal_assistance_limit"])
    
    await db.commit()
    logger.info(f"Plan updated: {plan_id} by admin {admin.id}")
    return ResponseFormatter.create_success(message="Plan updated successfully")


@router.delete("/plans/{plan_id}")
async def deactivate_plan(
    plan_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Deactivate a membership plan (admin only) - soft delete"""
    stmt = select(Plan).where(Plan.id == plan_id)
    result = await db.execute(stmt)
    plan = result.scalars().first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    plan.is_active = False
    await db.commit()
    logger.info(f"Plan deactivated: {plan_id} by admin {admin.id}")
    return ResponseFormatter.create_success(message="Plan deactivated successfully")


@router.get("/plans")
async def list_all_plans(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """List all plans including inactive ones (admin only)"""
    stmt = select(Plan).order_by(Plan.price)
    result = await db.execute(stmt)
    plans = result.scalars().all()
    return ResponseFormatter.create_success(data=[{
        "id": p.id,
        "name": p.name,
        "display_name": p.display_name,
        "description": p.description,
        "price": p.price,
        "validity_days": p.validity_days,
        "is_active": p.is_active,
        "created_at": p.created_at.isoformat() if p.created_at else None
    } for p in plans])


# ============ USER MANAGEMENT ============

@router.get("/users")
async def list_users(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """List all users (admin only)"""
    stmt = select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
    result = await db.execute(stmt)
    users = result.scalars().all()
    
    return ResponseFormatter.create_success(data=[{
        "id": u.id,
        "company_id": u.company_id,
        "company_name": u.company_name,
        "email": u.email,
        "phone": u.phone,
        "role": u.role,
        "is_active": u.is_active,
        "created_at": u.created_at.isoformat(),
    } for u in users])


@router.post("/invitations")
async def create_invitation(
    payload: dict,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create employee invitation (admin only)"""
    email = payload.get("email", "").lower()
    role = "USER"
    expiry_hours = int(payload.get("expiry_hours", 24))
    if expiry_hours < 1 or expiry_hours > 168:
        raise HTTPException(status_code=400, detail="expiry_hours must be between 1 and 168")
    token = str(uuid.uuid4())
    from datetime import timedelta
    now = datetime.utcnow().replace(microsecond=0)
    expires_at = now + timedelta(hours=expiry_hours)

    # Verify admin has company
    stmt = select(Company).where(Company.id == admin.company_id)
    res = await db.execute(stmt)
    company = res.scalars().first()
    if not company:
        raise HTTPException(status_code=400, detail="Admin company not found")

    inv = Invitation(
        id=str(uuid.uuid4()),
        company_id=company.id,
        email=email,
        role=role,
        token=token,
        expires_at=expires_at,
        status="PENDING",
    )
    db.add(inv)
    await db.commit()

    # Safe domain check — only enforce if company has domain set 
    company_domain = getattr(company, 'company_domain', None) or getattr(company, 'domain_name', None) 
    allow_any = getattr(company, 'allow_any_domain', True) 
    
    if not allow_any and company_domain: 
        invited_domain = email.split('@')[1] if '@' in email else '' 
        if invited_domain != company_domain: 
            raise HTTPException( 
                status_code=400, 
                detail=f"Invited email must be from your company domain @{company_domain}. To allow any domain, update your company settings." 
            ) 

    try:
        from app.services.email_service import EmailService
        await EmailService.send_invitation_email(
            to_email=email,
            company_name=company.company_name,
            role=role,
            token=token,
            expires_at=expires_at.isoformat(),
        )
    except Exception as e:
        logger.warning(f"Invitation email failed for {email}: {e}")
    return ResponseFormatter.create_success(message="Invitation created", data={"token": token, "expires_at": expires_at.isoformat(), "expiry_hours": expiry_hours})

@router.get("/invitations")
async def list_invitations(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """List invitations for admin's company"""
    stmt = select(Invitation).where(Invitation.company_id == admin.company_id).offset(skip).limit(limit).order_by(Invitation.created_at.desc())
    result = await db.execute(stmt)
    invitations = result.scalars().all()
    return ResponseFormatter.create_success(data=[{
        "id": i.id,
        "email": i.email,
        "role": i.role,
        "token": i.token,
        "expires_at": i.expires_at.isoformat() if i.expires_at else None,
        "status": i.status,
        "created_at": i.created_at.isoformat() if i.created_at else None
    } for i in invitations])


@router.put("/invitations/{invitation_id}")
async def update_invitation(
    invitation_id: str,
    payload: dict,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update invitation role and/or expiry (hours) - email is immutable"""
    from datetime import timedelta
    stmt = select(Invitation).where(Invitation.id == invitation_id, Invitation.company_id == admin.company_id)
    result = await db.execute(stmt)
    inv = result.scalars().first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invitation not found")
    # Role must remain USER for invitations
    inv.role = "USER"
    if "expiry_hours" in payload and payload["expiry_hours"] is not None:
        try:
            hours = int(payload["expiry_hours"])
        except Exception:
            raise HTTPException(status_code=400, detail="expiry_hours must be an integer")
        if hours < 1 or hours > 168:
            raise HTTPException(status_code=400, detail="expiry_hours must be between 1 and 168")
        now = datetime.utcnow().replace(microsecond=0)
        inv.expires_at = now + timedelta(hours=hours)
    await db.commit()
    return ResponseFormatter.create_success(
        message="Invitation updated",
        data={
            "id": inv.id,
            "email": inv.email,
            "role": inv.role,
            "expires_at": inv.expires_at.isoformat() if inv.expires_at else None,
            "status": inv.status,
        },
    )


@router.delete("/invitations/{invitation_id}")
async def delete_invitation(
    invitation_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete an invitation"""
    stmt = select(Invitation).where(Invitation.id == invitation_id, Invitation.company_id == admin.company_id)
    result = await db.execute(stmt)
    inv = result.scalars().first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invitation not found")
    await db.delete(inv)
    await db.commit()
    return ResponseFormatter.create_success(message="Invitation deleted")

@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    req: dict,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update user role (admin only)"""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Protect MASTER_ADMIN from role changes
    if str(user.role or "").upper() == "MASTER_ADMIN":
        raise HTTPException(status_code=400, detail="Cannot modify MASTER_ADMIN role")
    
    new_role = str(req.get("role", "")).upper()
    if new_role not in ["USER", "COMPANY_ADMIN"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    user.role = new_role
    await db.commit()
    logger.info(f"User {user_id} role updated to {new_role} by admin {admin.id}")
    return ResponseFormatter.create_success(message="User role updated successfully")

@router.delete("/users/{user_id}")
async def remove_user(
    user_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Remove employee from company (admin only)"""
    stmt = select(User).where(User.id == user_id, User.company_id == admin.company_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if str(user.role or "").upper() == "MASTER_ADMIN":
        raise HTTPException(status_code=400, detail="Cannot remove MASTER_ADMIN account")
    await db.delete(user)
    await db.commit()
    logger.info(f"User {user_id} removed from company {admin.company_id} by admin {admin.id}")
    return ResponseFormatter.create_success(message="User removed successfully")

# ============ DEFAULTER VERIFICATION ============

@router.get("/defaulters/pending")
async def list_pending_defaulters(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """List pending defaulter cases for verification (admin only)"""
    from app.models import DefaulterCase
    
    stmt = select(DefaulterCase).where(
        DefaulterCase.approval_status == "pending"
    ).offset(skip).limit(limit).order_by(DefaulterCase.created_at.desc())
    
    result = await db.execute(stmt)
    cases = result.scalars().all()
    
    return ResponseFormatter.create_success(data=[{
        "id": c.id,
        "business_name": c.business_name,
        "business_gstin": c.business_gstin,
        "amount": c.amount,
        "status": c.approval_status,
        "created_at": c.created_at.isoformat(),
    } for c in cases])


@router.put("/defaulters/{case_id}/verify")
async def verify_defaulter_case(
    case_id: str,
    req: dict,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Approve or reject a defaulter case (admin only)"""
    from app.models import DefaulterCase
    
    stmt = select(DefaulterCase).where(DefaulterCase.id == case_id)
    result = await db.execute(stmt)
    case = result.scalars().first()
    
    if not case:
        raise HTTPException(status_code=404, detail="Defaulter case not found")
    
    action = req.get("action", "").lower()  # approve, reject
    notes = req.get("notes", "")
    
    if action not in ["approve", "reject"]:
        raise HTTPException(status_code=400, detail="Invalid action (must be 'approve' or 'reject')")
    
    case.approval_status = "approved" if action == "approve" else "rejected"
    case.verified_by = admin.id
    case.verification_date = datetime.utcnow()
    case.notes = notes
    
    if action == "approve":
        # Reward the user with 50 points
        from app.services.wallet_service import WalletService
        wallet_service = WalletService(db)
        await wallet_service.add_transaction(
            user_id=case.user_id,
            amount=50.0,
            trans_type="CREDIT",
            reference_type="BONUS",
            reference_id=case.id,
            description=f"Reward for verified defaulter: {case.business_name}"
        )

    await db.commit()
    logger.info(f"Defaulter case {case_id} {action}ed by admin {admin.id}")
    return ResponseFormatter.create_success(message=f"Case {action}ed successfully")


# ============ ANALYTICS ============

@router.get("/analytics/subscriptions")
async def subscription_analytics(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get subscription analytics (admin only)"""
    stmt = select(Subscription).where(Subscription.is_active == True)
    result = await db.execute(stmt)
    subs = result.scalars().all()
    
    # Group by plan
    by_plan = {}
    for sub in subs:
        plan_name = sub.plan.name if sub.plan else "unknown"
        by_plan[plan_name] = by_plan.get(plan_name, 0) + 1
    
    return ResponseFormatter.create_success(data={
        "total_active": len(subs),
        "by_plan": by_plan,
    })


@router.get("/analytics/defaulters")
async def defaulter_analytics(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get defaulter case analytics (admin only)"""
    from app.models import DefaulterCase
    
    stmt = select(DefaulterCase)
    result = await db.execute(stmt)
    cases = result.scalars().all()
    
    # Group by status
    by_status = {
        "pending": len([c for c in cases if c.approval_status == "pending"]),
        "approved": len([c for c in cases if c.approval_status == "approved"]),
        "rejected": len([c for c in cases if c.approval_status == "rejected"]),
    }
    
    # Total amount
    total_amount = sum(c.amount for c in cases)
    
    return ResponseFormatter.create_success(data={
        "total_cases": len(cases),
        "by_status": by_status,
        "total_amount": total_amount,
    })


# ============ PO REMINDER CONFIG ============

@router.get("/po-reminders")
async def get_po_reminder_config(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get PO reminder configuration (admin only)"""
    from app.models import POReminderConfig
    stmt = select(POReminderConfig)
    result = await db.execute(stmt)
    config = result.scalars().first()
    if not config:
        config = POReminderConfig(
            id=str(uuid.uuid4()),
            before_days=[7, 3, 1],
            after_due_daily_enabled=True
        )
        db.add(config)
        await db.commit()
        await db.refresh(config)
    return ResponseFormatter.create_success(data={
        "id": config.id,
        "before_days": config.before_days,
        "after_due_daily_enabled": config.after_due_daily_enabled,
        "reminder_subject": config.reminder_subject or "Payment Reminder: PO {po_number} - {vendor_name}",
        "reminder_body": config.reminder_body or "Dear {vendor_name},\n\nThis is a reminder that PO {po_number} for the amount of ₹{amount} is due on {due_date}.\n\nPlease ensure payment is processed on time.\n\nRegards,\nTeam CreditWatch"
    })


@router.put("/po-reminders")
async def update_po_reminder_config(
    req: dict,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update PO reminder configuration (admin only)"""
    from app.models import POReminderConfig
    stmt = select(POReminderConfig)
    result = await db.execute(stmt)
    config = result.scalars().first()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    if "before_days" in req:
        config.before_days = req["before_days"]
    if "after_due_daily_enabled" in req:
        config.after_due_daily_enabled = req["after_due_daily_enabled"]
    if "reminder_subject" in req:
        config.reminder_subject = req["reminder_subject"]
    if "reminder_body" in req:
        config.reminder_body = req["reminder_body"]
    await db.commit()
    return ResponseFormatter.create_success(message="PO reminder config updated")


from fastapi import UploadFile, File 
from app.services.pdf_service import PDFService 
from app.models import SOPDocument 
from sqlalchemy import delete 
 
@router.post("/sop-upload") 
async def upload_sop( 
    file: UploadFile = File(...), 
    db: AsyncSession = Depends(get_db), 
    current_user = Depends(require_admin) 
): 
    if not file.filename.endswith('.pdf'): 
        raise HTTPException( 
            status_code=400, 
            detail="Only PDF files allowed" 
        ) 
    content = await file.read() 
    text = PDFService.extract_text(content) 
     
    await db.execute(delete(SOPDocument)) 
     
    sop = SOPDocument( 
        filename=file.filename, 
        content=text, 
        uploaded_by=current_user.id 
    ) 
    db.add(sop) 
    await db.commit() 
    return { 
        "success": True, 
        "message": f"SOP uploaded: {file.filename}" 
    } 
 
@router.get("/sop-status") 
async def get_sop_status( 
    db: AsyncSession = Depends(get_db), 
    current_user = Depends(require_admin) 
): 
    from sqlalchemy import select 
    result = await db.execute( 
        select(SOPDocument).order_by( 
            SOPDocument.uploaded_at.desc() 
        ).limit(1) 
    ) 
    sop = result.scalar_one_or_none() 
    if sop: 
        return { 
            "exists": True, 
            "filename": sop.filename, 
            "uploaded_at": str(sop.uploaded_at) 
        } 
    return {"exists": False} 
