"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging
import re

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
        logger.info(f"DATABASE_URL={str(engine.url)}")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            try:
                sel = await conn.execute(text("SELECT 1"))
                logger.info(f"DB SELECT 1 result={sel.scalar()}")
            except Exception as e:
                import traceback; logger.error("DB SELECT 1 failed"); traceback.print_exc(); raise
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
            try:
                # Migration: users table to new company-user model
                dburl = str(engine.url)
                is_sqlite = dburl.startswith("sqlite")
                if not is_sqlite:
                    # Drop old global unique index/constraint on users.gstin if exists
                    await conn.execute(text("""
                        DO $$
                        DECLARE idxname text;
                        DECLARE rec RECORD;
                        BEGIN
                            SELECT i.relname INTO idxname
                            FROM pg_class t
                            JOIN pg_index x ON t.oid = x.indrelid
                            JOIN pg_class i ON i.oid = x.indexrelid
                            JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(x.indkey)
                            WHERE t.relname = 'users' AND i.relname LIKE 'users_gstin%';
                            IF idxname IS NOT NULL THEN
                                EXECUTE 'DROP INDEX IF EXISTS ' || idxname;
                            END IF;
                            -- Drop any unique index on users that includes gstin (safety)
                            FOR rec IN
                                SELECT indexname FROM pg_indexes 
                                WHERE schemaname = ANY(current_schemas(false))
                                  AND tablename = 'users'
                                  AND indexdef ILIKE '%%unique%%'
                                  AND indexdef ILIKE '%%(gstin%%'
                            LOOP
                                EXECUTE 'DROP INDEX IF EXISTS ' || quote_ident(rec.indexname);
                            END LOOP;
                        END $$;
                    """))
                    # Ensure company_id and role/status columns exist
                    # Add company_id column if not exists
                    await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS company_id VARCHAR(36)"))
                    await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS name VARCHAR(255)"))
                    await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'ACTIVE'"))
                    await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(30) DEFAULT 'USER'"))
                    # Ensure non-unique index for (gstin, company_id) and allow multiple employees per company GSTIN
                    await conn.execute(text("DROP INDEX IF EXISTS users_gstin_company_unique"))
                    await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_gstin_company ON users (gstin, company_id)"))
                    # Ensure gstin is NOT NULL (required)
                    await conn.execute(text("ALTER TABLE users ALTER COLUMN gstin SET NOT NULL"))
                    # Add permanent bypass flags
                    await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_bypass BOOLEAN DEFAULT FALSE"))
                    await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS full_access BOOLEAN DEFAULT FALSE"))
                    await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(20) DEFAULT 'INACTIVE'"))
                else:
                    # SQLite-compatible migrations
                    try:
                        await conn.execute(text("ALTER TABLE users ADD COLUMN company_id VARCHAR(36)"))
                    except Exception:
                        pass
                    try:
                        await conn.execute(text("ALTER TABLE users ADD COLUMN name VARCHAR(255)"))
                    except Exception:
                        pass
                    try:
                        await conn.execute(text("ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'ACTIVE'"))
                    except Exception:
                        pass
                    try:
                        await conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(30) DEFAULT 'USER'"))
                    except Exception:
                        pass
                    try:
                        await conn.execute(text("ALTER TABLE users ADD COLUMN subscription_bypass BOOLEAN DEFAULT FALSE"))
                    except Exception:
                        pass
                    try:
                        await conn.execute(text("ALTER TABLE users ADD COLUMN full_access BOOLEAN DEFAULT FALSE"))
                    except Exception:
                        pass
                    try:
                        await conn.execute(text("ALTER TABLE users ADD COLUMN subscription_status VARCHAR(20) DEFAULT 'INACTIVE'"))
                    except Exception:
                        pass
                    # Note: Index creation and other operations might need to be added here for SQLite if necessary
                logger.info("Users table migrated/verified for company-user model")
            except Exception as e:
                logger.info(f"Users migration step skipped or already applied: {e}")
        # Ensure PurchaseOrder table columns exist
        try:
            async with engine.begin() as conn:
                await conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN IF NOT EXISTS payment_completed_at TIMESTAMP WITHOUT TIME ZONE"))
                await conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()"))
                await conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITHOUT TIME ZONE"))
                # rename legacy columns to new schema
                await conn.execute(text("DO $$ BEGIN IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='purchase_orders' AND column_name='number') THEN ALTER TABLE purchase_orders RENAME COLUMN number TO po_number; END IF; END $$;"))
                await conn.execute(text("DO $$ BEGIN IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='purchase_orders' AND column_name='vendor_name') THEN ALTER TABLE purchase_orders RENAME COLUMN vendor_name TO vendor; END IF; END $$;"))
                await conn.execute(text("DO $$ BEGIN IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='purchase_orders' AND column_name='vendor_gstin') THEN ALTER TABLE purchase_orders RENAME COLUMN vendor_gstin TO gstin; END IF; END $$;"))
                await conn.execute(text("DO $$ BEGIN IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='purchase_orders' AND column_name='is_archived') THEN ALTER TABLE purchase_orders RENAME COLUMN is_archived TO archived; END IF; END $$;"))
                await conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN IF NOT EXISTS company_id VARCHAR(36)"))
                # Add vendor contact columns (SQLite does not support IF NOT EXISTS on ALTER TABLE)
                dburl = str(engine.url)
                is_sqlite_local = dburl.startswith("sqlite")
                if is_sqlite_local:
                    try:
                        await conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN vendor_email VARCHAR(255)"))
                    except Exception:
                        pass
                    try:
                        await conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN vendor_phone VARCHAR(20)"))
                    except Exception:
                        pass
                else:
                    await conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN IF NOT EXISTS vendor_email VARCHAR(255)"))
                    await conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN IF NOT EXISTS company_id VARCHAR(36)"))
                # Add vendor contact columns (SQLite does not support IF NOT EXISTS on ALTER TABLE)
                dburl = str(engine.url)
                is_sqlite_local = dburl.startswith("sqlite")
                if is_sqlite_local:
                    try:
                        await conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN vendor_email VARCHAR(255)"))
                    except Exception:
                        pass
                    try:
                        await conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN vendor_phone VARCHAR(20)"))
                    except Exception:
                        pass
                else:
                    await conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN IF NOT EXISTS vendor_email VARCHAR(255)"))
                    await conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN IF NOT EXISTS vendor_phone VARCHAR(20)"))
                await conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN IF NOT EXISTS legal_notice_sent_at TIMESTAMP WITHOUT TIME ZONE"))
                await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_po_company_status ON purchase_orders (company_id, status)"))
                await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_po_gstin ON purchase_orders (gstin)"))
                await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_po_payment ON purchase_orders (payment_completed_at)"))
                await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_po_created ON purchase_orders (created_at)"))
                await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_po_updated ON purchase_orders (updated_at)"))
                await conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN IF NOT EXISTS payment_window_days INTEGER DEFAULT 50"))
                # ADDED: legal_support_requested_at column
                dburl = str(engine.url)
                is_sqlite_local = dburl.startswith("sqlite")
                if is_sqlite_local:
                    try:
                        await conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN legal_support_requested_at TIMESTAMP"))
                    except Exception:
                        pass
                else:
                    await conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN IF NOT EXISTS legal_support_requested_at TIMESTAMP WITHOUT TIME ZONE"))
                
                # ADDED: Drop any UNIQUE index on po_number to allow duplicates (idempotent)
                dburl2 = str(engine.url)
                is_sqlite2 = dburl2.startswith("sqlite")
                if not is_sqlite2:
                    await conn.execute(text("DROP INDEX IF EXISTS ix_purchase_orders_po_number"))
                # backfill company_id from users
                await conn.execute(text("UPDATE purchase_orders po SET company_id = u.company_id FROM users u WHERE po.user_id = u.id AND po.company_id IS NULL"))
                # backfill archived column
                await conn.execute(text("UPDATE purchase_orders SET archived = FALSE WHERE archived IS NULL"))
            logger.info("PurchaseOrder table columns migrated/verified")
        except Exception as e:
            logger.info(f"PurchaseOrder migration step skipped or already applied: {e}")
        try:
            # Migration: add reminder_subject and reminder_body to po_reminder_configs
            async with engine.begin() as conn:
                dburl = str(engine.url)
                is_sqlite = dburl.startswith("sqlite")
                if is_sqlite:
                    try:
                        await conn.execute(text("ALTER TABLE po_reminder_configs ADD COLUMN reminder_subject VARCHAR(255)"))
                    except Exception: pass
                    try:
                        await conn.execute(text("ALTER TABLE po_reminder_configs ADD COLUMN reminder_body TEXT"))
                    except Exception: pass
                else:
                    await conn.execute(text("ALTER TABLE po_reminder_configs ADD COLUMN IF NOT EXISTS reminder_subject VARCHAR(255)"))
                    await conn.execute(text("ALTER TABLE po_reminder_configs ADD COLUMN IF NOT EXISTS reminder_body TEXT"))
            logger.info("po_reminder_configs columns migrated/verified")
        except Exception as e:
            logger.info(f"po_reminder_configs migration step skipped or already applied: {e}")
        try:
            # Migration: create scheduled_reminders table
            async with engine.begin() as conn:
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS scheduled_reminders (
                        id VARCHAR(36) PRIMARY KEY,
                        purchase_order_id VARCHAR(36) NOT NULL,
                        user_id VARCHAR(36) NOT NULL,
                        subject VARCHAR(255) NOT NULL,
                        body TEXT NOT NULL,
                        scheduled_at DATETIME NOT NULL,
                        sent_at DATETIME,
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """))
            logger.info("scheduled_reminders table verified")
        except Exception as e:
            logger.info(f"scheduled_reminders migration failed: {e}")
        try:
            # Migration: create app_settings table
            async with engine.begin() as conn:
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS app_settings (
                        id VARCHAR(36) PRIMARY KEY,
                        payment_window_days INTEGER DEFAULT 50,
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """))
                # Insert default settings if not present
                res = await conn.execute(text("SELECT id FROM app_settings LIMIT 1"))
                if res.first() is None:
                    await conn.execute(text("INSERT INTO app_settings (id, payment_window_days) VALUES ('default', 50)"))
            logger.info("app_settings table verified")
        except Exception as e:
            logger.info(f"app_settings migration failed: {e}")
        logger.info("Database tables created/verified")
        try:
            await _ensure_dev_admin()  # idempotent bootstrap for developer admin and company
            logger.info("Developer admin ensured")
        except Exception as e:
            logger.info(f"Developer admin bootstrap skipped or failed: {e}")
    except Exception as e:
        logger.warning(f"Database connection failed during startup: {e}")
        logger.info("Continuing without database initialization...")

    # Start background tasks
    import asyncio
    if getattr(settings, "ENABLE_SCHEDULER", True):
        asyncio.create_task(_daily_tasks_runner())
        asyncio.create_task(_scheduled_reminders_runner())
        asyncio.create_task(_overdue_legal_notifier_runner())

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

