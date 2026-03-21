"""
SmartQueue AI — FastAPI Application Entry Point
SAVE AS: app/main.py

Install APScheduler first:
    pip install apscheduler
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from app.database.db import engine, Base, get_db
from app.routers import auth, tokens, queues, analytics, healthcare, banking, admin
from app.routers.slots import router as slots_router
from app.services.websocket_manager import manager
from app.ai.predictor import WaitTimePredictor
from app.models import Token, TokenStatus

# APScheduler for background tasks (no-show expiry + daily slot activation)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

predictor = WaitTimePredictor()
scheduler = AsyncIOScheduler()


# ── Background tasks ──────────────────────────────────────────────────────────

async def run_expiry_check():
    """Auto-expire no-show tokens every 5 minutes."""
    db = next(get_db())
    try:
        cutoff = datetime.utcnow() - timedelta(minutes=15)
        no_shows = db.query(Token).filter(
            Token.status             == TokenStatus.ACTIVE,
            Token.appointment_time   != None,
            Token.appointment_time   <  cutoff,
            Token.service_started_at == None
        ).all()
        for t in no_shows:
            t.status     = TokenStatus.EXPIRED
            t.expired_at = datetime.utcnow()
        if no_shows:
            db.commit()
            print(f"[Scheduler] Auto-expired {len(no_shows)} no-show token(s)")
    except Exception as e:
        print(f"[Scheduler] Expiry error: {e}")
    finally:
        db.close()


async def run_daily_activation():
    """Activate today's pre-booked tokens at midnight."""
    from datetime import date
    db = next(get_db())
    try:
        from app.models import AppointmentSlot
        today = date.today()
        booked = (
            db.query(Token)
            .join(AppointmentSlot)
            .filter(
                AppointmentSlot.slot_date == today,
                Token.status == TokenStatus.BOOKED
            )
            .all()
        )
        for t in booked:
            t.status = TokenStatus.ACTIVE
        if booked:
            db.commit()
            print(f"[Scheduler] Activated {len(booked)} pre-booked token(s) for {today}")
    except Exception as e:
        print(f"[Scheduler] Activation error: {e}")
    finally:
        db.close()


# ── App lifespan ──────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    predictor.train_initial_model()

    # Schedule background jobs
    scheduler.add_job(run_expiry_check,      'interval', minutes=5,  id='expiry_check')
    scheduler.add_job(run_daily_activation,  'cron',     hour=0, minute=1, id='daily_activation')
    scheduler.start()
    print("[Scheduler] Started: expiry check every 5min, activation at 00:01 daily")

    yield

    # Shutdown
    scheduler.shutdown(wait=False)
    print("[Scheduler] Stopped")


# ── App instance ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="SmartQueue AI",
    description="AI-Powered Queue Management System for Healthcare & Banking",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router,        prefix="/api/auth",        tags=["Authentication"])
app.include_router(tokens.router,      prefix="/api/tokens",      tags=["Tokens"])
app.include_router(queues.router,      prefix="/api/queues",      tags=["Queues"])
app.include_router(healthcare.router,  prefix="/api/healthcare",  tags=["Healthcare"])
app.include_router(banking.router,     prefix="/api/banking",     tags=["Banking"])
app.include_router(analytics.router,   prefix="/api/analytics",   tags=["Analytics"])
app.include_router(admin.router,       prefix="/api/admin",       tags=["Admin"])
app.include_router(slots_router,       prefix="/api/slots",       tags=["Appointment Slots"])


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "message": "SmartQueue AI Backend",
        "version": "2.0.0",
        "status":  "operational",
        "features": ["pre-booking", "otp-verification", "auto-expiry", "priority-queue"]
    }


# ── WebSocket ─────────────────────────────────────────────────────────────────

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client {client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(client_id)
