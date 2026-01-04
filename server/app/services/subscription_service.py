"""
Subscription service for plan purchases and management
"""
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Subscription, Plan, User
from app.exceptions import PlanNotFound, UserNotFound, InvalidPlanId
from app.utils.response import ResponseFormatter
import logging

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Handle subscription purchases, renewals, and expiry logic"""

    @staticmethod
    async def get_active_subscription(user_id: str, db: AsyncSession) -> Subscription | None:
        """
        Get user's active subscription
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            Active subscription or None if no active subscription
        """
        stmt = (
            select(Subscription)
            .where(
                (Subscription.user_id == user_id) &
                (Subscription.is_active == True)
            )
            .order_by(Subscription.start_date.desc())
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def is_subscription_valid(subscription: Subscription) -> bool:
        """
        Check if subscription is still valid (not expired)
        
        Args:
            subscription: Subscription object
            
        Returns:
            True if valid, False if expired
        """
        if not subscription:
            return False
        
        if not subscription.is_active:
            return False
        
        if subscription.expiry_date and subscription.expiry_date < datetime.now(timezone.utc):
            return False
        
        return True

    @staticmethod
    async def purchase_subscription(
        user_id: str, 
        plan_id: str, 
        db: AsyncSession
    ) -> Subscription:
        """
        Purchase a subscription plan
        
        Args:
            user_id: User ID
            plan_id: Plan ID to purchase
            db: Database session
            
        Returns:
            New subscription object
            
        Raises:
            UserNotFound: If user doesn't exist
            PlanNotFound: If plan doesn't exist or is inactive
        """
        # Verify user exists
        user_stmt = select(User).where(User.id == user_id)
        user_result = await db.execute(user_stmt)
        user = user_result.scalars().first()
        
        if not user:
            raise UserNotFound()
        
        # Verify plan exists and is active
        plan_stmt = select(Plan).where(
            (Plan.id == plan_id) & 
            (Plan.is_active == True)
        )
        plan_result = await db.execute(plan_stmt)
        plan = plan_result.scalars().first()
        
        if not plan:
            raise PlanNotFound()
        
        # Deactivate any existing active subscriptions
        active_stmt = (
            select(Subscription)
            .where(
                (Subscription.user_id == user_id) &
                (Subscription.is_active == True)
            )
        )
        active_result = await db.execute(active_stmt)
        active_subs = active_result.scalars().all()
        
        for sub in active_subs:
            sub.is_active = False
            sub.updated_at = datetime.now(timezone.utc)
        
        # Create new subscription
        now = datetime.now(timezone.utc)
        expiry_date = now + timedelta(days=plan.validity_days)
        
        new_subscription = Subscription(
            id=str(uuid4()),
            user_id=user_id,
            plan_id=plan_id,
            is_active=True,
            start_date=now,
            expiry_date=expiry_date,
            created_at=now,
            updated_at=now,
        )
        
        db.add(new_subscription)
        await db.flush()  # Flush to ensure subscription is created before commit
        
        logger.info(
            f"New subscription created: user_id={user_id}, plan_id={plan_id}, expiry={expiry_date}"
        )
        
        return new_subscription

    @staticmethod
    async def renew_subscription(
        subscription_id: str,
        db: AsyncSession
    ) -> Subscription:
        """
        Renew an existing subscription for another period
        
        Args:
            subscription_id: Subscription ID to renew
            db: Database session
            
        Returns:
            Renewed subscription object
        """
        # Get current subscription with plan
        stmt = (
            select(Subscription)
            .where(Subscription.id == subscription_id)
        )
        result = await db.execute(stmt)
        subscription = result.scalars().first()
        
        if not subscription:
            raise UserNotFound()
        
        # Calculate new expiry date
        now = datetime.now(timezone.utc)
        new_expiry = now + timedelta(days=subscription.plan.validity_days)
        
        subscription.expiry_date = new_expiry
        subscription.is_active = True
        subscription.updated_at = now
        
        logger.info(
            f"Subscription renewed: subscription_id={subscription_id}, new_expiry={new_expiry}"
        )
        
        return subscription

    @staticmethod
    async def get_subscription_details(subscription_id: str, db: AsyncSession) -> Subscription:
        """
        Get subscription details with plan info
        
        Args:
            subscription_id: Subscription ID
            db: Database session
            
        Returns:
            Subscription with related plan
        """
        stmt = select(Subscription).where(Subscription.id == subscription_id)
        result = await db.execute(stmt)
        subscription = result.scalars().first()
        
        if not subscription:
            raise UserNotFound()
        
        return subscription
