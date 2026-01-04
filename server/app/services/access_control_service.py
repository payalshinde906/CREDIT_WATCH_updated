"""
Access control service
"""
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User, Subscription, Plan


class AccessControlService:
    """Check user access to features based on subscription"""

    # Feature-to-plan mapping (by plan name)
    FEATURE_REQUIREMENTS = {
        "REPORT_OVERDUE": ["base", "royal", "groups", "enterprise"],
        "PO_MANAGEMENT": ["base", "royal", "groups", "enterprise"],
        "CREDIT_REPORTS": ["royal", "groups", "enterprise"],
        "AUTO_FOLLOWUPS": ["royal", "groups", "enterprise"],
        "SETTLEMENT": ["royal", "groups", "enterprise"],
        "PARTNER_SHARING": ["groups", "enterprise"],
    }

    @staticmethod
    async def can_access_feature(user_id: str, feature: str, db: AsyncSession) -> bool:
        """
        Check if user can access a feature
        
        Args:
            user_id: User ID
            feature: Feature name
            db: Database session
            
        Returns:
            True if user has access, False if no subscription or expired
        """
        # Get user's active subscription
        stmt = select(Subscription).where(
            (Subscription.user_id == user_id) &
            (Subscription.is_active == True)
        ).order_by(Subscription.start_date.desc())
        
        result = await db.execute(stmt)
        subscription = result.scalars().first()
        
        if not subscription:
            return False
        
        # Check if subscription is expired
        if subscription.expiry_date and subscription.expiry_date < datetime.now(timezone.utc):
            return False
        
        # Get the plan and check feature access
        if not subscription.plan:
            return False
        
        allowed_plans = AccessControlService.FEATURE_REQUIREMENTS.get(feature, [])
        return subscription.plan.name in allowed_plans

    @staticmethod
    async def get_user_plan(user_id: str, db: AsyncSession) -> str | None:
        """
        Get user's current plan
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            Plan name or None
        """
        stmt = select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.is_active == True
        )
        result = await db.execute(stmt)
        subscription = result.scalars().first()
        
        return subscription.plan if subscription else None

    @staticmethod
    def get_feature_requirements(feature: str) -> list:
        """
        Get required plans for a feature
        
        Args:
            feature: Feature name
            
        Returns:
            List of plan names that have access
        """
        return AccessControlService.FEATURE_REQUIREMENTS.get(feature, [])
