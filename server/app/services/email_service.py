import logging
import smtplib
from email.message import EmailMessage
from email.utils import formataddr, parseaddr

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_host = settings.GOOGLE_SMTP_HOST
        self.smtp_port = settings.GOOGLE_SMTP_PORT
        self.smtp_user = settings.GOOGLE_SMTP_USER
        self.smtp_password = settings.GOOGLE_SMTP_PASSWORD
        self.sender_email = settings.SENDER_EMAIL or settings.GOOGLE_SMTP_USER
        self.sender_name = getattr(settings, "SENDER_NAME", "CreditDataWatch")
        # Build a unified, explicit From header
        # Always normalize to enforce consistent display name
        _, addr_only = parseaddr(self.sender_email or "")
        base_addr = addr_only or self.sender_email
        self.from_header = formataddr((self.sender_name, base_addr))
        self.timeout = settings.SMTP_TIMEOUT

    def send_email(self, to_email: str, subject: str, body: str):
        """Send a normal email"""
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP not configured, skipping email.")
            return

        try:
            import smtplib, ssl
            from email.message import EmailMessage
            msg = EmailMessage()
            msg["From"] = self.from_header
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.set_content(body)
            logger.info(f"Sending email | From: {msg['From']} To: {to_email} Subject: {subject}")

            context = ssl.create_default_context()
            # Force port 465 for SMTP_SSL as per requirement
            with smtplib.SMTP_SSL(self.smtp_host, 465, context=context) as server:
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent to {to_email}")
        except Exception as e:
            logger.error(f"Email FAILED: {str(e)}")
            raise e

    def send_email_html(self, to_email: str, subject: str, html: str, text_fallback: str | None = None):
        """Send an HTML email with optional text fallback"""
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP not configured, skipping email.")
            return
        try:
            import smtplib, ssl
            from email.message import EmailMessage
            msg = EmailMessage()
            msg["From"] = self.from_header
            msg["To"] = to_email
            msg["Subject"] = subject
            if text_fallback:
                msg.set_content(text_fallback)
            else:
                msg.set_content("HTML email")
            msg.add_alternative(html, subtype="html")
            logger.info(f"Sending email | From: {msg['From']} To: {to_email} Subject: {subject}")

            context = ssl.create_default_context()
            # Force port 465 for SMTP_SSL as per requirement
            with smtplib.SMTP_SSL(self.smtp_host, 465, context=context) as server:
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"HTML email sent to {to_email}")
        except Exception as e:
            logger.error(f"Email FAILED: {str(e)}")
            raise e

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

    @staticmethod
    async def send_invitation_email(to_email: str, company_name: str, role: str, token: str, expires_at: str) -> None:
        """Send invitation email with acceptance link. Does not raise; logs on failure."""
        try:
            frontend_base = getattr(settings, "FRONTEND_URL", "") or "http://localhost:3000"
            invite_link = f"{frontend_base.rstrip('/')}/accept-invite?token={token}"
            subject = f"You're invited to join {company_name}"
            text_fallback = (
                f"You're invited to join {company_name}\n"
                f"Role: {role}\n"
                f"Expires At: {expires_at}\n\n"
                f"Accept Invitation: {invite_link}\n"
                f"If you did not expect this email, please ignore it."
            )
            html = f"""
              <h2>You're Invited!</h2>
              <p>You have been invited to join <b>{company_name}</b>.</p>
              <p><b>Role:</b> {role}</p>
              <p><b>Expires At:</b> {expires_at}</p>
              <br/>
              <a href="{invite_link}"
                 style="padding:10px 16px;background:#2563eb;color:white;text-decoration:none;border-radius:6px;">
                 Accept Invitation
              </a>
              <br/><br/>
              <p>If you did not expect this email, please ignore it.</p>
            """
            svc = EmailService()
            svc.send_email_html(to_email, subject, html, text_fallback=text_fallback)
        except Exception as e:
            logger.warning("Invitation email failed (invitation still valid): %s", e)
