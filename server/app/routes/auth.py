"""
Authentication routes
"""
from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException
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
    EmailLoginSendOTPRequest,
    EmailLoginVerifyOTPRequest,
)
from app.services import AuthService, EmailService, OTPService
from app.utils import ResponseFormatter, format_phone_e164
from app.config import settings
from sqlalchemy import select
from app.models import Invitation, Company, User

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
        data={"sent": result["sent"]},
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

    # Block duplicate GSTIN 
    existing_gstin = await db.execute( 
        select(User).where(User.gstin == request.gstin.upper()) 
    ) 
    if existing_gstin.scalar_one_or_none(): 
        raise HTTPException( 
            status_code=400, 
            detail="This GSTIN is already registered. Please ask your company admin to invite you instead." 
        ) 

    result = await AuthService.register(request, db)

    # Extract company domain from email
    email_domain = request.email.split('@')[1] if '@' in request.email else ''
    
    # Update company_domain in companies table
    from app.models import Company
    stmt = select(Company).where(Company.id == result["user"]["company_id"])
    c_res = await db.execute(stmt)
    company = c_res.scalars().first()
    if company:
        company.company_domain = email_domain
        await db.commit()

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
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=result["tokens"]["refresh_token"],
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
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

    request_id = getattr(getattr(http_request, "state", None), "request_id", "") if http_request else ""
    
    # Include access_token in the response data for non-cookie clients (like Flutter)
    user_data = result["user"]
    user_data["access_token"] = result["tokens"]["access_token"]
    
    response_data = ResponseFormatter.create_success(
        data=user_data,
        message="Login successful",
        request_id=request_id,
    )

    response = JSONResponse(content=response_data)

    response.set_cookie(
        key="access_token",
        value=result["tokens"]["access_token"],
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=result["tokens"]["refresh_token"],
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/",
    )

    return response

# ---------------- EMAIL OTP LOGIN ----------------


