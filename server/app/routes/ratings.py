"""
Ratings routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.dependencies import get_current_user
from app.models import Company, PurchaseOrder, Invoice, User
from app.utils import ResponseFormatter
from datetime import datetime

router = APIRouter(tags=["Ratings"])

@router.post("/ratings/check")
async def check_rating_allowed(
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check if rating is allowed based on verification and real transaction"""
    counterparty_gstin = payload.get("counterparty_gstin", "")
    if not counterparty_gstin:
        raise HTTPException(status_code=400, detail="counterparty_gstin required")
    # Get companies
    ucompany_stmt = select(Company).where(Company.id == current_user.company_id)
    ures = await db.execute(ucompany_stmt)
    user_company = ures.scalars().first()
    ccompany_stmt = select(Company).where(Company.gstin == counterparty_gstin.upper())
    cres = await db.execute(ccompany_stmt)
    counterparty_company = cres.scalars().first()
    if not user_company or not counterparty_company:
        raise HTTPException(status_code=400, detail="Company not found")
    if not user_company.is_verified or not counterparty_company.is_verified:
        raise HTTPException(status_code=400, detail="Both companies must be verified")
    # Check transactions: either PO with vendor_gstin or invoice with counterparty_gstin
    po_stmt = select(PurchaseOrder).where(
        PurchaseOrder.user_id == current_user.id,
        PurchaseOrder.vendor_gstin == counterparty_gstin.upper(),
    )
    po_res = await db.execute(po_stmt)
    po = po_res.scalars().first()
    inv_stmt = select(Invoice).where(
        Invoice.user_id == current_user.id,
        Invoice.counterparty_gstin == counterparty_gstin.upper(),
    )
    inv_res = await db.execute(inv_stmt)
    inv = inv_res.scalars().first()
    if not po and not inv:
        raise HTTPException(status_code=400, detail="No real transaction found between companies")
    return ResponseFormatter.create_success(message="Rating allowed", data={"allowed": True})
