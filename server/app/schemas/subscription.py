"""Subscription schemas"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PlanResponse(BaseModel):
    """Plan response schema"""
    id: str
    name: str
    display_name: str
    description: Optional[str] = None
    duration_type: str  # "monthly" or "yearly"
    price: float
    validity_days: int
    follow_up_limit: int
    legal_assistance_limit: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SubscriptionRequest(BaseModel):
    """Subscription purchase request"""
    plan_id: str = Field(..., description="Plan ID to purchase")


class SubscriptionResponse(BaseModel):
    """Subscription response schema"""
    id: str
    user_id: str
    plan_id: str
    status: str  # "active", "expired", "cancelled"
    is_active: bool
    start_date: datetime
    expiry_date: Optional[datetime] = None
    payment_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    plan: Optional[PlanResponse] = None

    class Config:
        from_attributes = True


class SubscriptionStatusResponse(BaseModel):
    """Current subscription status"""
    has_active_subscription: bool
    subscription: Optional[SubscriptionResponse] = None
    days_remaining: Optional[int] = None
    is_expired: bool = False