import os 
from fastapi.staticfiles import StaticFiles 
os.makedirs("uploads", exist_ok=True) 
app.mount( 
    "/uploads", 
    StaticFiles(directory="uploads"), 
    name="uploads" 
) 

# Ensure dev origins are always allowed (e.g. if .env only has 3000, frontend on 3001 would be blocked)
_dev_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
    "http://localhost:3002",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3002",
]
_cors_origins = list(settings.CORS_ORIGINS) if settings.CORS_ORIGINS else []
for origin in _dev_origins:
    if origin not in _cors_origins:
        _cors_origins.append(origin)
_cors_regex = re.compile(r"^http://localhost:\d{4}$")

@app.middleware("http")
async def _cors_fallback(request, call_next):
    try:
        response = await call_next(request)
    except Exception as e:
        import traceback
        logger.error(f"Middleware caught unhandled exception: {e}")
        traceback.print_exc()
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Internal Server Error", "detail": str(e)}
        )
    origin = request.headers.get("origin")
    if origin and (origin in _cors_origins or _cors_regex.match(origin)):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

# Middleware: add in reverse order of execution. Last added runs first.
# CORS is added last so it runs first and handles preflight OPTIONS before TrustedHost.
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=r"http://localhost:\d{4}",
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
app.include_router(core.notifications_router, prefix=API_PREFIX, tags=["Notifications"])
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
from app.routes import ratings, invitations
app.include_router(ratings.router, prefix=f"{API_PREFIX}", tags=["Ratings"])
app.include_router(invitations.router, prefix=f"{API_PREFIX}", tags=["Invitations"])
from app.routes import credibility
app.include_router(credibility.router, prefix=f"{API_PREFIX}", tags=["Credibility"])
from app.routes import chat
app.include_router(chat.router, prefix=f"{API_PREFIX}", tags=["Chat"])

