"""
Environment configuration and settings
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/creditdatawatch"

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Cookie settings
    COOKIE_DOMAIN: str = "localhost"
    COOKIE_PATH: str = "/"
    COOKIE_SECURE: bool = False  # Set to True in production with HTTPS
    COOKIE_HTTPONLY: bool = True
    COOKIE_SAMESITE: str = "lax"

    # Google SMTP (Email)
    GOOGLE_SMTP_HOST: str = "smtp.gmail.com"
    GOOGLE_SMTP_PORT: int = 587
    GOOGLE_SMTP_USER: str = ""
    GOOGLE_SMTP_PASSWORD: str = ""
    SENDER_EMAIL: str = ""

    # Google Drive OAuth2
    GOOGLE_CLIENT_CREDENTIALS_FILE: str = "server/credentials/client-credentials.json"
    GOOGLE_SERVICE_ACCOUNT_FILE: str = "server/credentials/service-account.json"
    GOOGLE_FOLDER_ID: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/drive/callback"

    # OTP (Twilio - optional, can use stub)
    OTP_PROVIDER: str = "smtp"  # or "twilio" or "mock"
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    OTP_EXPIRY_MINUTES: int = 10

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost:3001", "http://localhost:3002"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    # Logging
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"

    # Admin Configuration (for seeding initial admin user)
    ADMIN_GSTIN: str = ""
    ADMIN_EMAIL: str = ""
    ADMIN_PASSWORD: str = ""
    ADMIN_COMPANY_NAME: str = ""
    ADMIN_PHONE: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
