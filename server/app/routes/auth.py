"""
Authentication routes
"""
from typing import Optional
from fastapi import APIRouter, Depends, Response, Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import RegisterRequest, RegisterSendOTPRequest, LoginRequest, RefreshTokenRequest, SendOTPRequest, VerifyOTPRequest
from app.services import AuthService, EmailService, OTPService
from app.utils import ResponseFormatter, format_phone_e164
from app.config import settings
from app.dependencies import get_current_user
from app.models import User
import logging

logger = logging.getLogger(__name__)

JSON_MEDIA_TYPE = "application/json"

router = APIRouter()


@router.post("/register/send-otp")
async def register_send_otp(request: RegisterSendOTPRequest, http_request: Request = None):
    """Send OTP for registration verification"""
    try:
        from app.utils import format_phone_e164, is_valid_phone
        from app.exceptions import InvalidPhone
        
        # Validate phone
        phone_e164 = format_phone_e164(request.phone)
        if not phone_e164 or not is_valid_phone(request.phone):
            raise InvalidPhone()
        
        # Send OTP to both email and phone
        result = await OTPService.send_otp(phone_e164, "registration", email=request.email)
        
        request_id = http_request.state.request_id if http_request else ""
        return ResponseFormatter.create_success(
            data={"sent": result["sent"], "otp_code": result.get("otp_code")},  # otp_code only in dev
            message=result.get("message", "OTP sent"),
            request_id=request_id
        )
    except Exception as e:
        logger.error(f"Registration OTP error: {str(e)}")
        raise


@router.post("/register")
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db), http_request: Request = None):
    """Register new user (requires OTP verification)"""
    try:
        # Verify OTP if provided
        if request.otp_code:
            from app.utils import format_phone_e164
            phone_e164 = format_phone_e164(request.phone) or request.phone
            try:
                await OTPService.verify_otp(phone_e164, request.otp_code)
            except Exception as e:
                logger.error(f"OTP verification failed: {str(e)}")
                from app.exceptions import InvalidOTP
                raise InvalidOTP("Invalid or expired OTP. Please request a new one.")
        
        result = await AuthService.register(request, db)
        
        # Send welcome email
        sanitized_phone = format_phone_e164(request.phone) or request.phone
        await EmailService.send_registration_email(
            request.email,
            request.company_name,
            sanitized_phone
        )
        
        request_id = http_request.state.request_id if http_request else ""
        response_data = ResponseFormatter.create_success(
            data=result["user"],
            message="Registration successful",
            request_id=request_id
        )
        
        # Return tokens in httpOnly cookies
        response = JSONResponse(content=response_data)
        response.set_cookie(
            key="access_token",
            value=result["tokens"]["access_token"],
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            domain=settings.COOKIE_DOMAIN,
            path=settings.COOKIE_PATH,
        )
        response.set_cookie(
            key="refresh_token",
            value=result["tokens"]["refresh_token"],
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            domain=settings.COOKIE_DOMAIN,
            path=settings.COOKIE_PATH,
        )
        
        return response
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise


@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db), http_request: Request = None):
    """Login user"""
    try:
        result = await AuthService.login(request, db)
        
        request_id = http_request.state.request_id if http_request else ""
        response_data = ResponseFormatter.create_success(
            data=result["user"],
            message="Login successful",
            request_id=request_id
        )
        
        response = JSONResponse(content=response_data)
        response.set_cookie(
            key="access_token",
            value=result["tokens"]["access_token"],
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            domain=settings.COOKIE_DOMAIN,
            path=settings.COOKIE_PATH,
        )
        response.set_cookie(
            key="refresh_token",
            value=result["tokens"]["refresh_token"],
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            domain=settings.COOKIE_DOMAIN,
            path=settings.COOKIE_PATH,
        )
        
        return response
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise


@router.post("/refresh")
async def refresh_token(request: Optional[RefreshTokenRequest] = None, db: AsyncSession = Depends(get_db), http_request: Request = None):
    """Refresh access token using refresh token from body or cookies"""
    try:
        refresh_token_value = None
        
        # Try to get refresh token from request body first
        if request and request.refresh_token:
            refresh_token_value = request.refresh_token
        
        # If not in body, try to get from cookies
        if not refresh_token_value and http_request:
            refresh_token_value = http_request.cookies.get("refresh_token")
        
        if not refresh_token_value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not provided"
            )
        
        result = await AuthService.refresh_access_token(refresh_token_value, db)
        
        request_id = http_request.state.request_id if http_request else ""
        response_data = ResponseFormatter.create_success(
            data=result,
            message="Token refreshed",
            request_id=request_id
        )
        
        response = JSONResponse(content=response_data)
        response.set_cookie(
            key="access_token",
            value=result["access_token"],
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            domain=settings.COOKIE_DOMAIN,
            path=settings.COOKIE_PATH,
        )
        
        return response
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise


@router.post("/logout")
async def logout(http_request: Request = None):
    """Logout user (clear cookies)"""
    request_id = http_request.state.request_id if http_request else ""
    response_data = ResponseFormatter.create_success(
        message="Logged out successfully",
        request_id=request_id
    )
    
    response = JSONResponse(content=response_data)
    response.delete_cookie("access_token", domain=settings.COOKIE_DOMAIN, path=settings.COOKIE_PATH)
    response.delete_cookie("refresh_token", domain=settings.COOKIE_DOMAIN, path=settings.COOKIE_PATH)
    
    return response


@router.post("/otp/send")
async def send_otp(request: SendOTPRequest, http_request: Request = None):
    """Send OTP for phone verification"""
    try:
        result = await OTPService.send_otp(request.phone, "phone_verification")
        
        request_id = http_request.state.request_id if http_request else ""
        return ResponseFormatter.create_success(
            data={"sent": result["sent"]},
            message=result["message"],
            request_id=request_id
        )
    except Exception as e:
        logger.error(f"Send OTP error: {str(e)}")
        raise


@router.post("/otp/verify")
async def verify_otp(request: VerifyOTPRequest, http_request: Request = None):
    """Verify OTP code"""
    try:
        await OTPService.verify_otp(request.phone, request.otp_code)
        
        request_id = http_request.state.request_id if http_request else ""
        return ResponseFormatter.create_success(
            message="OTP verified successfully",
            request_id=request_id
        )
    except Exception as e:
        logger.error(f"Verify OTP error: {str(e)}")
        raise


@router.post("/password/send-otp")
async def send_password_reset_otp(request: dict, http_request: Request = None):
    """Send OTP for password reset"""
    try:
        email = (request.get("email") or "").strip().lower()
        if not email or "@" not in email:
            from app.exceptions import InvalidEmail
            raise InvalidEmail()
        
        result = await OTPService.send_otp_for_password_reset(email)
        
        request_id = http_request.state.request_id if http_request else ""
        return ResponseFormatter.create_success(
            data={"sent": result["sent"]},
            message=result["message"],
            request_id=request_id
        )
    except Exception as e:
        logger.error(f"Send password reset OTP error: {str(e)}")
        raise


@router.post("/password/verify-otp")
async def verify_password_reset_otp(request: dict, http_request: Request = None):
    """Verify OTP for password reset"""
    try:
        email = (request.get("email") or "").strip().lower()
        otp_code = (request.get("otp_code") or "").strip()
        
        await OTPService.verify_otp_for_password_reset(email, otp_code)
        
        request_id = http_request.state.request_id if http_request else ""
        return ResponseFormatter.create_success(
            message="OTP verified successfully",
            request_id=request_id
        )
    except Exception as e:
        logger.error(f"Verify password reset OTP error: {str(e)}")
        raise


@router.post("/password/reset")
async def reset_password(request: dict, db: AsyncSession = Depends(get_db), http_request: Request = None):
    """Reset password with verified OTP"""
    try:
        email = (request.get("email") or "").strip().lower()
        otp_code = (request.get("otp_code") or "").strip()
        password = request.get("password") or ""
        
        if not password or len(password) < 6:
            from app.exceptions import InvalidPassword
            raise InvalidPassword()
        
        await AuthService.reset_password(email, otp_code, password, db)
        
        request_id = http_request.state.request_id if http_request else ""
        return ResponseFormatter.create_success(
            message="Password reset successful",
            request_id=request_id
        )
    except Exception as e:
        logger.error(f"Reset password error: {str(e)}")
        raise