import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from uuid import uuid4
from .database import AsyncSessionLocal
from app.services.credibility_service import CredibilityService
from .models import PurchaseOrder, Notification, User
from app.services.email_service import EmailService

async def _daily_tasks_runner():
    while True:
        now = datetime.now(timezone.utc)
        # compute next 2 AM UTC
        next_run = now.replace(hour=2, minute=0, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)
        delay = (next_run - now).total_seconds()
        await asyncio.sleep(delay)
        try:
            # run BCI recalc
            async with AsyncSessionLocal() as session:
                await CredibilityService.recalc_all(session)
                await session.commit()
                # due in 3 days notifications
                cutoff_start = datetime.utcnow()
                cutoff_end = cutoff_start + timedelta(days=3)
                stmt = select(PurchaseOrder, User).join(User, PurchaseOrder.user_id == User.id).where(
                    (PurchaseOrder.payment_completed_at.is_(None)) &
                    (PurchaseOrder.due_date >= cutoff_start) &
                    (PurchaseOrder.due_date < cutoff_end)
                )
                res = await session.execute(stmt)
                for po, user in res.all():
                    note = Notification(
                        id=str(uuid4()),
                        user_id=user.id,
                        type="PO_DUE_SOON",
                        message=f"PO {po.po_number} due on {po.due_date.date()}",
                        related_po_id=po.id,
                    )
                    session.add(note)
                    try:
                        EmailService().send_email(user.email, f"PO {po.po_number} due soon", f"PO {po.po_number} due on {po.due_date.date()}")
                    except Exception:
                        pass
                # overdue notifications
                stmt2 = select(PurchaseOrder, User).join(User, PurchaseOrder.user_id == User.id).where(
                    (PurchaseOrder.payment_completed_at.is_(None)) &
                    (PurchaseOrder.due_date < datetime.utcnow())
                )
                res2 = await session.execute(stmt2)
                for po, user in res2.all():
                    note2 = Notification(
                        id=str(uuid4()),
                        user_id=user.id,
                        type="PO_OVERDUE",
                        message=f"PO {po.po_number} is overdue since {po.due_date.date()}",
                        related_po_id=po.id,
                    )
                    session.add(note2)
                    try:
                        EmailService().send_email(user.email, f"PO {po.po_number} overdue", f"PO {po.po_number} overdue since {po.due_date.date()}")
                    except Exception:
                        pass
                # Vendor reminders per admin config
                try:
                    from app.models import POReminderConfig
                    cfg_res = await session.execute(select(POReminderConfig))
                    cfg = cfg_res.scalars().first()
                    before_days = (cfg.before_days or []) if cfg else []
                    after_daily = bool(cfg.after_due_daily_enabled) if cfg else False
                    
                    custom_subject = cfg.reminder_subject if cfg else None
                    custom_body = cfg.reminder_body if cfg else None

                    def format_vendor_email(template, po, default_val):
                        if not template:
                            return default_val
                        return template.replace("{vendor_name}", po.vendor or "") \
                                       .replace("{amount}", f"₹{po.amount:,.2f}") \
                                       .replace("{due_date}", str(po.due_date.date())) \
                                       .replace("{po_number}", po.po_number or "")

                    # Send BEFORE due date reminders
                    if before_days:
                        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                        for d in before_days:
                            try:
                                delta = int(d)
                            except Exception:
                                continue
                            target_start = today + timedelta(days=delta)
                            target_end = target_start + timedelta(days=1)
                            q = select(PurchaseOrder).where(
                                (PurchaseOrder.payment_completed_at.is_(None)) &
                                (PurchaseOrder.due_date >= target_start) &
                                (PurchaseOrder.due_date < target_end)
                            )
                            po_res = await session.execute(q)
                            for po in po_res.scalars().all():
                                if po.vendor_email:
                                    subject = format_vendor_email(custom_subject, po, f"Reminder: PO {po.po_number} due in {delta} day(s)")
                                    body = format_vendor_email(custom_body, po, f"PO {po.po_number} to {po.vendor} amount {po.amount} is due on {po.due_date.date()}.")
                                    try:
                                        EmailService().send_email(po.vendor_email, subject, body)
                                    except Exception:
                                        pass
                    # Send AFTER due date daily reminders
                    if after_daily:
                        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                        q2 = select(PurchaseOrder).where(
                            (PurchaseOrder.payment_completed_at.is_(None)) &
                            (PurchaseOrder.due_date < today_start) &
                            (PurchaseOrder.status != "Closed")
                        )
                        po_res2 = await session.execute(q2)
                        for po in po_res2.scalars().all():
                            if po.vendor_email:
                                subject = format_vendor_email(custom_subject, po, f"Overdue: PO {po.po_number}")
                                body = format_vendor_email(custom_body, po, f"PO {po.po_number} has been overdue since {po.due_date.date()}. Kindly process immediately.")
                                try:
                                    EmailService().send_email(po.vendor_email, subject, body)
                                except Exception:
                                    pass
                    
                    # Process SCHEDULED reminders
                    # (Logic moved to frequent scheduler for responsiveness)
                    pass
                except Exception as e:
                    logger.error(f"Error in background reminder tasks: {e}")
                await session.commit()
        except Exception as e:
            logger.error(f"Daily tasks failed: {e}")

