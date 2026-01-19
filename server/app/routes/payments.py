"""
Payment management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from app.database import get_db
from app.schemas.payment import (
    PaymentInitiateRequest, PaymentInitiateResponse,
    PaymentVerifyRequest, PaymentResponse, PaymentStatusResponse,
    PaymentHistoryResponse
)
from app.services.payment_service import PaymentService
from app.exceptions import PlanNotFound, UserNotFound
from app.utils.response import ResponseFormatter
from app.dependencies import get_current_user
from app.models import Payment, Plan
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Payments"])


@router.post("/initiate", response_model=dict)
async def initiate_payment(
    request: PaymentInitiateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Initiate payment for a plan
    
    Args:
        request: Payment initiation request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Payment details with payment options
    """
    try:
        payment, payment_options = await PaymentService.initiate_payment(
            user_id=current_user["id"],
            plan_id=request.plan_id,
            payment_method=request.payment_method.value,
            db=db,
        )
        
        # Get plan details
        plan_stmt = select(Plan).where(Plan.id == request.plan_id)
        plan_result = await db.execute(plan_stmt)
        plan = plan_result.scalars().first()
        
        await db.commit()
        
        return ResponseFormatter.create_success(
            message="Payment initiated successfully",
            data={
                "payment_id": payment.id,
                "reference_id": payment.reference_id,
                "amount": payment.amount,
                "currency": payment.currency,
                "plan": {
                    "id": plan.id,
                    "name": plan.name,
                    "display_name": plan.display_name,
                    "duration_type": plan.duration_type.value if hasattr(plan.duration_type, 'value') else str(plan.duration_type),
                },
                "payment_options": payment_options,
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
        logger.error(f"Error initiating payment: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate payment",
        )


@router.post("/{payment_id}/verify", response_model=dict)
async def verify_payment(
    payment_id: str,
    request: PaymentVerifyRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Verify payment completion
    
    Args:
        payment_id: Payment ID
        request: Payment verification request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Payment verification result with subscription details
    """
    try:
        # Verify payment belongs to user
        payment = await PaymentService.get_payment_status(payment_id, db)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found",
            )
        
        if payment.user_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized to verify this payment",
            )
        
        payment, subscription = await PaymentService.verify_payment(
            payment_id=payment_id,
            transaction_id=request.transaction_id,
            gateway_order_id=request.gateway_order_id,
            gateway_payment_id=request.gateway_payment_id,
            db=db,
        )
        
        await db.commit()
        
        subscription_data = None
        if subscription:
            subscription_data = {
                "id": subscription.id,
                "plan_id": subscription.plan_id,
                "status": subscription.status.value if hasattr(subscription.status, 'value') else str(subscription.status),
                "start_date": subscription.start_date.isoformat(),
                "expiry_date": subscription.expiry_date.isoformat() if subscription.expiry_date else None,
            }
        
        return ResponseFormatter.create_success(
            message="Payment verified successfully",
            data={
                "payment_id": payment.id,
                "transaction_id": payment.transaction_id,
                "status": payment.status.value if hasattr(payment.status, 'value') else str(payment.status),
                "subscription": subscription_data,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify payment",
        )


@router.get("/{payment_id}/status", response_model=dict)
async def get_payment_status(
    payment_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get payment status
    
    Args:
        payment_id: Payment ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Payment status details
    """
    try:
        payment = await PaymentService.get_payment_status(payment_id, db)
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found",
            )
        
        # Verify ownership
        if payment.user_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized to view this payment",
            )
        
        return ResponseFormatter.create_success(
            message="Payment status retrieved",
            data={
                "payment_id": payment.id,
                "status": payment.status.value if hasattr(payment.status, 'value') else str(payment.status),
                "transaction_id": payment.transaction_id,
                "amount": payment.amount,
                "payment_method": payment.payment_method.value if hasattr(payment.payment_method, 'value') else str(payment.payment_method),
                "created_at": payment.created_at.isoformat(),
                "completed_at": payment.completed_at.isoformat() if payment.completed_at else None,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get payment status",
        )


@router.get("/history", response_model=dict)
async def get_payment_history(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    """
    Get user's payment history
    
    Args:
        current_user: Current authenticated user
        db: Database session
        limit: Maximum number of payments to return
        offset: Offset for pagination
        
    Returns:
        List of payment history entries
    """
    try:
        payments = await PaymentService.get_user_payment_history(
            user_id=current_user["id"],
            limit=limit,
            offset=offset,
            db=db,
        )
        
        # Get plan names for each payment
        payment_data = []
        for payment in payments:
            plan_stmt = select(Plan).where(Plan.id == payment.plan_id)
            plan_result = await db.execute(plan_stmt)
            plan = plan_result.scalars().first()
            
            payment_data.append({
                "id": payment.id,
                "plan_name": plan.display_name if plan else "Unknown Plan",
                "amount": payment.amount,
                "status": payment.status.value if hasattr(payment.status, 'value') else str(payment.status),
                "payment_method": payment.payment_method.value if hasattr(payment.payment_method, 'value') else str(payment.payment_method),
                "transaction_id": payment.transaction_id,
                "failure_reason": payment.failure_reason,
                "created_at": payment.created_at.isoformat(),
            })
        
        return ResponseFormatter.create_success(
            message="Payment history retrieved",
            data={
                "payments": payment_data,
                "total": len(payment_data),
            },
        )
    except Exception as e:
        logger.error(f"Error getting payment history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get payment history",
        )


@router.post("/{payment_id}/cancel", response_model=dict)
async def cancel_payment(
    payment_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancel a pending payment
    
    Args:
        payment_id: Payment ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Cancelled payment details
    """
    try:
        payment = await PaymentService.cancel_payment(
            payment_id=payment_id,
            user_id=current_user["id"],
            db=db,
        )
        
        await db.commit()
        
        return ResponseFormatter.create_success(
            message="Payment cancelled successfully",
            data={
                "payment_id": payment.id,
                "status": payment.status.value if hasattr(payment.status, 'value') else str(payment.status),
            },
        )
    except UserNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found or unauthorized",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error cancelling payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel payment",
        )
