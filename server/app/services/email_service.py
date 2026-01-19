"""
Secure and Production-Ready Email Service Module
Supports Gmail SMTP with SMTP_SSL (port 465)
Framework-agnostic and compatible with FastAPI
"""
import smtplib
import ssl
import logging
from email.message import EmailMessage
from typing import Optional, List

logger = logging.getLogger(__name__)

# Import settings from config (handles .env file loading via Pydantic)
try:
    from app.config import settings
except ImportError:
    # Fallback for standalone usage (not within FastAPI app)
    import os
    from typing import Any
    
    class _Settings:
        def __init__(self):
            self.GOOGLE_SMTP_HOST = os.getenv("GOOGLE_SMTP_HOST", "smtp.gmail.com")
            self.GOOGLE_SMTP_PORT = int(os.getenv("GOOGLE_SMTP_PORT", "465"))
            self.GOOGLE_SMTP_USER = os.getenv("GOOGLE_SMTP_USER", "")
            self.GOOGLE_SMTP_PASSWORD = os.getenv("GOOGLE_SMTP_PASSWORD", "")
            self.SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
            self.SMTP_TIMEOUT = int(os.getenv("SMTP_TIMEOUT", "30"))
            self.OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", "10"))
    
    settings = _Settings()


class EmailServiceError(Exception):
    """Custom exception for email service errors"""
    pass