async def _scheduled_reminders_runner():
    """Checks for due scheduled reminders every minute"""
    logger.info("Starting frequent scheduled reminders runner (1m interval)")
    while True:
        try:
            async with AsyncSessionLocal() as session:
                from app.models import ScheduledReminder, PurchaseOrder
                now = datetime.utcnow()
                # Find reminders due now or in the past that haven't been sent
                q_sched = select(ScheduledReminder, PurchaseOrder).join(
                    PurchaseOrder, ScheduledReminder.purchase_order_id == PurchaseOrder.id
                ).where(
                    (ScheduledReminder.scheduled_at <= now) &
                    (ScheduledReminder.sent_at.is_(None))
                )
                sched_res = await session.execute(q_sched)
                tasks = sched_res.all()
                if tasks:
                    logger.info(f"Found {len(tasks)} due reminders to process")
                
                for sr, po in tasks:
                    if po.vendor_email:
                        try:
                            logger.info(f"Sending scheduled reminder {sr.id} to {po.vendor_email}")
                            EmailService().send_email(po.vendor_email, sr.subject, sr.body)
                            sr.sent_at = datetime.utcnow()
                            # Use a separate commit per reminder to ensure progress is saved
                            await session.commit()
                        except Exception as e:
                            logger.error(f"Failed to send scheduled reminder {sr.id}: {e}")
                
                await session.commit()
        except Exception as e:
            logger.error(f"Error in scheduled reminders runner: {e}")
        
        # Wait for 60 seconds before next check
        await asyncio.sleep(60)

