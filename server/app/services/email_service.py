"""
Email service using Google SMTP
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Send emails via Google SMTP"""

    @staticmethod
    async def send_registration_email(email: str, company_name: str, phone: str) -> bool:
        """
        Send registration confirmation email
        
        Args:
            email: Recipient email
            company_name: Company name
            phone: Phone number
            
        Returns:
            True if sent successfully
        """
        try:
            subject = "Welcome to CreditDataWatch"
            body = f"""
            <html>
                <body>
                    <h2>Welcome to CreditDataWatch!</h2>
                    <p>Hi {company_name},</p>
                    <p>Your account has been successfully created.</p>
                    <p><strong>Account Details:</strong></p>
                    <ul>
                        <li>Email: {email}</li>
                        <li>Phone: {phone}</li>
                    </ul>
                    <p>You can now log in and start managing your credit data.</p>
                    <p>Best regards,<br/>CreditDataWatch Team</p>
                </body>
            </html>
            """
            
            await EmailService._send_smtp(email, subject, body)
            logger.info(f"Registration email sent to {email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send registration email to {email}: {str(e)}")
            return False

    @staticmethod
    async def send_otp_email(email: str, otp_code: str, reason: str = "phone verification") -> bool:
        """
        Send OTP via email
        
        Args:
            email: Recipient email
            otp_code: OTP code
            reason: Reason for OTP
            
        Returns:
            True if sent successfully
        """
        try:
            subject = f"Your OTP for {reason}"
            body = f"""
            <html>
                <body>
                    <h2>OTP Verification</h2>
                    <p>Your OTP code is:</p>
                    <h3 style="color: #007bff; font-family: monospace;">{otp_code}</h3>
                    <p>This code will expire in 10 minutes.</p>
                    <p>Do not share this code with anyone.</p>
                </body>
            </html>
            """
            
            await EmailService._send_smtp(email, subject, body)
            logger.info(f"OTP email sent to {email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send OTP email to {email}: {str(e)}")
            return False

    @staticmethod
    async def _send_smtp(to_email: str, subject: str, html_body: str) -> bool:
        """
        Send email via Google SMTP
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_body: Email body (HTML)
            
        Returns:
            True if successful
        """
        if settings.ENVIRONMENT == "development":
            # In development, just log
            logger.info(f"[DEV] Email to {to_email}: {subject}")
            logger.info(f"[DEV] Body: {html_body}")
            return True
        
        # In production, send via SMTP
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.SENDER_EMAIL
            msg["To"] = to_email
            
            # Attach HTML body
            msg.attach(MIMEText(html_body, "html"))
            
            # Connect to Google SMTP
            with smtplib.SMTP(settings.GOOGLE_SMTP_HOST, settings.GOOGLE_SMTP_PORT) as server:
                server.starttls()
                server.login(settings.GOOGLE_SMTP_USER, settings.GOOGLE_SMTP_PASSWORD)
                server.send_message(msg)
            
            return True
        except Exception as e:
            logger.error(f"SMTP error: {str(e)}")
            return False
