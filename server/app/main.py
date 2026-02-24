"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import engine, Base
from sqlalchemy import text
from app.middleware import (
    ErrorHandlerMiddleware,
    RequestIDMiddleware,
    RateLimitMiddleware,
)
from app.routes import (
    auth,
    drive,
    core,
    admin,
    subscriptions,
    business_profile,
    invoices,
    appointments,
    contact,
    wallet,
    cms,
    payments,
    user_settings,
)

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Create tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting CreditDataWatch API...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            try:
                # Migration: ensure PO address columns exist
                dburl = str(engine.url)
                is_sqlite = dburl.startswith("sqlite")
                if is_sqlite:
                    await conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN supplier_address TEXT"))
                    await conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN delivery_address TEXT"))
                    await conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN invoice_address TEXT"))
                else:
                    await conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN IF NOT EXISTS supplier_address TEXT"))
                    await conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN IF NOT EXISTS delivery_address TEXT"))
                    await conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN IF NOT EXISTS invoice_address TEXT"))
                logger.info("PO address columns migrated/verified")
            except Exception as e:
                logger.info(f"PO address migration step skipped or already applied: {e}")
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.warning(f"Database connection failed during startup: {e}")
        logger.info("Continuing without database initialization...")

    yield

    # Shutdown
    logger.info("Shutting down...")
    try:
        await engine.dispose()
    except Exception as e:
        logger.warning(f"Error disposing database engine: {e}")


app = FastAPI(
    title="CreditDataWatch API",
    description="Credit intelligence and B2B transaction management",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# Ensure dev origins are always allowed (e.g. if .env only has 3000, frontend on 3001 would be blocked)
_dev_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
    "http://localhost:3002",
   
]
_cors_origins = list(settings.CORS_ORIGINS) if settings.CORS_ORIGINS else []
for origin in _dev_origins:
    if origin not in _cors_origins:
        _cors_origins.append(origin)

# Middleware: add in reverse order of execution. Last added runs first.
# CORS is added last so it runs first and handles preflight OPTIONS before TrustedHost.
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# API prefix constant
API_PREFIX = "/api/v1"

# Routes
app.include_router(auth.router, prefix=f"{API_PREFIX}/auth", tags=["Authentication"])
app.include_router(core.user_router, prefix=f"{API_PREFIX}/user", tags=["User"])
app.include_router(core.po_router, prefix=f"{API_PREFIX}/purchase-orders", tags=["Purchase Orders"])
app.include_router(core.purchase_history_router, prefix=API_PREFIX, tags=["Purchase History"])
app.include_router(invoices.router, prefix=API_PREFIX, tags=["Invoices"])
app.include_router(core.defaulter_router, prefix=f"{API_PREFIX}/defaulters", tags=["Defaulters"])
app.include_router(core.credit_router, prefix=f"{API_PREFIX}/credit-reports", tags=["Credit Reports"])
app.include_router(core.settlement_router, prefix=f"{API_PREFIX}/settlements", tags=["Settlement"])
app.include_router(appointments.router, prefix=API_PREFIX, tags=["Appointments"])
app.include_router(contact.router, prefix=API_PREFIX, tags=["Contact"])
app.include_router(subscriptions.router, prefix=API_PREFIX, tags=["Subscriptions"])
app.include_router(business_profile.router, prefix=API_PREFIX, tags=["Account"])
app.include_router(drive.router, prefix=f"{API_PREFIX}/drive", tags=["Google Drive"])
app.include_router(wallet.router, prefix=API_PREFIX, tags=["Wallet"])
app.include_router(admin.router, prefix=f"{API_PREFIX}/admin", tags=["Admin"])
app.include_router(cms.router, prefix=API_PREFIX, tags=["CMS"])
app.include_router(payments.router, prefix=f"{API_PREFIX}/payments", tags=["Payments"])
app.include_router(user_settings.router, prefix=f"{API_PREFIX}/user/settings", tags=["User Settings"])


@app.get("/health")
async def health_check():
    db_status = "ok"
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unavailable: {str(e)}"
    return {"status": "ok", "service": "creditdatawatch-api", "version": "1.0.0", "db": db_status}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CreditDataWatch API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
