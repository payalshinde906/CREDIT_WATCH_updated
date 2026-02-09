"""
Authentication routes
"""
from typing import Optional
from fastapi import APIRouter, Depends, Response, Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.database import get_db
from app.schemas import (
    RegisterRequest,
    RegisterSendOTPRequest,
    LoginRequest,
    RefreshTokenRequest,
    SendOTPRequest,
    VerifyOTPRequest,
)
from app.services import AuthService, EmailService, OTPService
from app.utils import ResponseFormatter, format_phone_e164
from app.config import settings
from app.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------- REGISTER OTP ----------------
@router.post("/register/send-otp")
async def register_send_otp(request: RegisterSendOTPRequest, http_request: Request):
    phone_e164 = format_phone_e164(request.phone)

    result = await OTPService.send_otp(
        phone_e164, "registration", email=request.email
    )

    return ResponseFormatter.create_success(
        data={"sent": result["sent"], "otp_code": result.get("otp_code")},
        message="OTP sent successfully",
        request_id=http_request.state.request_id,
    )


# ---------------- REGISTER ----------------
@router.post("/register")
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    http_request: Request = None,
):
    if request.otp_code:
        phone_e164 = format_phone_e164(request.phone)
        await OTPService.verify_otp(phone_e164, request.otp_code)

    result = await AuthService.register(request, db)

    await EmailService.send_registration_email(
        request.email, request.company_name, request.phone
    )

    request_id = getattr(getattr(http_request, "state", None), "request_id", "") if http_request else ""
    response_data = ResponseFormatter.create_success(
        data=result["user"],
        message="Registration successful",
        request_id=request_id,
    )

    response = JSONResponse(content=response_data)

    # ✅ FIXED COOKIE SETTING (NO DOMAIN)
    response.set_cookie(
        key="access_token",
        value=result["tokens"]["access_token"],
        httponly=True,
        secure=False,        # localhost
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=result["tokens"]["refresh_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/",
    )

    return response


# ---------------- LOGIN ----------------
@router.post("/login")
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
    http_request: Request = None,
):
    result = await AuthService.login(request, db)

    response_data = ResponseFormatter.create_success(
        data=result["user"],
        message="Login successful",
        request_id=http_request.state.request_id,
    )

    response = JSONResponse(content=response_data)

    response.set_cookie(
        key="access_token",
        value=result["tokens"]["access_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=result["tokens"]["refresh_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/",
    )

    return response


# ---------------- REFRESH TOKEN ----------------
@router.post("/refresh")
async def refresh_token(
    request: Optional[RefreshTokenRequest] = None,
    db: AsyncSession = Depends(get_db),
    http_request: Request = None,
):
    refresh_token_value = None

    if request and request.refresh_token:
        refresh_token_value = request.refresh_token
    else:
        refresh_token_value = http_request.cookies.get("refresh_token")

    if not refresh_token_value:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    result = await AuthService.refresh_access_token(refresh_token_value, db)

    response_data = ResponseFormatter.create_success(
        data=result,
        message="Token refreshed",
        request_id=http_request.state.request_id,
    )

    response = JSONResponse(content=response_data)

    response.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    return response


# ---------------- LOGOUT ----------------
@router.post("/logout")
async def logout(http_request: Request):
    response_data = ResponseFormatter.create_success(
        message="Logged out successfully",
        request_id=http_request.state.request_id,
    )

    response = JSONResponse(content=response_data)

    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")

    return response


# ---------------- OTP ----------------
@router.post("/otp/send")
async def send_otp(request: SendOTPRequest, http_request: Request):
    result = await OTPService.send_otp(request.phone, "phone_verification")

    return ResponseFormatter.create_success(
        data={"sent": result["sent"]},
        message="OTP sent",
        request_id=http_request.state.request_id,
    )


@router.post("/otp/verify")
async def verify_otp(request: VerifyOTPRequest, http_request: Request):
    await OTPService.verify_otp(request.phone, request.otp_code)

    return ResponseFormatter.create_success(
        message="OTP verified",
        request_id=http_request.state.request_id,
    )


# ---------------- PASSWORD RESET ----------------
@router.post("/password/send-otp")
async def send_password_reset_otp(request: dict, http_request: Request):
    email = request.get("email", "").strip().lower()
    result = await OTPService.send_otp_for_password_reset(email)

    return ResponseFormatter.create_success(
        data={"sent": result["sent"]},
        message="OTP sent",
        request_id=http_request.state.request_id,
    )


@router.post("/password/verify-otp")
async def verify_password_reset_otp(request: dict, http_request: Request):
    await OTPService.verify_otp_for_password_reset(
        request.get("email"), request.get("otp_code")
    )

    return ResponseFormatter.create_success(
        message="OTP verified",
        request_id=http_request.state.request_id,
    )


@router.post("/password/reset")
async def reset_password(
    request: dict,
    db: AsyncSession = Depends(get_db),
    http_request: Request = None,
):
    await AuthService.reset_password(
        request.get("email"),
        request.get("otp_code"),
        request.get("password"),
        db,
    )

    return ResponseFormatter.create_success(
        message="Password reset successful",
        request_id=http_request.state.request_id,
    )
