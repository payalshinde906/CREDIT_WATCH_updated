"""
OTP service
"""
from datetime import datetime, timedelta, timezone
from app.config import settings
from app.utils import format_phone_e164, is_valid_phone
from app.exceptions import InvalidPhone, OTPExpired, InvalidOTP
import logging
import random
import string

logger = logging.getLogger(__name__)

# In-memory OTP store (in production, use Redis)
otp_store = {}


class OTPService:
    """Generate, send, and verify OTPs"""

    @staticmethod
    async def send_otp(phone: str, reason: str = "phone_verification") -> dict:
        """
        Generate and send OTP
        
        Args:
            phone: Phone number
            reason: Reason for OTP
            
        Returns:
            Dict with sent status
        """
        # Validate phone
        if not is_valid_phone(phone):
            raise InvalidPhone()
        
        phone_e164 = format_phone_e164(phone)
        
        # Generate OTP (4-6 digits)
        otp_code = "".join(random.choices(string.digits, k=6))
        
        # Store OTP with expiry
        expiry = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
        otp_store[phone_e164] = {
            "code": otp_code,
            "expiry": expiry,
            "reason": reason,
            "attempts": 0,
        }
        
        logger.info(f"OTP generated for {phone_e164}: {otp_code}")
        
        # In development, return OTP in response for testing
        if settings.ENVIRONMENT == "development":
            return {
                "sent": True,
                "message": f"OTP sent (dev: {otp_code})",
                "otp_code": otp_code,  # Only in dev!
            }
        
        # In production, send via SMS/email
        # For now, we're using email as primary
        return {
            "sent": True,
            "message": "OTP sent to your email",
        }

    @staticmethod
    async def verify_otp(phone: str, otp_code: str) -> bool:
        """
        Verify OTP code
        
        Args:
            phone: Phone number
            otp_code: OTP code to verify
            
        Returns:
            True if valid
        """
        # Validate phone
        if not is_valid_phone(phone):
            raise InvalidPhone()
        
        phone_e164 = format_phone_e164(phone)
        
        # Check if OTP exists
        if phone_e164 not in otp_store:
            raise InvalidOTP("OTP not found. Request a new one.")
        
        otp_data = otp_store[phone_e164]
        
        # Check expiry
        if datetime.now(timezone.utc) > otp_data["expiry"]:
            del otp_store[phone_e164]
            raise OTPExpired()
        
        # Check attempts (max 3)
        if otp_data["attempts"] >= 3:
            del otp_store[phone_e164]
            raise InvalidOTP("Too many attempts. Request a new OTP.")
        
        # Verify code
        if otp_data["code"] != otp_code.strip():
            otp_data["attempts"] += 1
            raise InvalidOTP(f"Invalid OTP. {3 - otp_data['attempts']} attempts remaining.")
        
        # OTP verified, remove from store
        del otp_store[phone_e164]
        logger.info(f"OTP verified for {phone_e164}")
        
        return True

    @staticmethod
    def get_otp_expiry_minutes() -> int:
        """Get OTP expiry time in minutes"""
        return settings.OTP_EXPIRY_MINUTES

    @staticmethod
    async def send_otp_for_password_reset(email: str) -> dict:
        """
        Generate and send OTP for password reset
        
        Args:
            email: Email address
            
        Returns:
            Dict with sent status
        """
        if not email or "@" not in email:
            from app.exceptions import InvalidEmail
            raise InvalidEmail()
        
        # Generate OTP (6 digits)
        otp_code = "".join(random.choices(string.digits, k=6))
        
        # Store OTP with expiry (use email as key for password reset)
        expiry = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
        otp_store[f"password_reset:{email.lower()}"] = {
            "code": otp_code,
            "expiry": expiry,
            "reason": "password_reset",
            "attempts": 0,
        }
        
        logger.info(f"Password reset OTP generated for {email}: {otp_code}")
        
        # Send via email
        from app.services import EmailService
        await EmailService.send_otp_email(email, otp_code, "password reset")
        
        return {
            "sent": True,
            "message": "OTP sent to your email",
        }

    @staticmethod
    async def verify_otp_for_password_reset(email: str, otp_code: str) -> bool:
        """
        Verify password reset OTP
        
        Args:
            email: Email address
            otp_code: OTP code to verify
            
        Returns:
            True if valid
        """
        email_lower = email.lower()
        key = f"password_reset:{email_lower}"
        
        # Check if OTP exists
        if key not in otp_store:
            raise InvalidOTP("OTP not found. Request a new one.")
        
        otp_data = otp_store[key]
        
        # Check expiry
        if datetime.now(timezone.utc) > otp_data["expiry"]:
            del otp_store[key]
            raise OTPExpired()
        
        # Check attempts (max 3)
        if otp_data["attempts"] >= 3:
            del otp_store[key]
            raise InvalidOTP("Too many attempts. Request a new OTP.")
        
        # Verify code
        if otp_data["code"] != otp_code.strip():
            otp_data["attempts"] += 1
            raise InvalidOTP(f"Invalid OTP. {3 - otp_data['attempts']} attempts remaining.")
        
        # OTP verified, remove from store
        del otp_store[key]
        logger.info(f"Password reset OTP verified for {email}")
        
        return True
