"""
Subscription management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from app.database import get_db
from app.schemas import SubscriptionRequest, SubscriptionResponse, SubscriptionStatusResponse
from app.services.subscription_service import SubscriptionService
from app.exceptions import PlanNotFound, UserNotFound
from app.utils.response import ResponseFormatter
from app.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get("/plans", response_model=dict)
async def list_plans(db: AsyncSession = Depends(get_db)):
    """List all membership plans (public)"""
    try:
        from app.models import Plan
        from sqlalchemy import select
        
        stmt = select(Plan).where(Plan.is_active == True).order_by(Plan.price)
        result = await db.execute(stmt)
        plans = result.scalars().all()
        
        return ResponseFormatter.create_success(
            data=[{
                "id": p.id,
                "name": p.name,
                "display_name": p.display_name,
                "description": p.description,
                "duration_type": p.duration_type.value if hasattr(p.duration_type, 'value') else str(p.duration_type),
                "price": p.price,
                "validity_days": p.validity_days,
                "features": {
                    "follow_up_limit": p.follow_up_limit,
                    "legal_assistance_limit": p.legal_assistance_limit,
                }
            } for p in plans]
        )
    except Exception as e:
        logger.error(f"Error in list_plans: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=dict)
async def purchase_subscription(
    request: SubscriptionRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Purchase a subscription plan
    
    Args:
        request: Subscription purchase request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message with subscription details
    """
    try:
        subscription = await SubscriptionService.purchase_subscription(
            user_id=current_user["id"],
            plan_id=request.plan_id,
            db=db,
        )
        
        await db.commit()
        
        return ResponseFormatter.create_success(
            message="Subscription purchased successfully",
            data={
                "subscription_id": subscription.id,
                "plan_id": subscription.plan_id,
                "start_date": subscription.start_date.isoformat(),
                "expiry_date": subscription.expiry_date.isoformat() if subscription.expiry_date else None,
            },
        )
    except PlanNotFound:
        logger.warning(f"User {current_user['id']} tried to purchase non-existent plan")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found or inactive",
        )
    except UserNotFound:
        logger.error(f"Authenticated user {current_user['id']} not found in database")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    except Exception as e:
        logger.error(f"Error purchasing subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to purchase subscription",
        )


@router.get("/status", response_model=dict)
async def get_subscription_status(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current subscription status for authenticated user
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Subscription status with remaining days
    """
    try:
        subscription = await SubscriptionService.get_active_subscription(
            user_id=current_user["id"],
            db=db,
        )
        
        has_active = False
        days_remaining = None
        is_expired = False
        
        if subscription:
            is_valid = await SubscriptionService.is_subscription_valid(subscription)
            has_active = is_valid
            
            if subscription.expiry_date:
                now = datetime.now(timezone.utc)
                if subscription.expiry_date < now:
                    is_expired = True
                    days_remaining = 0
                else:
                    delta = subscription.expiry_date - now
                    days_remaining = delta.days
        
        # Build subscription data or None
        subscription_data = None
        if subscription:
            expiry_isoformat = subscription.expiry_date.isoformat() if subscription.expiry_date else None
            subscription_data = {
                "id": subscription.id,
                "plan_id": subscription.plan_id,
                "status": subscription.status.value if hasattr(subscription.status, 'value') else str(subscription.status),
                "start_date": subscription.start_date.isoformat(),
                "expiry_date": expiry_isoformat,
            }
        
        return ResponseFormatter.create_success(
            message="Subscription status retrieved",
            data={
                "has_active_subscription": has_active,
                "is_expired": is_expired,
                "days_remaining": days_remaining,
                "subscription": subscription_data,
            },
        )
    except Exception as e:
        logger.error(f"Error getting subscription status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get subscription status",
        )


@router.get("/{subscription_id}", response_model=dict)
async def get_subscription_details(
    subscription_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get details of a specific subscription
    
    Args:
        subscription_id: Subscription ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Subscription details with plan information
    """
    try:
        subscription = await SubscriptionService.get_subscription_details(
            subscription_id=subscription_id,
            db=db,
        )
        
        # Verify ownership
        if subscription.user_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized to view this subscription",
            )
        
        return ResponseFormatter.create_success(
            message="Subscription details retrieved",
            data={
                "id": subscription.id,
                "plan_id": subscription.plan_id,
                "is_active": subscription.is_active,
                "start_date": subscription.start_date.isoformat(),
                "expiry_date": subscription.expiry_date.isoformat() if subscription.expiry_date else None,
                "plan": {
                    "name": subscription.plan.name,
                    "display_name": subscription.plan.display_name,
                    "price": subscription.plan.price,
                    "validity_days": subscription.plan.validity_days,
                    "follow_up_limit": subscription.plan.follow_up_limit,
                    "legal_assistance_limit": subscription.plan.legal_assistance_limit,
                } if subscription.plan else None,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subscription details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get subscription details",
        )