class EmailService:
    """
    Secure email service using Gmail SMTP with SMTP_SSL (port 465)
    
    This service is framework-agnostic and can be used with FastAPI,
    Django, Flask, or standalone Python applications.
    
    Requirements:
        - Gmail account with App Password (not regular password)
        - Environment variables configured:
            * GOOGLE_SMTP_USER: Gmail address
            * GOOGLE_SMTP_PASSWORD: App Password
            * SENDER_EMAIL: (optional) defaults to GOOGLE_SMTP_USER
    """

    @staticmethod
    def _validate_config() -> tuple[str, str]:
        """
        Validate SMTP configuration
        
        Returns:
            Tuple of (smtp_user, sender_email)
            
        Raises:
            EmailServiceError: If configuration is invalid
        """
        smtp_user = settings.GOOGLE_SMTP_USER
        smtp_password = settings.GOOGLE_SMTP_PASSWORD
        
        if not smtp_user or not smtp_password:
            raise EmailServiceError(
                "SMTP credentials not configured. Set GOOGLE_SMTP_USER and GOOGLE_SMTP_PASSWORD environment variables."
            )
        
        # Gmail requires sender email to match authenticated user
        # If SENDER_EMAIL is different, use GOOGLE_SMTP_USER instead
        sender_email = settings.SENDER_EMAIL or smtp_user
        if sender_email != smtp_user:
            logger.warning(
                f"Sender email ({sender_email}) differs from SMTP user ({smtp_user}). "
                "Gmail requires sender to match authenticated user. Using GOOGLE_SMTP_USER as sender."
            )
            sender_email = smtp_user
        
        return smtp_user, sender_email

    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        html_body: str,
        plain_text_body: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> bool:
        """
        Send an email using Gmail SMTP_SSL (port 465)
        
        This is the main reusable function for sending emails.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_body: HTML content of the email
            plain_text_body: Optional plain text version (falls back to HTML if not provided)
            cc: Optional list of CC recipients
            bcc: Optional list of BCC recipients
            
        Returns:
            True if email sent successfully, False otherwise
            
        Raises:
            EmailServiceError: For configuration or connection errors
        """
        try:
            # Validate configuration
            smtp_user, sender_email = EmailService._validate_config()
            
            # Get SMTP password from settings
            smtp_password = settings.GOOGLE_SMTP_PASSWORD
            
            # Validate recipient email
            if not to_email or "@" not in to_email:
                raise EmailServiceError(f"Invalid recipient email: {to_email}")
            
            # Create EmailMessage (recommended over MIMEMultipart)
            msg = EmailMessage()
            msg["From"] = sender_email
            msg["To"] = to_email
            msg["Subject"] = subject
            
            if cc:
                msg["Cc"] = ", ".join(cc)
            if bcc:
                msg["Bcc"] = ", ".join(bcc)
            
            # Set email content
            # Try plain text first, fall back to HTML if not provided
            if plain_text_body:
                msg.set_content(plain_text_body)
                msg.add_alternative(html_body, subtype="html")
            else:
                # If no plain text provided, use HTML as primary content
                msg.set_content(html_body, subtype="html")
            
            # Create SSL context for secure connection
            context = ssl.create_default_context()
            
            # Get SMTP configuration from settings
            smtp_host = settings.GOOGLE_SMTP_HOST
            smtp_port = settings.GOOGLE_SMTP_PORT
            smtp_timeout = settings.SMTP_TIMEOUT
            
            # Connect using SMTP_SSL (NOT starttls)
            try:
                with smtplib.SMTP_SSL(
                    smtp_host,
                    smtp_port,
                    context=context,
                    timeout=smtp_timeout
                ) as server:
                    # Login with Gmail credentials
                    server.login(smtp_user, smtp_password)
                    
                    # Send email
                    recipients = [to_email]
                    if cc:
                        recipients.extend(cc)
                    if bcc:
                        recipients.extend(bcc)
                    
                    server.send_message(msg, from_addr=sender_email, to_addrs=recipients)
                    
                    logger.info(f"Email sent successfully to {to_email} | Subject: {subject}")
                    return True
                    
            except smtplib.SMTPAuthenticationError as e:
                error_msg = (
                    "SMTP authentication failed. Check your Gmail App Password. "
                    "Make sure GOOGLE_SMTP_USER and GOOGLE_SMTP_PASSWORD are correct."
                )
                logger.error(f"{error_msg} Error: {str(e)}")
                raise EmailServiceError(error_msg) from e
                
            except smtplib.SMTPRecipientsRefused as e:
                error_msg = f"Recipient email rejected: {to_email}"
                logger.error(f"{error_msg} Error: {str(e)}")
                raise EmailServiceError(error_msg) from e
                
            except smtplib.SMTPServerDisconnected as e:
                error_msg = "SMTP server disconnected unexpectedly"
                logger.error(f"{error_msg} Error: {str(e)}")
                raise EmailServiceError(error_msg) from e
                
            except (smtplib.SMTPException, OSError, TimeoutError) as e:
                error_msg = f"SMTP connection error: {str(e)}"
                logger.error(error_msg)
                raise EmailServiceError(error_msg) from e
                
        except EmailServiceError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            error_msg = f"Unexpected error sending email to {to_email}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise EmailServiceError(error_msg) from e

    @staticmethod
    async def send_otp_email(
        to_email: str,
        otp_code: str,
        reason: str = "verification",
        expiry_minutes: Optional[int] = None
    ) -> bool:
        """
        Send OTP (One-Time Password) email
        
        Args:
            to_email: Recipient email address
            otp_code: 6-digit OTP code
            reason: Reason for OTP (e.g., "phone verification", "password reset")
            expiry_minutes: OTP expiry time in minutes (defaults to settings.OTP_EXPIRY_MINUTES)
            
        Returns:
            True if sent successfully, False otherwise
        """
        if expiry_minutes is None:
            expiry_minutes = settings.OTP_EXPIRY_MINUTES
        subject = f"Your OTP for {reason}"
        
        # Plain text version for better email client compatibility
        plain_text = f"""
Your OTP Code: {otp_code}

This code will expire in {expiry_minutes} minutes.

Do not share this code with anyone.

If you did not request this code, please ignore this email.
        """.strip()
        
        # HTML version
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>OTP Verification</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                <h2 style="color: #007bff; margin-top: 0;">OTP Verification</h2>
                <p>Your OTP code is:</p>
                <div style="background-color: #ffffff; border: 2px solid #007bff; border-radius: 6px; padding: 15px; text-align: center; margin: 20px 0;">
                    <span style="font-size: 32px; font-weight: bold; color: #007bff; font-family: 'Courier New', monospace; letter-spacing: 4px;">
                        {otp_code}
                    </span>
                </div>
                <p style="color: #666; font-size: 14px;">
                    This code will expire in <strong>{expiry_minutes} minutes</strong>.
                </p>
                <p style="color: #dc3545; font-size: 14px; font-weight: bold;">
                    ⚠️ Do not share this code with anyone.
                </p>
                <hr style="border: none; border-top: 1px solid #dee2e6; margin: 20px 0;">
                <p style="color: #6c757d; font-size: 12px;">
                    If you did not request this code, please ignore this email.
                </p>
            </div>
        </body>
        </html>
        """
        
        try:
            return EmailService.send_email(
                to_email=to_email,
                subject=subject,
                html_body=html_body,
                plain_text_body=plain_text
            )
        except EmailServiceError as e:
            logger.error(f"Failed to send OTP email to {to_email}: {str(e)}")
            return False

    @staticmethod
    async def send_password_reset_email(
        to_email: str,
        reset_token: str,
        reset_url: Optional[str] = None
    ) -> bool:
        """
        Send password reset email
        
        Args:
            to_email: Recipient email address
            reset_token: Password reset token
            reset_url: Optional reset URL (if provided, will be included in email)
            expiry_minutes: Token expiry time in minutes
            
        Returns:
            True if sent successfully, False otherwise
        """
        subject = "Password Reset Request"
        
        # Plain text version
        plain_text = f"""
Password Reset Request

A password reset was requested for your account.

Reset Token: {reset_token}

{''.join([f'Reset URL: {reset_url}', '']) if reset_url else 'Use the token above to reset your password.'}

This token will expire in 30 minutes.

