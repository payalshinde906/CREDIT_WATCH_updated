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
    async def send_otp(phone: str, reason: str = "phone_verification", email: str = None) -> dict:
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
        
        # Send OTP via email (if email is available) or SMS
        # For phone verification, we need to get email from user context
        # For now, send via SMS provider if configured, otherwise log
        sent_via = None
        
        # Try to send via SMS if Twilio is configured
        if settings.OTP_PROVIDER == "twilio" and settings.TWILIO_ACCOUNT_SID:
            try:
                from twilio.rest import Client
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                message = client.messages.create(
                    body=f"Your OTP code is {otp_code}. Valid for {settings.OTP_EXPIRY_MINUTES} minutes.",
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=phone_e164
                )
                sent_via = "SMS"
                logger.info(f"OTP sent via SMS to {phone_e164}")
            except Exception as e:
                logger.warning(f"Failed to send SMS: {e}. Falling back to email.")
        
        # If SMS failed or not configured, try email
        if not sent_via and email:
            try:
                from app.services import EmailService
                await EmailService.send_otp_email(email, otp_code, reason)
                sent_via = "email"
                logger.info(f"OTP sent via email to {email}")
            except Exception as e:
                logger.warning(f"Failed to send email: {e}")
        
        # In development, also log to console for testing
        if settings.ENVIRONMENT == "development":
            logger.info(f"[DEV] OTP for {phone_e164}: {otp_code}")
            if not sent_via:
                logger.warning(f"[DEV] OTP NOT SENT - Configure SMTP or Twilio to send OTPs")
            return {
                "sent": bool(sent_via),
                "message": f"OTP {'sent via ' + sent_via if sent_via else 'NOT SENT - check logs'} (dev: OTP={otp_code})",
                "otp_code": otp_code,  # Always show in dev for testing
            }
        
        if not sent_via:
            logger.error(f"OTP generated but NOT SENT to {phone_e164}. Configure SMTP or Twilio.")
            return {
                "sent": False,
                "message": "OTP generation failed. Please configure email/SMS service.",
            }
        
        return {
            "sent": True,
            "message": f"OTP sent via {sent_via}",
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
    async def send_otp_for_email_change(new_email: str, current_email: str) -> dict:
        """
        Generate and send OTP for email change
        Sends OTP to both current and new email addresses
        
        Args:
            new_email: New email address
            current_email: Current email address
            
        Returns:
            Dict with sent status
        """
        if not new_email or "@" not in new_email:
            from app.exceptions import InvalidEmail
            raise InvalidEmail()
        
        # Generate OTP (6 digits)
        otp_code = "".join(random.choices(string.digits, k=6))
        
        # Store OTP with expiry (use new_email as key for email change)
        expiry = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
        otp_store[f"email_change:{new_email.lower()}"] = {
            "code": otp_code,
            "expiry": expiry,
            "reason": "email_change",
            "attempts": 0,
        }
        
        logger.info(f"Email change OTP generated for {new_email}: {otp_code}")
        
        # Send OTP to new email
        from app.services import EmailService
        await EmailService.send_otp_email(new_email, otp_code, "email change")
        
        # Also send to current email for security
        await EmailService.send_otp_email(current_email, otp_code, "email change verification")
        
        return {
            "sent": True,
            "message": "OTP sent to both current and new email addresses",
            "otp_code": otp_code if settings.ENVIRONMENT == "development" else None,
        }

    @staticmethod
    async def verify_otp_for_email_change(new_email: str, otp_code: str) -> bool:
        """
        Verify email change OTP
        
        Args:
            new_email: New email address
            otp_code: OTP code to verify
            
        Returns:
            True if valid
        """
        email_lower = new_email.lower()
        key = f"email_change:{email_lower}"
        
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
        logger.info(f"Email change OTP verified for {new_email}")
        
        return True

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
