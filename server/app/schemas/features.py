"""
Pydantic schemas for features (PO, defaulter, credit report, settlement)
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class PurchaseOrderRequest(BaseModel):
    """Create/update purchase order"""

    number: str = Field(..., min_length=1, max_length=100)
    vendor_name: str = Field(..., min_length=2, max_length=255)
    vendor_gstin: str = Field(..., min_length=15, max_length=15)
    amount: float = Field(..., gt=0)
    due_date: datetime
    status: Optional[str] = "Open"
    notes: Optional[str] = None


class PurchaseOrderResponse(BaseModel):
    """Purchase order response"""

    id: str
    number: str
    vendor_name: str
    vendor_gstin: str
    amount: float
    due_date: datetime
    status: str
    document_url: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DefaulterCaseRequest(BaseModel):
    """Create defaulter case"""

    business_name: str = Field(..., min_length=2, max_length=255)
    business_gstin: str = Field(..., min_length=15, max_length=15)
    invoice_number: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0)
    due_date: datetime
    notes: Optional[str] = None


class DefaulterCaseResponse(BaseModel):
    """Defaulter case response"""

    id: str
    business_name: str
    business_gstin: str
    invoice_number: str
    amount: float
    due_date: datetime
    status: str
    notes: Optional[str]
    documents_drive_folder: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreditReportRequest(BaseModel):
    """Request credit report"""

    entity_name: str = Field(..., min_length=2, max_length=255)
    entity_gstin: str = Field(..., min_length=15, max_length=15)


class CreditReportResponse(BaseModel):
    """Credit report response"""

    id: str
    entity_name: str
    entity_gstin: str
    credit_score: Optional[int]
    status: str
    report_url: Optional[str]
    last_updated: Optional[datetime]
    requested_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SettlementRequest(BaseModel):
    """Create settlement record"""

    case_reference: str = Field(..., min_length=1, max_length=255)
    notes: Optional[str] = None


class SettlementResponse(BaseModel):
    """Settlement response"""

    id: str
    case_reference: str
    status: str
    notes: Optional[str]
    documents_drive_folder: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Invoice schemas
class InvoiceCreate(BaseModel):
    """Create invoice"""

    counterparty_name: str = Field(..., min_length=2, max_length=255)
    counterparty_gstin: Optional[str] = Field(None, min_length=15, max_length=15)
    counterparty_pan: Optional[str] = Field(None, min_length=10, max_length=10)
    invoice_number: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0)
    due_date: datetime
    status: Optional[str] = "pending"
    reminder_frequency_days: Optional[int] = Field(7, ge=1, le=365)
    notes: Optional[str] = None


class InvoiceUpdate(BaseModel):
    """Update invoice"""

    counterparty_name: Optional[str] = Field(None, min_length=2, max_length=255)
    counterparty_gstin: Optional[str] = Field(None, min_length=15, max_length=15)
    counterparty_pan: Optional[str] = Field(None, min_length=10, max_length=10)
    invoice_number: Optional[str] = Field(None, min_length=1, max_length=100)
    amount: Optional[float] = Field(None, gt=0)
    due_date: Optional[datetime] = None
    status: Optional[str] = None
    reminder_frequency_days: Optional[int] = Field(None, ge=1, le=365)
    notes: Optional[str] = None


class InvoiceResponse(BaseModel):
    """Invoice response"""

    id: UUID
    user_id: UUID
    counterparty_name: str
    counterparty_gstin: Optional[str]
    counterparty_pan: Optional[str]
    invoice_number: str
    amount: float
    due_date: datetime
    status: str
    acknowledged_at: Optional[datetime]
    reminder_frequency_days: int
    reminder_next_at: Optional[datetime]
    last_follow_up_at: Optional[datetime]
    follow_up_history: List[Dict[str, Any]]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    """List of invoices"""

    invoices: List[InvoiceResponse]
    total: int
    skip: int
    limit: int


class InvoiceFollowUpNote(BaseModel):
    """Add follow-up note to invoice"""

    note: str = Field(..., min_length=1, max_length=2000)