@router.post("/login/send-email-otp")
async def login_send_email_otp(
    request: EmailLoginSendOTPRequest,
    http_request: Request,
):
    print(f"DEBUG: auth.py - Received login_send_email_otp for {request.email}")
    try:
        result = await OTPService.send_otp_for_login_email(request.email)
        logger.info(f"Login OTP sent to {request.email}")
        return ResponseFormatter.create_success(
            data={"sent": result["sent"]},
            message="OTP sent to email",
            request_id=http_request.state.request_id,
        )
    except Exception as e:
        print(f"DEBUG: auth.py - Caught exception: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


@router.post("/login/verify-email-otp")
async def login_verify_email_otp(
    request: EmailLoginVerifyOTPRequest,
    db: AsyncSession = Depends(get_db),
    http_request: Request = None,
):
    result = await AuthService.login_with_email_otp(request.email, request.gstin, request.otp_code, db)
    request_id = getattr(getattr(http_request, "state", None), "request_id", "") if http_request else ""
    
    # Include access_token in the response data for non-cookie clients (like Flutter)
    user_data = result["user"]
    user_data["access_token"] = result["tokens"]["access_token"]
    
    response_data = ResponseFormatter.create_success(
        data=user_data,
        message="Login successful",
        request_id=request_id,
    )
    response = JSONResponse(content=response_data)
    response.set_cookie(
        key="access_token",
        value=result["tokens"]["access_token"],
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=result["tokens"]["refresh_token"],
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/",
    )
    return response

# ---------------- INVITATION ACCEPT ----------------
@router.post("/invitations/accept")
async def accept_invitation(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    http_request: Request = None,
):
    token = payload.get("token")
    email = payload.get("email", "").lower()
    password = payload.get("password", "")
    if not token or not email or not password:
        raise HTTPException(status_code=400, detail="Missing token, email, or password")
    stmt = select(Invitation).where(Invitation.token == token, Invitation.status == "PENDING")
    result = await db.execute(stmt)
    inv = result.scalars().first()
    if not inv:
        raise HTTPException(status_code=400, detail="Invalid or expired invitation")
    from datetime import datetime as _dt
    if inv.expires_at and inv.expires_at < _dt.utcnow():
        raise HTTPException(status_code=400, detail="Invitation expired")
    from passlib.exc import PasswordValueError
    from app.utils import hash_password
    try:
        password_hash = hash_password(password)
    except PasswordValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    company_stmt = select(Company).where(Company.id == inv.company_id)
    cres = await db.execute(company_stmt)
    company = cres.scalars().first()
    if not company:
        raise HTTPException(status_code=400, detail="Company not found")
    if "@" not in email or email.split("@", 1)[1] != company.domain_name:
        raise HTTPException(status_code=400, detail="Email domain mismatch")
    # Check duplicate email
    existing_stmt = select(User).where(User.email == email)
    existing_res = await db.execute(existing_stmt)
    existing_user = existing_res.scalars().first()
    if existing_user:
        # If user already belongs to same company, treat as accepted
        if existing_user.company_id == company.id:
            inv.status = "ACCEPTED"
            await db.commit()
            tokens = AuthService._generate_tokens(existing_user)
            request_id = getattr(getattr(http_request, "state", None), "request_id", "") if http_request else ""
            response_data = ResponseFormatter.create_success(
                data={"user": {"id": existing_user.id, "email": existing_user.email, "company_id": existing_user.company_id, "role": existing_user.role}, "tokens": tokens},
                message="Invitation accepted",
                request_id=request_id,
            )
            return JSONResponse(content=response_data)
        # Otherwise, duplicate email on different company
        raise HTTPException(status_code=400, detail="Email already registered")
    from uuid import uuid4
    user = User(
        id=str(uuid4()),
        company_id=company.id,
        name=email.split("@", 1)[0],
        email=email,
        password_hash=password_hash,
        role="USER",
        status="ACTIVE",
        is_active=True,
        company_name=company.company_name,
        gstin=company.gstin,
    )
    db.add(user)
    inv.status = "ACCEPTED"
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        from sqlalchemy.exc import IntegrityError
        if isinstance(e, IntegrityError):
            err = str(getattr(e, "orig", e)).lower()
            if "email" in err:
                raise HTTPException(status_code=409, detail="Email already registered")
            if "gstin" in err:
                raise HTTPException(status_code=409, detail="GSTIN conflict within company")
        raise HTTPException(status_code=400, detail="Failed to accept invitation")
    await db.refresh(user)
    tokens = AuthService._generate_tokens(user)
    response_data = ResponseFormatter.create_success(
        data={"user": {"id": user.id, "email": user.email, "company_id": user.company_id, "role": user.role}, "tokens": tokens},
        message="Invitation accepted",
        request_id=http_request.state.request_id,
    )
    return JSONResponse(content=response_data)


# ---------------- REFRESH TOKEN ----------------
@router.post("/refresh")
async def refresh_token(
    request: Optional[RefreshTokenRequest] = None,
    db: AsyncSession = Depends(get_db),
    http_request: Request = None,
):
    try:
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
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            path="/",
        )
        return response
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content=ResponseFormatter.create_error(
                "TOKEN_REFRESH_FAILED" if e.status_code >= 400 else "ERROR",
                str(e.detail),
                e.status_code,
                {},
                getattr(http_request.state, "request_id", None),
            ),
        )
    except Exception as e:
        # Always return JSON on unexpected failures
        return JSONResponse(
            status_code=500,
            content=ResponseFormatter.create_error(
                "INTERNAL_SERVER_ERROR",
                "Failed to refresh token",
                500,
                {"cause": str(e)},
                getattr(http_request.state, "request_id", None),
            ),
        )


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

    request_id = getattr(getattr(http_request, "state", None), "request_id", "") if http_request else ""
    return ResponseFormatter.create_success(
        message="OTP verified",
        request_id=request_id,
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

    request_id = getattr(getattr(http_request, "state", None), "request_id", "") if http_request else ""
    return ResponseFormatter.create_success(
        message="OTP verified",
        request_id=request_id,
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
