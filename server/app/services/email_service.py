import logging
import smtplib
from email.message import EmailMessage

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_host = settings.GOOGLE_SMTP_HOST
        self.smtp_port = settings.GOOGLE_SMTP_PORT
        self.smtp_user = settings.GOOGLE_SMTP_USER
        self.smtp_password = settings.GOOGLE_SMTP_PASSWORD
        self.sender_email = (
            settings.SENDER_EMAIL if settings.SENDER_EMAIL else settings.GOOGLE_SMTP_USER
        )
        self.timeout = settings.SMTP_TIMEOUT

    def send_email(self, to_email: str, subject: str, body: str):
        """Send a normal email"""
        if not self.smtp_user or not self.smtp_password:
            logging.warning("SMTP not configured, skipping email.")
            return

        try:
            from email.message import EmailMessage
            msg = EmailMessage()
            msg["From"] = self.sender_email
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.set_content(body)

            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=self.timeout) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logging.info(f"Email sent to {to_email}")
        except Exception as e:
            logging.error(f"Email failed: {e}")

    @staticmethod
    async def send_registration_email(to_email: str, company_name: str, phone: str) -> None:
        """Send welcome email after registration. Does not raise; logs on failure."""
        try:
            subject = "Welcome to CreditDataWatch"
            body = (
                f"Hello,\n\n"
                f"Thank you for registering with CreditDataWatch.\n\n"
                f"Company: {company_name}\n"
                f"Phone: {phone}\n\n"
                f"You can now log in and use the platform.\n\n"
                f"Thank you!"
            )
            svc = EmailService()
            svc.send_email(to_email, subject, body)
        except Exception as e:
            logger.warning("Registration email failed (registration still succeeds): %s", e)
