"""
Pydantic schemas for user
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class UserProfileResponse(BaseModel):
    """User profile response"""

    id: str
    role: str
    gstin: str
    company_name: str
    email: str
    phone: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    """Update user profile"""

    company_name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=20)


class SubscriptionResponse(BaseModel):
    """Subscription/plan response"""

    id: str
    plan: str
    is_active: bool
    start_date: datetime
    expiry_date: Optional[datetime]

    class Config:
        from_attributes = True
