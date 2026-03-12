from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.wallet import WalletBalanceResponse, WalletHistoryResponse, RedeemRequest, WalletTransactionResponse
from app.services.wallet_service import WalletService
from app.utils.response import ResponseFormatter

router = APIRouter(prefix="/wallet", tags=["Wallet"])

@router.get("/balance", response_model=ResponseFormatter[WalletBalanceResponse])
async def get_balance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = WalletService(db)
    balance = await service.get_balance(current_user.id)
    return ResponseFormatter.create_success(data={"balance": balance, "currency": "INR_POINTS"})

@router.get("/history", response_model=ResponseFormatter[WalletHistoryResponse])
async def get_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = WalletService(db)
    items, total = await service.get_history(current_user.id, page, limit)
    return ResponseFormatter.create_success(data={
        "items": items,
        "total": total,
        "page": page,
        "page_size": limit
    })

@router.post("/redeem", response_model=ResponseFormatter[WalletTransactionResponse])
async def redeem_points(
    req: RedeemRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = WalletService(db)
    transaction = await service.redeem_points(current_user.id, req.amount, req.reference)
    return ResponseFormatter.create_success(data=transaction, message="Points redeemed successfully")
