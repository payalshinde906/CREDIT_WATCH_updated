"""
Authentication service
"""
from typing import Optional
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User, Subscription
from app.schemas import RegisterRequest, LoginRequest
from app.utils import (
    hash_password, verify_password, is_valid_gstin, is_valid_phone,
    format_phone_e164, create_access_token, create_refresh_token, decode_token, verify_token_type
)
from app.exceptions import InvalidGSTIN, InvalidPhone, InvalidCredentials, UserNotFound
from app.config import settings
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication and authorization service"""

    @staticmethod
    async def register(request: RegisterRequest, db: AsyncSession) -> dict:
        """
        Register new user
        
        Args:
            request: Registration request
            db: Database session
            
        Returns:
            User data with tokens
        """
        # Validate GSTIN
        if not is_valid_gstin(request.gstin):
            raise InvalidGSTIN()
        
        # Validate phone
        if not is_valid_phone(request.phone):
            raise InvalidPhone()
        
        phone_e164 = format_phone_e164(request.phone)
        
        # Check if user exists
        stmt = select(User).where(User.gstin == request.gstin.upper())
        existing = await db.execute(stmt)
        if existing.scalars().first():
            raise InvalidCredentials("GSTIN already registered")
        
        # Create user
        user = User(
            id=str(uuid4()),
            gstin=request.gstin.upper(),
            company_name=request.company_name,
            email=request.email.lower(),
            phone=phone_e164,
            password_hash=hash_password(request.password),
            is_active=True,
        )
        
        db.add(user)
        
        # Create default subscription (Base plan) - ONLY IF EXPLICITLY PURCHASED
        # Registration does NOT automatically create a subscription per requirement
        # User must purchase a plan from /membership
        
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"User registered: {user.id} ({user.gstin})")
        
        # Generate tokens
        tokens = AuthService._generate_tokens(user)
        
        return {
            "user": {
                "id": user.id,
                "gstin": user.gstin,
                "email": user.email,
                "company_name": user.company_name,
            },
            "tokens": tokens,
        }

    @staticmethod
    async def login(request: LoginRequest, db: AsyncSession) -> dict:
        """
        Login user
        
        Args:
            request: Login request
            db: Database session
            
        Returns:
            User data with tokens
        """
        # Validate GSTIN
        if not is_valid_gstin(request.gstin):
            raise InvalidGSTIN()
        
        # Find user by GSTIN
        stmt = select(User).where(User.gstin == request.gstin.upper(), User.is_active == True)
        result = await db.execute(stmt)
        user = result.scalars().first()
        
        if not user or not verify_password(request.password, user.password_hash):
            raise InvalidCredentials("Invalid GSTIN or password")
        
        logger.info(f"User logged in: {user.id}")
        
        # Generate tokens
        tokens = AuthService._generate_tokens(user)
        
        return {
            "user": {
                "id": user.id,
                "gstin": user.gstin,
                "email": user.email,
                "company_name": user.company_name,
            },
            "tokens": tokens,
        }

    @staticmethod
    async def refresh_access_token(refresh_token: str, db: AsyncSession) -> dict:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Refresh token
            db: Database session
            
        Returns:
            New access token
        """
        payload = decode_token(refresh_token)
        
        if not payload or not verify_token_type(payload, "refresh"):
            raise InvalidCredentials("Invalid or expired refresh token")
        
        user_id = payload.get("sub")
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            raise UserNotFound()
        
        # Generate new access token
        access_token = create_access_token({"sub": user.id})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    @staticmethod
    def _generate_tokens(user: User) -> dict:
        """
        Generate access and refresh tokens for user
        
        Args:
            user: User object
            
        Returns:
            Tokens dict
        """
        access_token = create_access_token({"sub": user.id})
        refresh_token = create_refresh_token({"sub": user.id})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    @staticmethod
    async def reset_password(email: str, otp_code: str, new_password: str, db: AsyncSession) -> dict:
        """
        Reset user password with verified OTP
        
        Args:
            email: User email
            otp_code: Verified OTP code
            new_password: New password
            db: Database session
            
        Returns:
            Success response
        """
        # Find user by email
        stmt = select(User).where(User.email == email.lower(), User.is_active == True)
        result = await db.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            raise UserNotFound()
        
        # Update password
        user.password_hash = hash_password(new_password)
        await db.commit()
        
        logger.info(f"Password reset for user: {user.id}")
        
        return {"message": "Password reset successful"}
