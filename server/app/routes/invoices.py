from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Invoice, User
from app.schemas.features import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    InvoiceListResponse,
    InvoiceFollowUpNote,
)
from app.utils.response import ResponseFormatter

# Constants
INVOICE_NOT_FOUND_ERROR = "Invoice not found"

# Helper function
def get_utc_now():
    """Get current UTC time"""
    return datetime.utcnow()

router = APIRouter(prefix="/invoices", tags=["Invoices"])

# Helper function for success responses
def success_response(data=None, message="Success"):
    return ResponseFormatter.create_success(data=data, message=message)


@router.get("")
async def list_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    counterparty_gstin: Optional[str] = None,
    counterparty_pan: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List invoices with optional filtering"""
    query = select(Invoice).where(Invoice.user_id == current_user.id)

    if status:
        query = query.where(Invoice.status == status)
    if counterparty_gstin:
        query = query.where(Invoice.counterparty_gstin == counterparty_gstin)
    if counterparty_pan:
        query = query.where(Invoice.counterparty_pan == counterparty_pan)
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Invoice.counterparty_name.ilike(search_term),
                Invoice.invoice_number.ilike(search_term),
                Invoice.notes.ilike(search_term),
            )
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar_one()

    # Get paginated results
    query = query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    invoices = result.scalars().all()

    return success_response(
        data={"invoices": invoices, "total": total, "skip": skip, "limit": limit}
    )


@router.post("", status_code=201)
async def create_invoice(
    invoice_data: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new invoice"""
    from uuid import uuid4
    
    # Validate at least one identifier
    if not invoice_data.counterparty_gstin and not invoice_data.counterparty_pan:
        raise HTTPException(
            status_code=400,
            detail="Either counterparty_gstin or counterparty_pan must be provided",
        )

    invoice = Invoice(
        id=str(uuid4()),
        user_id=current_user.id,
        counterparty_name=invoice_data.counterparty_name,
        counterparty_gstin=invoice_data.counterparty_gstin,
        counterparty_pan=invoice_data.counterparty_pan,
        invoice_number=invoice_data.invoice_number,
        amount=invoice_data.amount,
        due_date=invoice_data.due_date,
        status=invoice_data.status or "pending",
        reminder_frequency_days=invoice_data.reminder_frequency_days or 7,
        notes=invoice_data.notes,
        follow_up_history=[],
    )

    # Set initial reminder date if not acknowledged
    if invoice.status != "acknowledged":
        invoice.reminder_next_at = get_utc_now() + timedelta(
            days=invoice.reminder_frequency_days
        )

    db.add(invoice)
    await db.commit()
    await db.refresh(invoice)

    return success_response(data=invoice)


@router.get("/{invoice_id}")
async def get_invoice(
    invoice_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific invoice"""
    result = await db.execute(
        select(Invoice).where(
            and_(Invoice.id == invoice_id, Invoice.user_id == current_user.id)
        )
    )
    invoice = result.scalar_one_or_none()

    if not invoice:
        raise HTTPException(status_code=404, detail=INVOICE_NOT_FOUND_ERROR)

    return success_response(data=invoice)


@router.put("/{invoice_id}")
async def update_invoice(
    invoice_id: UUID,
    invoice_data: InvoiceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an invoice"""
    result = await db.execute(
        select(Invoice).where(
            and_(Invoice.id == invoice_id, Invoice.user_id == current_user.id)
        )
    )
    invoice = result.scalar_one_or_none()

    if not invoice:
        raise HTTPException(status_code=404, detail=INVOICE_NOT_FOUND_ERROR)

    # Update fields
    update_data = invoice_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(invoice, field, value)

    # Update reminder schedule if frequency changed
    if "reminder_frequency_days" in update_data and invoice.status != "acknowledged":
        invoice.reminder_next_at = get_utc_now() + timedelta(
            days=invoice.reminder_frequency_days
        )

    invoice.updated_at = get_utc_now()
    await db.commit()
    await db.refresh(invoice)

    return success_response(data=invoice)


@router.delete("/{invoice_id}", status_code=204)
async def delete_invoice(
    invoice_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an invoice"""
    result = await db.execute(
        select(Invoice).where(
            and_(Invoice.id == invoice_id, Invoice.user_id == current_user.id)
        )
    )
    invoice = result.scalar_one_or_none()

    if not invoice:
        raise HTTPException(status_code=404, detail=INVOICE_NOT_FOUND_ERROR)

    await db.delete(invoice)
    await db.commit()


@router.post("/{invoice_id}/acknowledge")
async def toggle_acknowledgment(
    invoice_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Toggle invoice acknowledgment status"""
    result = await db.execute(
        select(Invoice).where(
            and_(Invoice.id == invoice_id, Invoice.user_id == current_user.id)
        )
    )
    invoice = result.scalar_one_or_none()

    if not invoice:
        raise HTTPException(status_code=404, detail=INVOICE_NOT_FOUND_ERROR)

    if invoice.status == "acknowledged":
        # Unacknowledge - set back to pending and schedule next reminder
        invoice.status = "pending"
        invoice.acknowledged_at = None
        invoice.reminder_next_at = get_utc_now() + timedelta(
            days=invoice.reminder_frequency_days
        )
    else:
        # Acknowledge - clear reminder
        invoice.status = "acknowledged"
        invoice.acknowledged_at = get_utc_now()
        invoice.reminder_next_at = None

    invoice.updated_at = get_utc_now()
    await db.commit()
    await db.refresh(invoice)

    return success_response(data=invoice)


@router.post("/{invoice_id}/follow-up")
async def add_follow_up_note(
    invoice_id: UUID,
    note_data: InvoiceFollowUpNote,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a follow-up note to an invoice"""
    result = await db.execute(
        select(Invoice).where(
            and_(Invoice.id == invoice_id, Invoice.user_id == current_user.id)
        )
    )
    invoice = result.scalar_one_or_none()

    if not invoice:
        raise HTTPException(status_code=404, detail=INVOICE_NOT_FOUND_ERROR)

    # Add note to follow-up history
    new_note = {
        "timestamp": get_utc_now().isoformat(),
        "note": note_data.note,
    }

    if invoice.follow_up_history is None:
        invoice.follow_up_history = []

    invoice.follow_up_history.append(new_note)
    invoice.last_follow_up_at = get_utc_now()
    invoice.updated_at = get_utc_now()

    # Schedule next reminder if not acknowledged
    if invoice.status != "acknowledged":
        invoice.reminder_next_at = get_utc_now() + timedelta(
            days=invoice.reminder_frequency_days
        )

    # Mark as modified to trigger SQLAlchemy update for JSON field
    from sqlalchemy.orm import attributes

    attributes.flag_modified(invoice, "follow_up_history")

    await db.commit()
    await db.refresh(invoice)

    return success_response(data=invoice)


@router.get("/reminders/due")
async def get_due_reminders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get invoices with reminders due"""
    now = get_utc_now()
    query = select(Invoice).where(
        and_(
            Invoice.user_id == current_user.id,
            Invoice.status != "acknowledged",
            Invoice.reminder_next_at <= now,
        )
    )

    result = await db.execute(query)
    invoices = result.scalars().all()

    return success_response(
        data={"invoices": invoices, "total": len(invoices), "skip": 0, "limit": len(invoices)}
    )