async def _overdue_legal_notifier_runner():
    """Checks for newly overdue POs and notifies legal team every minute"""
    logger.info("Starting frequent overdue legal notifier runner (1m interval)")
    while True:
        try:
            async with AsyncSessionLocal() as db:
                from datetime import datetime, date
                today = date.today()
                
                # Find POs that just became overdue (due_date < today) 
                # AND legal_support_requested_at is NULL 
                # AND status is "Open"
                # Use scalar_one_or_none or scalars().all()
                stmt = select(PurchaseOrder).where(
                    PurchaseOrder.due_date < datetime.combine(today, datetime.min.time()),
                    PurchaseOrder.status == "Open",
                    PurchaseOrder.legal_support_requested_at == None
                )
                overdue_pos_res = await db.execute(stmt)
                overdue_pos = overdue_pos_res.scalars().all()
                
                if overdue_pos:
                    logger.info(f"Found {len(overdue_pos)} overdue POs to notify legal team")
                
                for po in overdue_pos:
                    # Send auto email to legal team 
                    subject = f"⚠️ AUTO ALERT: PO Overdue - {po.po_number} - {po.vendor}"
                    body = f"""
AUTOMATIC OVERDUE ALERT 
======================= 

This is an automatic alert that the following PO is now overdue: 

PO Number : {po.po_number} 
Vendor    : {po.vendor} 
Amount    : Rs.{po.amount} 
Due Date  : {po.due_date} 
Status    : {po.status} 

Please review and take necessary action. 

CreditDataWatch Automated System 
                    """
                    try: 
                        EmailService().send_email("payalshinde906@gmail.com", subject, body) 
                        po.legal_support_requested_at = datetime.utcnow() 
                        logger.info(f"[LEGAL] Auto alert sent for overdue PO: {po.po_number}")
                    except Exception as e: 
                        logger.error(f"[LEGAL ERROR] Failed to send auto alert: {e}") 
                
                await db.commit()
        except Exception as e:
            logger.error(f"Error in overdue legal notifier runner: {e}")
            
        await asyncio.sleep(60)

