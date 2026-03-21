"""
Appointment Slots Router — SmartQueue AI
SAVE AS: app/routers/slots.py
SMS notifications added at OTP send, booking confirmed, activation, expiry.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta, date
from typing import Optional
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

SLOT_DURATION_MIN = 30
DAY_START         = "09:00"
DAY_END           = "17:00"
DEFAULT_CAPACITY  = 10
EXPIRY_MINUTES    = 15

_otp_store: dict = {}


class OTPSendRequest(BaseModel):
    phone: str

class OTPVerifyRequest(BaseModel):
    phone: str
    otp:   str

class SlotGenerateRequest(BaseModel):
    date:       str
    department: str
    domain:     str
    capacity:   Optional[int] = DEFAULT_CAPACITY
    doctor_id:  Optional[int] = None

class SlotBookRequest(BaseModel):
    slot_id:      int
    phone:        str
    patient_name: str
    department:   str
    domain:       str
    priority:     Optional[str] = "normal"
    reason:       Optional[str] = None
    age:          Optional[int] = None
    gender:       Optional[str] = None


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
    sms_otp(phone, otp)   # ← SMS sent here
    return {"message": "OTP sent.", "dev_otp": otp}  # remove dev_otp in production


@router.post("/otp/verify")
def verify_otp(data: OTPVerifyRequest):
    phone  = data.phone.strip()
    record = _otp_store.get(phone)
    if not record:
        raise HTTPException(400, "No OTP found. Request a new one.")
    if datetime.utcnow() > record["expires"]:
        _otp_store.pop(phone, None)
        raise HTTPException(400, "OTP expired. Request a new one.")
    if record["otp"] != data.otp.strip():
        raise HTTPException(400, "Incorrect OTP.")
    _otp_store[phone]["verified"] = True
    return {"verified": True, "phone": phone}


@router.post("/generate")
def generate_slots(data: SlotGenerateRequest, db: Session = Depends(get_db)):
    try:
        slot_date = datetime.strptime(data.date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(400, "Invalid date. Use YYYY-MM-DD.")
    if slot_date < date.today():
        raise HTTPException(400, "Cannot generate slots for past dates.")

    created   = []
    current_t = datetime.strptime(DAY_START, "%H:%M")
    end_t     = datetime.strptime(DAY_END, "%H:%M")
    while current_t < end_t:
        t_str   = current_t.strftime("%H:%M")
        end_str = (current_t + timedelta(minutes=SLOT_DURATION_MIN)).strftime("%H:%M")
        exists  = db.query(AppointmentSlot).filter(
            AppointmentSlot.slot_date  == slot_date,
            AppointmentSlot.slot_time  == t_str,
            AppointmentSlot.department == data.department,
            AppointmentSlot.domain     == Domain(data.domain)
        ).first()
        if not exists:
            db.add(AppointmentSlot(
                slot_date=slot_date, slot_time=t_str, slot_end=end_str,
                department=data.department, domain=Domain(data.domain),
                doctor_id=data.doctor_id, capacity=data.capacity,
                status=SlotStatus.AVAILABLE
            ))
            created.append(t_str)
        current_t += timedelta(minutes=SLOT_DURATION_MIN)
    db.commit()
    return {"date": data.date, "department": data.department,
            "slots_created": len(created), "times": created}


@router.get("/available")
def get_available_slots(
    date_str: str, department: str, domain: str,
    db: Session = Depends(get_db)
):
    try:
        slot_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(400, "Invalid date. Use YYYY-MM-DD.")

    slots = db.query(AppointmentSlot).filter(
        AppointmentSlot.slot_date  == slot_date,
        AppointmentSlot.department == department,
        AppointmentSlot.domain     == Domain(domain),
        AppointmentSlot.status     != SlotStatus.CLOSED
    ).order_by(AppointmentSlot.slot_time).all()

    if not slots:
        return {"date": date_str, "department": department, "slots": [],
                "message": "No slots available. Admin must generate slots first."}

    return {
        "date": date_str, "department": department,
        "slots": [
            {"id": s.id, "slot_time": s.slot_time, "slot_end": s.slot_end,
             "available": max(0, s.capacity - s.booked_count),
             "capacity": s.capacity, "is_full": s.booked_count >= s.capacity,
             "status": s.status.value}
            for s in slots
        ]
    }


@router.post("/book")
def book_slot(data: SlotBookRequest, db: Session = Depends(get_db)):
    otp_record = _otp_store.get(data.phone.strip())
    if not otp_record or not otp_record.get("verified"):
        raise HTTPException(400, "Phone not verified. Complete OTP first.")

    slot = db.query(AppointmentSlot).filter(AppointmentSlot.id == data.slot_id).first()
    if not slot:
        raise HTTPException(404, "Slot not found.")
    if slot.booked_count >= slot.capacity:
        raise HTTPException(400, "Slot is full. Choose another time.")
    if slot.status == SlotStatus.CLOSED:
        raise HTTPException(400, "Slot no longer available.")

    duplicate = db.query(Token).filter(
        Token.slot_id == data.slot_id,
        Token.patient_phone == data.phone.strip(),
        Token.status.notin_([TokenStatus.CANCELLED, TokenStatus.EXPIRED])
    ).first()
    if duplicate:
        raise HTTPException(400, f"Phone already has booking {duplicate.token_number} for this slot.")

    priority_map = {"emergency": PriorityLevel.EMERGENCY,
                    "senior": PriorityLevel.HIGH, "normal": PriorityLevel.NORMAL}
    token_id      = generate_token(data.domain, data.department.upper()[:3])
    slot_position = slot.booked_count + 1
    appt_datetime = datetime.combine(
        slot.slot_date, datetime.strptime(slot.slot_time, "%H:%M").time()
    )

    token = Token(
        token_number=token_id, domain=Domain(data.domain),
        status=TokenStatus.BOOKED,
        priority=priority_map.get(data.priority, PriorityLevel.NORMAL),
        slot_id=data.slot_id, patient_name=data.patient_name,
        patient_phone=data.phone.strip(), symptoms=data.reason,
        service_name=data.department, appointment_time=appt_datetime,
        estimated_wait_time=(slot_position - 1) * 8
    )
    slot.booked_count += 1
    if slot.booked_count >= slot.capacity:
        slot.status = SlotStatus.FULL
    db.add(token)
    db.commit()
    db.refresh(token)
    _otp_store.pop(data.phone.strip(), None)

    # ── SMS: booking confirmed ─────────────────────────────────────────────
    sms_booking_confirmed(
        phone=data.phone, token_id=token_id, department=data.department,
        appointment_date=slot.slot_date.strftime("%d %b %Y"),
        slot_time=slot.slot_time, slot_position=slot_position
    )

    return {
        "token_id": token_id, "slot_time": slot.slot_time, "slot_end": slot.slot_end,
        "appointment_date": slot.slot_date.strftime("%Y-%m-%d"),
        "appointment_date_display": slot.slot_date.strftime("%d %B %Y"),
        "department": data.department, "slot_position": slot_position,
        "estimated_queue_position": slot_position, "status": "booked",
        "message": (
            f"Appointment confirmed for {slot.slot_date.strftime('%d %b %Y')} "
            f"at {slot.slot_time}. You are #{slot_position} in this slot. "
            f"SMS confirmation sent to {data.phone}."
        )
    }


@router.post("/activate-today")
def activate_todays_tokens(db: Session = Depends(get_db)):
    today       = date.today()
    booked_today = (
        db.query(Token).join(AppointmentSlot)
        .filter(AppointmentSlot.slot_date == today, Token.status == TokenStatus.BOOKED)
        .all()
    )
    activated = 0
    for token in booked_today:
        token.status = TokenStatus.ACTIVE
        activated   += 1
        if token.patient_phone:
            # ── SMS: token is active today ─────────────────────────────
            sms_token_activated(
                phone=token.patient_phone, token_id=token.token_number,
                department=token.service_name or "hospital",
                position=token.position or 1,
                wait_mins=token.estimated_wait_time or 0
            )
    db.commit()
    return {"activated": activated, "date": str(today)}


@router.post("/expire-noshows")
def expire_noshows(db: Session = Depends(get_db)):
    cutoff   = datetime.utcnow() - timedelta(minutes=EXPIRY_MINUTES)
    no_shows = db.query(Token).filter(
        Token.status == TokenStatus.ACTIVE,
        Token.appointment_time != None,
        Token.appointment_time < cutoff,
        Token.service_started_at == None
    ).all()
    count = 0
    for token in no_shows:
        token.status     = TokenStatus.EXPIRED
        token.expired_at = datetime.utcnow()
        count           += 1
        if token.patient_phone:
            # ── SMS: token expired ─────────────────────────────────────
            sms_token_expired(
                phone=token.patient_phone, token_id=token.token_number,
                department=token.service_name or "hospital"
            )
    db.commit()
    return {"expired": count, "checked_at": datetime.utcnow().isoformat()}


@router.get("/booking/{token_number}")
def get_booking(token_number: str, db: Session = Depends(get_db)):
    token = db.query(Token).filter(Token.token_number == token_number).first()
    if not token:
        raise HTTPException(404, "Token not found.")
    slot = token.slot
    return {
        "token_id": token.token_number, "status": token.status.value,
        "department": token.service_name, "priority": token.priority.value,
        "patient_name": token.patient_name,
        "appointment_date": slot.slot_date.strftime("%d %B %Y") if slot else None,
        "slot_time": slot.slot_time if slot else None,
        "slot_end": slot.slot_end if slot else None,
        "estimated_wait": token.estimated_wait_time
    }