If you did not request this reset, please ignore this email and your password will remain unchanged.
        """.strip()
        
        # HTML version
        reset_link_html = ""
        if reset_url:
            reset_link_html = f'<p><a href="{reset_url}" style="background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 10px 0;">Reset Password</a></p>'
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; border-radius: 8px; padding: 20px;">
                <h2 style="color: #dc3545; margin-top: 0;">Password Reset Request</h2>
                <p>A password reset was requested for your account.</p>
                {reset_link_html if reset_url else f'<p>Reset Token: <code style="background-color: #e9ecef; padding: 4px 8px; border-radius: 4px; font-family: monospace;">{reset_token}</code></p>'}
                <p style="color: #666; font-size: 14px;">
                    This token will expire in <strong>30 minutes</strong>.
                </p>
                <hr style="border: none; border-top: 1px solid #dee2e6; margin: 20px 0;">
                <p style="color: #6c757d; font-size: 12px;">
                    If you did not request this reset, please ignore this email and your password will remain unchanged.
                </p>
            </div>
        </body>
        </html>
        """
        
        try:
            return EmailService.send_email(
                to_email=to_email,
                subject=subject,
                html_body=html_body,
                plain_text_body=plain_text
            )
        except EmailServiceError as e:
            logger.error(f"Failed to send password reset email to {to_email}: {str(e)}")
            return False

    @staticmethod
    async def send_notification_email(
        to_email: str,
        title: str,
        message: str,
        notification_type: str = "info"
    ) -> bool:
        """
        Send notification email
        
        Args:
            to_email: Recipient email address
            title: Notification title
            message: Notification message (can be HTML)
            notification_type: Type of notification ("info", "success", "warning", "error")
            
        Returns:
            True if sent successfully, False otherwise
        """
        # Color mapping for notification types
        color_map = {
            "info": "#007bff",
            "success": "#28a745",
            "warning": "#ffc107",
            "error": "#dc3545"
        }
        color = color_map.get(notification_type.lower(), "#007bff")
        
        subject = f"Notification: {title}"
        
        # Plain text version (strip HTML tags for basic compatibility)
        import re
        plain_text = re.sub(r'<[^>]+>', '', message).strip()
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; border-left: 4px solid {color}; border-radius: 8px; padding: 20px;">
                <h2 style="color: {color}; margin-top: 0;">{title}</h2>
                <div style="color: #333;">
                    {message}
                </div>
            </div>
        </body>
        </html>
        """
        
        try:
            return EmailService.send_email(
                to_email=to_email,
                subject=subject,
                html_body=html_body,
                plain_text_body=plain_text
            )
        except EmailServiceError as e:
            logger.error(f"Failed to send notification email to {to_email}: {str(e)}")
            return False

    @staticmethod
    async def send_registration_email(
        email: str,
        company_name: str,
        phone: str
    ) -> bool:
        """
        Send registration confirmation email (for backward compatibility)
        
        Args:
            email: Recipient email
            company_name: Company name
            phone: Phone number
            
        Returns:
            True if sent successfully
        """
        subject = "Welcome to CreditDataWatch"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; border-radius: 8px; padding: 20px;">
                <h2 style="color: #007bff; margin-top: 0;">Welcome to CreditDataWatch!</h2>
                <p>Hi {company_name},</p>
                <p>Your account has been successfully created.</p>
                <div style="background-color: #ffffff; border-radius: 6px; padding: 15px; margin: 20px 0;">
                    <p><strong>Account Details:</strong></p>
                    <ul>
                        <li>Email: {email}</li>
                        <li>Phone: {phone}</li>
                    </ul>
                </div>
                <p>You can now log in and start managing your credit data.</p>
                <p>Best regards,<br/>CreditDataWatch Team</p>
            </div>
        </body>
        </html>
        """
        
        try:
            return EmailService.send_email(
                to_email=email,
                subject=subject,
                html_body=html_body
            )
        except EmailServiceError as e:
            logger.error(f"Failed to send registration email to {email}: {str(e)}")
            return False


# Example usage for sending OTP email
if __name__ == "__main__":
    """
    Example: Send an OTP email
    
    Make sure to set environment variables:
    export GOOGLE_SMTP_USER="your-email@gmail.com"
    export GOOGLE_SMTP_PASSWORD="your-app-password"
    
    Or create a .env file with:
    GOOGLE_SMTP_USER=your-email@gmail.com
    GOOGLE_SMTP_PASSWORD=your-app-password
    """
    
    import asyncio
    
    async def example_send_otp():
        """Example: Send OTP email"""
        recipient = "recipient@example.com"
        otp_code = "123456"
        
        success = await EmailService.send_otp_email(
            to_email=recipient,
            otp_code=otp_code,
            reason="account verification",
            expiry_minutes=10
        )
        
        if success:
            print(f"✓ OTP email sent successfully to {recipient}")
        else:
            print(f"✗ Failed to send OTP email to {recipient}")
    
    # Uncomment to test:
    # asyncio.run(example_send_otp())