# Development/bootstrapping: Ensure developer admin and company exist
try:
    from sqlalchemy import select
    from uuid import uuid4
    from .database import AsyncSessionLocal
    from .models import User, Company
    from app.utils.password import hash_password
    from app.utils.phone import format_phone_e164, is_valid_phone
    from .utils.gstin import is_valid_gstin
    async def _ensure_dev_admin():
        """
        Idempotently ensure the fixed developer account exists and is configured correctly.
        IMPORTANT: This function must not modify any other users/companies/data.
        """
        dev_email = "payalshinde906@gmail.com"
        dev_gstin = "22AAAAD0000A1Z5"
        dev_phone = "+919112896827"
        dev_role = "MASTER_ADMIN"
        dev_company_name = "Test Company"
        dev_password = "AdminPass123!"
        dev_domain = "gmail.com"

        if not is_valid_gstin(dev_gstin):
            return

        async with AsyncSessionLocal() as _db:
            # Ensure company exists for developer GSTIN
            res_company = await _db.execute(select(Company).where(Company.gstin == dev_gstin))
            company = res_company.scalars().first()
            if not company:
                company = Company(
                    id=str(uuid4()),
                    company_name=dev_company_name,
                    gstin=dev_gstin,
                    domain_name=dev_domain,
                    is_verified=True,
                )
                _db.add(company)
                await _db.flush()

            # Ensure developer user exists and is configured correctly
            res_user = await _db.execute(select(User).where(User.email == dev_email))
            user = res_user.scalars().first()
            if user:
                changed = False
                if (user.role or "") != dev_role:
                    user.role = dev_role
                    changed = True
                if getattr(user, "is_active", True) is not True:
                    user.is_active = True
                    changed = True
                if getattr(user, "subscription_bypass", False) is not True:
                    user.subscription_bypass = True
                    changed = True
                if getattr(user, "full_access", False) is not True:
                    user.full_access = True
                    changed = True
                if (user.gstin or "").upper() != dev_gstin:
                    user.gstin = dev_gstin
                    changed = True
                if not user.company_id or user.company_id != company.id:
                    user.company_id = company.id
                    changed = True
                if (user.phone or "") != dev_phone:
                    user.phone = dev_phone
                    changed = True
                if (user.status or "").upper() != "ACTIVE":
                    user.status = "ACTIVE"
                    changed = True
                if (user.company_name or "") != dev_company_name:
                    user.company_name = dev_company_name
                    changed = True
                if (getattr(user, "subscription_status", "INACTIVE") or "INACTIVE") != "ACTIVE":
                    try:
                        user.subscription_status = "ACTIVE"
                        changed = True
                    except Exception:
                        pass

                # Always reset developer password hash to the current bcrypt_sha256 hash
                # (hash includes salt, so equality checks are not meaningful).
                user.password_hash = hash_password(dev_password)
                changed = True

                if changed:
                    await _db.commit()
            else:
                user = User(
                    id=str(uuid4()),
                    company_id=company.id,
                    name=dev_company_name,
                    email=dev_email,
                    password_hash=hash_password(dev_password),
                    role=dev_role,
                    status="ACTIVE",
                    phone=dev_phone,
                    gstin=dev_gstin,
                    company_name=dev_company_name,
                    subscription_bypass=True,
                    full_access=True,
                    is_active=True,
                    subscription_status="ACTIVE",
                )
                _db.add(user)
                await _db.commit()
except Exception:
    pass


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
