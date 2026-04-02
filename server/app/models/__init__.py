"""
SQLAlchemy ORM Models
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, Index, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
import uuid

from app.database import Base


# Enums for membership and payment system
class MembershipStatus(str, enum.Enum):
    """Membership subscription status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    """Payment transaction status"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PaymentMethod(str, enum.Enum):
    """Payment methods supported"""
    UPI = "upi"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    NET_BANKING = "net_banking"
    QR_CODE = "qr_code"


class DurationType(str, enum.Enum):
    """Plan duration types"""
    MONTHLY = "monthly"
    YEARLY = "yearly"

CASCADE_DELETE_ORPHAN = "all, delete-orphan"
USER_ID_FK = "users.id"
ONDELETE_CASCADE = "CASCADE"


class Company(Base):
    """Company entity"""

    __tablename__ = "companies"

    id = Column(String(36), primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    gstin = Column(String(15), unique=True, nullable=False, index=True)
    domain_name = Column(String(255), nullable=False, index=True)
    is_verified = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="company", cascade=CASCADE_DELETE_ORPHAN)
    purchase_orders = relationship("PurchaseOrder", back_populates="company", cascade=CASCADE_DELETE_ORPHAN)


class User(Base):
    """User account model (belongs to Company)"""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete=ONDELETE_CASCADE), nullable=True, index=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), default="USER", index=True)  # ADMIN, FINANCE, LEGAL, OPERATIONS, USER
    status = Column(String(20), default="ACTIVE", index=True)  # PENDING, ACTIVE
    phone = Column(String(20), nullable=True, index=True)
    gstin = Column(String(15), nullable=False, index=True)
    company_name = Column(String(255), nullable=True)  # Deprecated display; prefer Company.company_name
    is_active = Column(Boolean, default=True, index=True)
    subscription_bypass = Column(Boolean, default=False, nullable=False, index=True)
    full_access = Column(Boolean, default=False, nullable=False, index=True)
    subscription_status = Column(String(20), default="INACTIVE", nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="users")
    subscription = relationship("Subscription", back_populates="user", uselist=False, cascade=CASCADE_DELETE_ORPHAN)
    payments = relationship("Payment", back_populates="user", cascade=CASCADE_DELETE_ORPHAN)
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade=CASCADE_DELETE_ORPHAN)
    business_profiles = relationship("BusinessProfile", back_populates="user", cascade=CASCADE_DELETE_ORPHAN)
    purchase_orders = relationship("PurchaseOrder", back_populates="user", cascade=CASCADE_DELETE_ORPHAN)
    invoices = relationship("Invoice", back_populates="user", cascade=CASCADE_DELETE_ORPHAN)
    defaulter_cases = relationship("DefaulterCase", back_populates="user", cascade=CASCADE_DELETE_ORPHAN)
    credit_reports = relationship("CreditReport", back_populates="user", cascade=CASCADE_DELETE_ORPHAN)
    settlements = relationship("Settlement", back_populates="user", cascade=CASCADE_DELETE_ORPHAN)
    appointments = relationship("Appointment", back_populates="user", cascade=CASCADE_DELETE_ORPHAN)
    wallet = relationship("Wallet", back_populates="user", uselist=False, cascade=CASCADE_DELETE_ORPHAN)

    __table_args__ = (
        Index("idx_user_email_active", "email", "is_active"),
        Index("idx_user_role", "role"),
        Index("idx_user_company", "company_id", "status"),
    )


class Subscription(Base):
    """Subscription/plan model"""

    __tablename__ = "subscriptions"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey(USER_ID_FK, ondelete=ONDELETE_CASCADE), nullable=False, index=True)
    plan_id = Column(String(36), ForeignKey("plans.id"), nullable=False, index=True)
    status = Column(Enum(MembershipStatus), default=MembershipStatus.ACTIVE, nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    start_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    expiry_date = Column(DateTime, nullable=True, index=True)
    payment_id = Column(String(36), ForeignKey("payments.id"), nullable=True, index=True)  # Link to successful payment
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="subscription")
    plan = relationship("Plan", back_populates="subscriptions")
    payment = relationship("Payment", back_populates="subscription", foreign_keys=[payment_id])

    __table_args__ = (
        Index("idx_subscription_user_active", "user_id", "is_active"),
        Index("idx_subscription_status", "status"),
    )


class Plan(Base):
    """Membership plan model (admin-configurable)"""

    __tablename__ = "plans"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)  # basic, pro, premium
    display_name = Column(String(100), nullable=False)  # "Basic", "Pro", "Premium"
    description = Column(Text, nullable=True)
    duration_type = Column(Enum(DurationType), default=DurationType.MONTHLY, nullable=False, index=True)  # monthly, yearly
    price = Column(Float, nullable=False, default=0)  # in INR
    validity_days = Column(Integer, nullable=False, default=30)  # Calculated from duration_type
    follow_up_limit = Column(Integer, nullable=False, default=10)  # max follow-ups per case
    legal_assistance_limit = Column(Integer, nullable=False, default=2)  # max legal escalations per case
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan", cascade=CASCADE_DELETE_ORPHAN)

    __table_args__ = (
        Index("idx_plan_active", "is_active"),
        Index("idx_plan_duration", "duration_type", "is_active"),
    )


class BusinessProfile(Base):
    """Business profile for multi-unit companies"""

    __tablename__ = "business_profiles"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey(USER_ID_FK, ondelete=ONDELETE_CASCADE), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    registered_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    gstin = Column(String(15), nullable=False, index=True)
    profile_photo_url = Column(String(512), nullable=True)  # Google Drive URL
    company_logo_url = Column(String(512), nullable=True)   # Google Drive URL
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="business_profiles")


class PurchaseOrder(Base):
    """Purchase order model"""

    __tablename__ = "purchase_orders"

    id = Column(String(36), primary_key=True, index=True)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete=ONDELETE_CASCADE), nullable=True, index=True)
    user_id = Column(String(36), ForeignKey(USER_ID_FK, ondelete=ONDELETE_CASCADE), nullable=False, index=True)
    po_number = Column(String(100), nullable=False)
    vendor = Column(String(255), nullable=False)
    gstin = Column(String(15), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    due_date = Column(DateTime, nullable=False, index=True)
    status = Column(String(50), default="Open", index=True)  # Open, Pending Docs, Closed
    archived = Column(Boolean, default=False, index=True)
    document_url = Column(String(500), nullable=True)  # Google Drive URL
    notes = Column(Text, nullable=True)
    supplier_address = Column(Text, nullable=True)
    delivery_address = Column(Text, nullable=True)
    invoice_address = Column(Text, nullable=True)
    payment_completed_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    vendor_email = Column(String, nullable=True)
    vendor_phone = Column(String, nullable=True)
    legal_notice_sent_at = Column(DateTime, nullable=True)
    payment_window_days = Column(Integer, default=50)

    # Relationships
    user = relationship("User", back_populates="purchase_orders")
    company = relationship("Company", back_populates="purchase_orders", foreign_keys=[company_id])

    __table_args__ = (
        Index("idx_po_company_status", "company_id", "status"),
        Index("idx_po_gstin", "gstin"),
        Index("idx_po_payment", "payment_completed_at"),
    )

class CompanyCredibilityIndex(Base):
    __tablename__ = "company_credibility_index"
    id = Column(String(36), primary_key=True, index=True)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete=ONDELETE_CASCADE), nullable=False, unique=True, index=True)
    score = Column(Integer, nullable=False, default=0, index=True)
    grade = Column(String(10), nullable=False, default="D", index=True)
    risk_level = Column(String(20), nullable=False, default="High", index=True)
    ai_summary = Column(Text, nullable=True)
    calculation_window_days = Column(Integer, nullable=False, default=90)
    total_pos = Column(Integer, nullable=False, default=0)
    paid_on_time = Column(Integer, nullable=False, default=0)
    paid_late = Column(Integer, nullable=False, default=0)
    unpaid = Column(Integer, nullable=False, default=0)
    avg_delay_days = Column(Float, nullable=False, default=0.0)
    max_delay_days = Column(Integer, nullable=False, default=0)
    overdue_count = Column(Integer, nullable=False, default=0)
    last_calculated_at = Column(DateTime, nullable=True, index=True)


class CredibilityConfig(Base):
    __tablename__ = "credibility_config"
    id = Column(String(36), primary_key=True, index=True)
    calculation_window_days = Column(Integer, nullable=False, default=90)
    last_updated_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PurchaseOrderAuditLog(Base):
    __tablename__ = "purchase_order_audit_logs"
    id = Column(String(36), primary_key=True, index=True)
    purchase_order_id = Column(String(36), ForeignKey("purchase_orders.id", ondelete=ONDELETE_CASCADE), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)  # e.g., MARK_PAID
    performed_by_user_id = Column(String(36), ForeignKey(USER_ID_FK, ondelete=ONDELETE_CASCADE), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    details = Column(JSON, nullable=True)

# Re-export Notification for `from app.models import Notification`
from app.models.notification import Notification


class Invoice(Base):
    """Receivables invoice for credit management"""

    __tablename__ = "invoices"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey(USER_ID_FK, ondelete=ONDELETE_CASCADE), nullable=False, index=True)
    counterparty_name = Column(String(255), nullable=False)
    counterparty_gstin = Column(String(15), nullable=True, index=True)
    counterparty_pan = Column(String(10), nullable=True, index=True)
    invoice_number = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    due_date = Column(DateTime, nullable=False, index=True)
    status = Column(String(50), default="open", index=True)  # open, acknowledged, partially_paid, paid, overdue, canceled
    acknowledged_at = Column(DateTime, nullable=True)
    reminder_frequency_days = Column(Integer, default=7)
    reminder_next_at = Column(DateTime, nullable=True)
    last_follow_up_at = Column(DateTime, nullable=True)
    follow_up_history = Column(JSON, default=list)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="invoices")

    __table_args__ = (
        Index("idx_invoice_user_status", "user_id", "status"),
        Index("idx_invoice_counterparty", "counterparty_gstin", "counterparty_pan"),
    )


class DefaulterCase(Base):
    """Defaulter reporting case"""

    __tablename__ = "defaulter_cases"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey(USER_ID_FK, ondelete=ONDELETE_CASCADE), nullable=False, index=True)
    business_name = Column(String(255), nullable=False)
    business_gstin = Column(String(15), nullable=True, index=True)  # GSTIN optional, PAN fallback allowed
    pan = Column(String(10), nullable=True, index=True)  # PAN as fallback
    invoice_number = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    due_date = Column(DateTime, nullable=False, index=True)
    approval_status = Column(String(50), default="pending", index=True)  # pending, approved, rejected
    verified_by = Column(String(36), nullable=True)  # Admin user ID who verified
    verification_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    documents_drive_folder = Column(String(500), nullable=True)  # Google Drive folder ID
    ledger_url = Column(String(500), nullable=True)
    ca_certificate_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="defaulter_cases")

    __table_args__ = (
        Index("idx_defaulter_user_status", "user_id", "approval_status"),
        Index("idx_defaulter_business_gstin", "business_gstin"),
        Index("idx_defaulter_approval_date", "approval_status", "created_at"),
    )


class CreditReport(Base):
    """Credit report request and data"""

    __tablename__ = "credit_reports"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey(USER_ID_FK, ondelete=ONDELETE_CASCADE), nullable=False, index=True)
    entity_name = Column(String(255), nullable=False)
    entity_gstin = Column(String(15), nullable=False, index=True)
    credit_score = Column(Integer, nullable=True)
    status = Column(String(50), default="Requested", index=True)  # Requested, Ready, Pending refresh
    report_url = Column(String(500), nullable=True)  # Google Drive link
    last_updated = Column(DateTime, nullable=True)
    requested_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="credit_reports")

    __table_args__ = (
        Index("idx_credit_user_status", "user_id", "status"),
        Index("idx_credit_entity_gstin", "entity_gstin"),
    )


class Settlement(Base):
    """Settlement/finalization record"""

    __tablename__ = "settlements"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey(USER_ID_FK, ondelete=ONDELETE_CASCADE), nullable=False, index=True)
    case_reference = Column(String(255), nullable=False)  # Reference to defaulter case or PO
    status = Column(String(50), default="Open", index=True)
    notes = Column(Text, nullable=True)
    documents_drive_folder = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="settlements")

    __table_args__ = (
        Index("idx_settlement_user_status", "user_id", "status"),
    )


class Appointment(Base):
    """Appointment booking model"""

    __tablename__ = "appointments"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey(USER_ID_FK, ondelete=ONDELETE_CASCADE), nullable=False, index=True)
    contact_name = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(20), nullable=False)
    appointment_date = Column(DateTime, nullable=False, index=True)
    purpose = Column(String(500), nullable=False)
    status = Column(String(50), default="scheduled", index=True)  # scheduled, confirmed, completed, cancelled
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="appointments")

    __table_args__ = (
        Index("idx_appointment_user_status", "user_id", "status"),
        Index("idx_appointment_date", "appointment_date"),
    )


class Wallet(Base):
    """User wallet for points/credits"""

    __tablename__ = "wallets"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey(USER_ID_FK, ondelete=ONDELETE_CASCADE), nullable=False, unique=True, index=True)
    balance = Column(Float, default=0.0, nullable=False)
    currency = Column(String(20), default="INR_POINTS")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="wallet")
    transactions = relationship("WalletTransaction", back_populates="wallet", cascade=CASCADE_DELETE_ORPHAN)


class WalletTransaction(Base):
    """History of wallet credits/debits"""

    __tablename__ = "wallet_transactions"

    id = Column(String(36), primary_key=True, index=True)
    wallet_id = Column(String(36), ForeignKey("wallets.id", ondelete=ONDELETE_CASCADE), nullable=False, index=True)
    amount = Column(Float, nullable=False)  # Positive for credit, negative for debit (visual only, implementation stores abs usually but let's stick to signed or explicit type)
    # Sticking to: Amount is absolute, Type determines sign logic.
    trans_type = Column(String(20), nullable=False) # CREDIT, DEBIT
    reference_type = Column(String(50), nullable=False) # SUBSCRIPTION, REFERRAL, etc.
    reference_id = Column(String(36), nullable=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    wallet = relationship("Wallet", back_populates="transactions")

    __table_args__ = (
        Index("idx_wallet_trans_wallet_date", "wallet_id", "created_at"),
    )



class CMSPage(Base):
    """CMS Page model for dynamic content pages"""

    __tablename__ = "cms_pages"

    id = Column(String(36), primary_key=True, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    is_published = Column(Boolean, default=False, index=True)
    seo_title = Column(String(255), nullable=True)
    seo_description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sections = relationship("CMSSection", back_populates="page", cascade=CASCADE_DELETE_ORPHAN, order_by="CMSSection.order_index")


class CMSSection(Base):
    """CMS Section model for page blocks"""

    __tablename__ = "cms_sections"

    id = Column(String(36), primary_key=True, index=True)
    page_id = Column(String(36), ForeignKey("cms_pages.id", ondelete=ONDELETE_CASCADE), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # hero, stats, scam_alert, etc.
    order_index = Column(Integer, nullable=False, default=0)
    is_visible = Column(Boolean, default=True)
    content = Column(JSON, default=dict)  # Flexible JSON payload
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    page = relationship("CMSPage", back_populates="sections")

    __table_args__ = (
        Index("idx_cms_section_page_order", "page_id", "order_index"),
    )


class Payment(Base):
    """Payment transaction model"""

    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey(USER_ID_FK, ondelete=ONDELETE_CASCADE), nullable=False, index=True)
    plan_id = Column(String(36), ForeignKey("plans.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)  # in INR
    currency = Column(String(10), default="INR", nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False, index=True)
    payment_provider = Column(String(50), nullable=True)  # "razorpay", "payu", "stripe", etc.
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False, index=True)
    transaction_id = Column(String(255), unique=True, nullable=True, index=True)  # Gateway transaction ID
    reference_id = Column(String(255), unique=True, nullable=False, index=True)  # Internal reference
    gateway_order_id = Column(String(255), nullable=True)  # Payment gateway order ID
    gateway_payment_id = Column(String(255), nullable=True)  # Payment ID from gateway
    failure_reason = Column(Text, nullable=True)  # If failed
    payment_metadata = Column(JSON, default=dict)  # Additional payment data (card last 4 digits, UPI ID, etc.)
    initiated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="payments")
    plan = relationship("Plan")
    subscription = relationship("Subscription", back_populates="payment", uselist=False)

    __table_args__ = (
        Index("idx_payment_user_status", "user_id", "status"),
        Index("idx_payment_status_created", "status", "created_at"),
    )


class UserSettings(Base):
    """User settings and preferences model"""

    __tablename__ = "user_settings"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey(USER_ID_FK, ondelete=ONDELETE_CASCADE), nullable=False, unique=True, index=True)
    theme_preference = Column(String(20), default="system", nullable=False)  # "light", "dark", "system"
    language = Column(String(10), default="en", nullable=False)
    notifications_enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="settings")

    __table_args__ = (
        Index("idx_user_settings_user", "user_id"),
    )


class Invitation(Base):
    """Employee invitation to join Company"""

    __tablename__ = "invitations"

    id = Column(String(36), primary_key=True, index=True)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete=ONDELETE_CASCADE), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    role = Column(String(30), nullable=False)  # ADMIN, FINANCE, LEGAL, OPERATIONS
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    status = Column(String(20), default="PENDING", index=True)  # PENDING, ACCEPTED
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    company = relationship("Company")

class POReminderConfig(Base):
    __tablename__ = "po_reminder_configs"
    id = Column(String(36), primary_key=True, index=True)
    before_days = Column(JSON, nullable=True)
    after_due_daily_enabled = Column(Boolean, default=False)
    reminder_subject = Column(String(255), nullable=True, default="Payment Reminder: PO {po_number} - {vendor_name}")
    reminder_body = Column(Text, nullable=True, default="Dear {vendor_name},\n\nThis is a reminder that PO {po_number} for the amount of ₹{amount} is due on {due_date}.\n\nPlease ensure payment is processed on time.\n\nRegards,\nTeam CreditWatch")

class ScheduledReminder(Base):
    __tablename__ = "scheduled_reminders"
    id = Column(String(36), primary_key=True, index=True)
    purchase_order_id = Column(String(36), ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    scheduled_at = Column(DateTime, nullable=False, index=True)
    sent_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class SOPDocument(Base): 
    __tablename__ = "sop_documents" 
    id = Column( 
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4()) 
    ) 
    filename = Column(String, nullable=False) 
    content = Column(Text, nullable=False) 
    uploaded_at = Column( 
        DateTime, 
        default=datetime.utcnow 
    ) 
    uploaded_by = Column( 
        String(36), 
        nullable=True 
    ) 

class AppSettings(Base):
    __tablename__ = "app_settings"
    id = Column(String(36), primary_key=True, index=True)
    payment_window_days = Column(Integer, nullable=False, default=50)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

