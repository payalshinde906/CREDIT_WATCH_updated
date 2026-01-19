"""
SQLAlchemy ORM Models
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, Index, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

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


class User(Base):
    """User account model"""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)
    gstin = Column(String(15), unique=True, nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    role = Column(String(20), default="user", index=True)  # user, admin
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
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
        Index("idx_user_gstin_active", "gstin", "is_active"),
        Index("idx_user_email_active", "email", "is_active"),
        Index("idx_user_role", "role"),
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
    user_id = Column(String(36), ForeignKey(USER_ID_FK, ondelete=ONDELETE_CASCADE), nullable=False, index=True)
    number = Column(String(100), nullable=False)
    vendor_name = Column(String(255), nullable=False)
    vendor_gstin = Column(String(15), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    due_date = Column(DateTime, nullable=False, index=True)
    status = Column(String(50), default="Open", index=True)  # Open, Pending Docs, Closed
    is_archived = Column(Boolean, default=False, index=True)
    document_url = Column(String(500), nullable=True)  # Google Drive URL
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="purchase_orders")

    __table_args__ = (
        Index("idx_po_user_status", "user_id", "status"),
        Index("idx_po_vendor_gstin", "vendor_gstin"),
    )


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
