"""
Authentication service
"""
from typing import Optional
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from passlib.exc import PasswordValueError

from app.models import User   # or from app.__init__ import User
from app.schemas import RegisterRequest, LoginRequest
from app.utils import (
    hash_password,
    verify_password,
    is_valid_gstin,
    is_valid_phone,
    format_phone_e164,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type,
)
from app.services.otp_service import OTPService
from app.exceptions import (
    InvalidGSTIN,
    InvalidPhone,
    InvalidCredentials,
    UserNotFound,
    InvalidOTP,
    OTPExpired,
    DuplicateGSTIN,
)
from app.config import settings

import logging
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication and authorization service"""

    @staticmethod
    async def register(request: RegisterRequest, db: AsyncSession) -> dict:
        """Register new user"""

        if not is_valid_gstin(request.gstin):
            raise InvalidGSTIN()
        if not is_valid_phone(request.phone):
            raise InvalidPhone()

        phone_e164 = format_phone_e164(request.phone)

        stmt = select(User).where(User.gstin == request.gstin.upper())
        result = await db.execute(stmt)
        existing_user: Optional[User] = result.scalars().first()
        if existing_user:
            raise DuplicateGSTIN()

        try:
            password_hash: str = hash_password(request.password)
        except PasswordValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

        user = User(
            id=str(uuid4()),
            gstin=request.gstin.upper(),
            company_name=request.company_name,
            email=request.email.lower(),
            phone=phone_e164,
            password_hash=password_hash,
            is_active=True,
        )

        db.add(user)
        try:
            await db.commit()
        except IntegrityError as e:
            await db.rollback()
            msg = str(e.orig).lower() if getattr(e, "orig", None) else str(e).lower()
            if "gstin" in msg and "unique" in msg:
                raise DuplicateGSTIN()
            raise
        await db.refresh(user)

        logger.info(f"User registered: {user.id} ({user.gstin})")

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
        """Login user"""

        if not is_valid_gstin(request.gstin):
            raise InvalidGSTIN()

        stmt = select(User).where(
            User.gstin == request.gstin.upper(),
            User.is_active,
        )
        result = await db.execute(stmt)
        user: Optional[User] = result.scalars().first()

        if not user or not verify_password(request.password, user.password_hash):  # type: ignore
            raise InvalidCredentials("Invalid GSTIN or password")

        logger.info(f"User logged in: {user.id}")

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
    async def login_with_email_otp(email: str, gstin: str, otp_code: str, db: AsyncSession) -> dict:
        if not is_valid_gstin(gstin):
            raise InvalidGSTIN()
        try:
            await OTPService.verify_otp_for_login_email(email, otp_code)
        except (InvalidOTP, OTPExpired):
            raise InvalidCredentials("Invalid or expired OTP")
        stmt = select(User).where(
            User.email == email.lower(),
            User.gstin == gstin.upper(),
            User.is_active,
        )
        result = await db.execute(stmt)
        user: Optional[User] = result.scalars().first()
        if not user:
            raise UserNotFound()
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
        """Refresh access token"""

        payload = decode_token(refresh_token)

        if not payload or not verify_token_type(payload, "refresh"):
            raise InvalidCredentials("Invalid or expired refresh token")

        user_id = payload.get("sub")
        if not user_id or not isinstance(user_id, str):
            raise InvalidCredentials("Invalid token payload")

        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user: Optional[User] = result.scalars().first()

        if not user:
            raise UserNotFound()

        access_token = create_access_token({"sub": user.id})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    @staticmethod
    def _generate_tokens(user: User) -> dict:
        """Generate access & refresh tokens"""

        return {
            "access_token": create_access_token({"sub": user.id}),
            "refresh_token": create_refresh_token({"sub": user.id}),
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    @staticmethod
    async def reset_password(
        email: str,
        otp_code: str,
        new_password: str,
        db: AsyncSession,
    ) -> dict:
        """Reset password"""

        # Verify OTP before proceeding
        try:
            await OTPService.verify_otp_for_password_reset(email, otp_code)
        except (InvalidOTP, OTPExpired):
            raise InvalidCredentials("Invalid or expired OTP")

        stmt = select(User).where(
            User.email == email.lower(),
            User.is_active,
        )
        result = await db.execute(stmt)
        user: Optional[User] = result.scalars().first()

        if not user:
            raise UserNotFound()

        try:
            user.password_hash = hash_password(new_password)  # type: ignore
        except PasswordValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password contains invalid characters",
            )

        await db.commit()

        logger.info(f"Password reset for user: {user.id}")

        return {"message": "Password reset successful"}
