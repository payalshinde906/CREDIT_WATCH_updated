"""
Admin routes - for plan management and system configuration
"""
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, Plan, Subscription
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
        "gstin": u.gstin,
        "company_name": u.company_name,
        "email": u.email,
        "phone": u.phone,
        "role": u.role,
        "is_active": u.is_active,
        "created_at": u.created_at.isoformat(),
    } for u in users])


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
    
    new_role = req.get("role", "").lower()
    if new_role not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    user.role = new_role
    await db.commit()
    logger.info(f"User {user_id} role updated to {new_role} by admin {admin.id}")
    return ResponseFormatter.create_success(message="User role updated successfully")


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
    case.verification_date = datetime.now(timezone.utc)
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
