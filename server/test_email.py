from app.services.email_service import EmailService

email_service = EmailService()

email_service.send_email(
    to_email="shindepayal296@gmail.com",
    subject="SMTP Test – CreditDataWatch",
    body="If you received this email, SMTP is working 🎉"
)
