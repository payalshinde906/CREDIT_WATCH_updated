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
from app.middleware import ErrorHandlerMiddleware, RequestIDMiddleware, RateLimitMiddleware
from app.routes import auth, drive, core, admin, subscriptions, business_profile, invoices, appointments, contact

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

# Middleware
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# API prefix constant
API_PREFIX = "/api/v1"

# Routes
app.include_router(auth.router, prefix=f"{API_PREFIX}/auth", tags=["Authentication"])
app.include_router(core.user_router, prefix=f"{API_PREFIX}/user", tags=["User"])
app.include_router(core.po_router, prefix=f"{API_PREFIX}/purchase-orders", tags=["Purchase Orders"])
app.include_router(invoices.router, prefix=API_PREFIX, tags=["Invoices"])
app.include_router(core.defaulter_router, prefix=f"{API_PREFIX}/defaulters", tags=["Defaulters"])
app.include_router(core.credit_router, prefix=f"{API_PREFIX}/credit-reports", tags=["Credit Reports"])
app.include_router(core.settlement_router, prefix=f"{API_PREFIX}/settlements", tags=["Settlement"])
app.include_router(appointments.router, prefix=API_PREFIX, tags=["Appointments"])
app.include_router(contact.router, prefix=API_PREFIX, tags=["Contact"])
app.include_router(subscriptions.router, prefix=API_PREFIX, tags=["Subscriptions"])
app.include_router(business_profile.router, prefix=API_PREFIX, tags=["Account"])
app.include_router(drive.router, prefix=f"{API_PREFIX}/drive", tags=["Google Drive"])
app.include_router(admin.router, prefix=f"{API_PREFIX}/admin", tags=["Admin"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "creditdatawatch-api", "version": "1.0.0"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CreditDataWatch API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
    )
