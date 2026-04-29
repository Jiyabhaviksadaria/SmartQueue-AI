"""
SmartQueue AI — FastAPI Entry Point
SAVE AS: app/main.py
pip install apscheduler twilio


from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from app.database.db import engine, Base, get_db
from app.routers import auth, tokens, queues, analytics, healthcare, banking, admin
from app.routers.slots     import router as slots_router
from app.routers.grievance import router as grievance_router
from app.services.websocket_manager import manager
from app.ai.predictor import WaitTimePredictor
from app.models import Token, TokenStatus
from apscheduler.schedulers.asyncio import AsyncIOScheduler

predictor = WaitTimePredictor()
scheduler = AsyncIOScheduler()


async def run_expiry_check():
    db = next(get_db())
    try:
        from app.services.notification_service import sms_token_expired
        cutoff   = datetime.utcnow() - timedelta(minutes=15)
        no_shows = db.query(Token).filter(
            Token.status == TokenStatus.ACTIVE,
            Token.appointment_time != None,
            Token.appointment_time < cutoff,
            Token.service_started_at == None
        ).all()
        for t in no_shows:
            t.status     = TokenStatus.EXPIRED
            t.expired_at = datetime.utcnow()
            if t.patient_phone:
                sms_token_expired(t.patient_phone, t.token_number, t.service_name or "hospital")
        if no_shows:
            db.commit()
            print(f"[Scheduler] Expired {len(no_shows)} no-show token(s)")
    except Exception as e:
        print(f"[Scheduler] Expiry error: {e}")
    finally:
        db.close()


async def run_daily_activation():
    from datetime import date
    db = next(get_db())
    try:
        from app.models import AppointmentSlot
        from app.services.notification_service import sms_token_activated
        today  = date.today()
        booked = (
            db.query(Token).join(AppointmentSlot)
            .filter(AppointmentSlot.slot_date == today, Token.status == TokenStatus.BOOKED)
            .all()
        )
        for t in booked:
            t.status = TokenStatus.ACTIVE
            if t.patient_phone:
                sms_token_activated(
                    t.patient_phone, t.token_number,
                    t.service_name or "hospital",
                    t.position or 1, t.estimated_wait_time or 0
                )
        if booked:
            db.commit()
            print(f"[Scheduler] Activated {len(booked)} token(s) for {today}")
    except Exception as e:
        print(f"[Scheduler] Activation error: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    predictor.train_initial_model()
    scheduler.add_job(run_expiry_check,     'interval', minutes=5,        id='expiry')
    scheduler.add_job(run_daily_activation, 'cron',     hour=0, minute=1, id='activate')
    scheduler.start()
    print("[Scheduler] Started — expiry every 5min, activation at 00:01")
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(
    title="SmartQueue AI", version="2.0.0",
    description="AI Queue Management — Healthcare & Banking",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

app.include_router(auth.router,        prefix="/api/auth",        tags=["Auth"])
app.include_router(tokens.router,      prefix="/api/tokens",      tags=["Tokens"])
app.include_router(queues.router,      prefix="/api/queues",      tags=["Queues"])
app.include_router(healthcare.router,  prefix="/api/healthcare",  tags=["Healthcare"])
app.include_router(banking.router,     prefix="/api/banking",     tags=["Banking"])
app.include_router(analytics.router,   prefix="/api/analytics",   tags=["Analytics"])
app.include_router(admin.router,       prefix="/api/admin",       tags=["Admin"])
app.include_router(slots_router,       prefix="/api/slots",       tags=["Slots"])
app.include_router(grievance_router,   prefix="/api/grievance",   tags=["Grievance"])


@app.get("/")
async def root():
    return {"message": "SmartQueue AI", "version": "2.0.0", "status": "operational"}


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client {client_id}: {data}")
    except WebSocketDisconnect:
        managfrom fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta, date
from typing import Optional, List
import random, string

from app.database.db import get_db
from app.models import (
    AppointmentSlot, Token, TokenStatus, SlotStatus,
    Domain, PriorityLevel
)
from app.utils.token_generator import generate_token
from app.services.notification_service import (
    sms_otp, sms_booking_confirmed,
    sms_token_activated, sms_token_expired
)

router = APIRouter()

# --- SCHEMAS FOR SWAGGER ---
class SlotResponse(BaseModel):
    id: int
    slot_time: str
    slot_end: str
    available: int
    booked_count: int
    capacity: int
    is_full: bool
    status: str

    class Config:
        from_attributes = True

class AvailableSlotsResponse(BaseModel):
    date: str
    department: str
    slots: List[SlotResponse]
    message: Optional[str] = None

class OTPSendRequest(BaseModel):
    phone: str

class OTPVerifyRequest(BaseModel):
    phone: str
    otp: str

class SlotGenerateRequest(BaseModel):
    date: str
    department: str
    domain: str
    capacity: Optional[int] = 10
    doctor_id: Optional[int] = None

class SlotBookRequest(BaseModel):
    slot_id: int
    phone: str
    patient_name: str
    department: str
    domain: str
    priority: Optional[str] = "normal"
    reason: Optional[str] = None

# --- DATABASE / MEMORY ---
_otp_store: dict = {}

# --- ROUTES ---

@router.post("/otp/send")
def send_otp(data: OTPSendRequest):
    phone = data.phone.strip()
    if not phone or len(phone) < 10:
        raise HTTPException(400, "Invalid phone number.")
    otp = ''.join(random.choices(string.digits, k=6))
    _otp_store[phone] = {
        "otp": otp,
        "expires": datetime.utcnow() + timedelta(minutes=10),
        "verified": False
    }
    sms_otp(phone, otp)
    return {"message": "OTP sent.", "dev_otp": otp}

@router.post("/otp/verify")
def verify_otp(data: OTPVerifyRequest):
    phone = data.phone.strip()
    record = _otp_store.get(phone)
    if not record or datetime.utcnow() > record["expires"]:
        raise HTTPException(400, "OTP expired or not found.")
    if record["otp"] != data.otp.strip():
        raise HTTPException(400, "Incorrect OTP.")
    _otp_store[phone]["verified"] = True
    return {"verified": True, "phone": phone}

@router.get("/available", response_model=AvailableSlotsResponse)
def get_available_slots(date_str: str, department: str, domain: str, db: Session = Depends(get_db)):
    try:
        slot_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(400, "Use YYYY-MM-DD format.")

    slots = db.query(AppointmentSlot).filter(
        AppointmentSlot.slot_date == slot_date,
        AppointmentSlot.department == department,
        AppointmentSlot.domain == Domain(domain),
        AppointmentSlot.status != SlotStatus.CLOSED
    ).order_by(AppointmentSlot.slot_time).all()

    return {
        "date": date_str,
        "department": department,
        "slots": [
            {
                "id": s.id,
                "slot_time": s.slot_time,
                "slot_end": s.slot_end,
                "available": max(0, s.capacity - s.booked_count),
                "booked_count": s.booked_count, # This is your pre-booked data
                "capacity": s.capacity,
                "is_full": s.booked_count >= s.capacity,
                "status": s.status.value
            } for s in slots
        ]
    }

@router.post("/book")
def book_slot(data: SlotBookRequest, db: Session = Depends(get_db)):
    otp_record = _otp_store.get(data.phone.strip())
    if not otp_record or not otp_record.get("verified"):
        raise HTTPException(400, "Verify phone via OTP first.")

    slot = db.query(AppointmentSlot).filter(AppointmentSlot.id == data.slot_id).first()
    if not slot or slot.booked_count >= slot.capacity:
        raise HTTPException(400, "Slot full or invalid.")

    token_id = generate_token(data.domain, data.department.upper()[:3])
    
    token = Token(
        token_number=token_id, domain=Domain(data.domain),
        status=TokenStatus.BOOKED, slot_id=data.slot_id,
        patient_name=data.patient_name, patient_phone=data.phone.strip(),
        service_name=data.department,
        appointment_time=datetime.combine(slot.slot_date, datetime.strptime(slot.slot_time, "%H:%M").time())
    )
    
    slot.booked_count += 1
    if slot.booked_count >= slot.capacity:
        slot.status = SlotStatus.FULL
        
    db.add(token)
    db.commit()
    _otp_store.pop(data.phone.strip(), None)
    
    sms_booking_confirmed(data.phone, token_id, data.department, slot.slot_date.strftime("%d %b"), slot.slot_time, slot.booked_count)
    
    return {"token_id": token_id, "status": "booked", "slot_time": slot.slot_time}er.disconnect(client_id)"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from app.database.db import engine, Base, get_db
from app.routers import auth, tokens, queues, analytics, healthcare, banking, admin
from app.routers.slots import router as slots_router
from app.routers.grievance import router as grievance_router
from app.services.websocket_manager import manager
from app.ai.predictor import WaitTimePredictor
from app.models import Token, TokenStatus
from apscheduler.schedulers.asyncio import AsyncIOScheduler

predictor = WaitTimePredictor()
scheduler = AsyncIOScheduler()

async def run_expiry_check():
    db = next(get_db())
    try:
        from app.services.notification_service import sms_token_expired
        cutoff = datetime.utcnow() - timedelta(minutes=15)
        no_shows = db.query(Token).filter(
            Token.status == TokenStatus.ACTIVE,
            Token.appointment_time < cutoff,
            Token.service_started_at == None
        ).all()
        for t in no_shows:
            t.status = TokenStatus.EXPIRED
            if t.patient_phone:
                sms_token_expired(t.patient_phone, t.token_number, t.service_name)
        db.commit()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    predictor.train_initial_model()
    scheduler.add_job(run_expiry_check, 'interval', minutes=5)
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(
    title="SmartQueue AI", 
    version="2.0.0",
    description="AI Queue Management — Healthcare & Banking",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# Router Registration
app.include_router(auth.router,       prefix="/api/auth",       tags=["Auth"])
app.include_router(tokens.router,     prefix="/api/tokens",     tags=["Tokens"])
app.include_router(queues.router,     prefix="/api/queues",     tags=["Queues"])
app.include_router(healthcare.router, prefix="/api/healthcare", tags=["Healthcare"])
app.include_router(banking.router,    prefix="/api/banking",    tags=["Banking"])
app.include_router(analytics.router,  prefix="/api/analytics",  tags=["Analytics"])
app.include_router(admin.router,      prefix="/api/admin",      tags=["Admin"])
app.include_router(slots_router,      prefix="/api/slots",      tags=["Slots"]) # This line fixes your Swagger UI
app.include_router(grievance_router,  prefix="/api/grievance",  tags=["Grievance"])

@app.get("/")
async def root():
    return {"message": "SmartQueue AI", "version": "2.0.0", "status": "operational"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client {client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(client_id)