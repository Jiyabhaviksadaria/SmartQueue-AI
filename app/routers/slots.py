"""
Appointment Slots Router — SmartQueue AI
Handles: OTP send/verify, slot generation, slot availability, booking, activation, expiry
SAVE AS: app/routers/slots.py
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta, date, time
from typing import Optional, List
import random, string

from app.database.db import get_db
from app.models import (
    AppointmentSlot, Token, TokenStatus, SlotStatus,
    Domain, PriorityLevel
)
from app.utils.token_generator import generate_token

router = APIRouter()

# ── Configuration ─────────────────────────────────────────────────────────────
SLOT_DURATION_MIN = 30      # each time slot = 30 minutes
DAY_START         = "09:00"
DAY_END           = "17:00"
DEFAULT_CAPACITY  = 10      # patients per slot
EXPIRY_MINUTES    = 15      # auto-expire no-shows after 15 min past their slot


# ── In-memory OTP store ───────────────────────────────────────────────────────
# In production: replace with Redis  { phone -> {otp, expires, verified} }
_otp_store: dict = {}


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class OTPSendRequest(BaseModel):
    phone: str

class OTPVerifyRequest(BaseModel):
    phone: str
    otp:   str

class SlotGenerateRequest(BaseModel):
    date:       str           # "2026-03-22"
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


# ── OTP: Send ─────────────────────────────────────────────────────────────────

@router.post("/otp/send")
def send_otp(data: OTPSendRequest):
    """
    Generate and store a 6-digit OTP for the given phone.
    In production: replace print() with Twilio / MSG91 call.
    """
    phone = data.phone.strip()
    if not phone or len(phone) < 10:
        raise HTTPException(400, "Invalid phone number.")

    otp = ''.join(random.choices(string.digits, k=6))
    _otp_store[phone] = {
        "otp":      otp,
        "expires":  datetime.utcnow() + timedelta(minutes=10),
        "verified": False
    }

    # TODO in production: send via Twilio
    # from twilio.rest import Client
    # client = Client(TWILIO_SID, TWILIO_TOKEN)
    # client.messages.create(body=f"SmartQueue OTP: {otp}", from_='+1234', to=phone)
    print(f"[OTP] Phone={phone}  OTP={otp}")   # dev only

    return {
        "message":  "OTP sent successfully.",
        "dev_otp":  otp   # REMOVE in production
    }


# ── OTP: Verify ───────────────────────────────────────────────────────────────

@router.post("/otp/verify")
def verify_otp(data: OTPVerifyRequest):
    phone  = data.phone.strip()
    record = _otp_store.get(phone)

    if not record:
        raise HTTPException(400, "No OTP found for this number. Please request a new OTP.")
    if datetime.utcnow() > record["expires"]:
        _otp_store.pop(phone, None)
        raise HTTPException(400, "OTP expired. Please request a new one.")
    if record["otp"] != data.otp.strip():
        raise HTTPException(400, "Incorrect OTP. Please try again.")

    _otp_store[phone]["verified"] = True
    return {"verified": True, "phone": phone}


# ── Admin: Generate slots for a date ─────────────────────────────────────────

@router.post("/generate")
def generate_slots(data: SlotGenerateRequest, db: Session = Depends(get_db)):
    """
    Admin creates time slots for a given date + department.
    Creates 30-min slots from DAY_START to DAY_END.
    Skips slots that already exist.
    """
    try:
        slot_date = datetime.strptime(data.date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(400, "Invalid date format. Use YYYY-MM-DD.")

    if slot_date < date.today():
        raise HTTPException(400, "Cannot generate slots for past dates.")

    created = []
    current_t = datetime.strptime(DAY_START, "%H:%M")
    end_t     = datetime.strptime(DAY_END,   "%H:%M")

    while current_t < end_t:
        slot_time_str = current_t.strftime("%H:%M")
        end_time_str  = (current_t + timedelta(minutes=SLOT_DURATION_MIN)).strftime("%H:%M")

        exists = db.query(AppointmentSlot).filter(
            AppointmentSlot.slot_date  == slot_date,
            AppointmentSlot.slot_time  == slot_time_str,
            AppointmentSlot.department == data.department,
            AppointmentSlot.domain     == Domain(data.domain)
        ).first()

        if not exists:
            slot = AppointmentSlot(
                slot_date  = slot_date,
                slot_time  = slot_time_str,
                slot_end   = end_time_str,
                department = data.department,
                domain     = Domain(data.domain),
                doctor_id  = data.doctor_id,
                capacity   = data.capacity,
                status     = SlotStatus.AVAILABLE
            )
            db.add(slot)
            created.append(slot_time_str)

        current_t += timedelta(minutes=SLOT_DURATION_MIN)

    db.commit()
    return {
        "date":         data.date,
        "department":   data.department,
        "slots_created": len(created),
        "times":        created
    }


# ── Get available slots for a date + department ───────────────────────────────

@router.get("/available")
def get_available_slots(
    date_str:   str,
    department: str,
    domain:     str,
    db:         Session = Depends(get_db)
):
    """
    Returns all slots for the given date/department/domain.
    Shows available count per slot. Full slots are flagged.
    """
    try:
        slot_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(400, "Invalid date format. Use YYYY-MM-DD.")

    slots = db.query(AppointmentSlot).filter(
        AppointmentSlot.slot_date  == slot_date,
        AppointmentSlot.department == department,
        AppointmentSlot.domain     == Domain(domain),
        AppointmentSlot.status     != SlotStatus.CLOSED
    ).order_by(AppointmentSlot.slot_time).all()

    if not slots:
        return {
            "date":       date_str,
            "department": department,
            "slots":      [],
            "message":    "No slots generated for this date. Admin must generate slots first."
        }

    return {
        "date":       date_str,
        "department": department,
        "slots": [
            {
                "id":        s.id,
                "slot_time": s.slot_time,
                "slot_end":  s.slot_end,
                "available": max(0, s.capacity - s.booked_count),
                "capacity":  s.capacity,
                "is_full":   s.booked_count >= s.capacity,
                "status":    s.status.value
            }
            for s in slots
        ]
    }


# ── Book a slot ───────────────────────────────────────────────────────────────

@router.post("/book")
def book_slot(data: SlotBookRequest, db: Session = Depends(get_db)):
    """
    Book a pre-verified slot.
    Requirements:
      1. Phone must have been OTP-verified.
      2. Slot must exist and have available capacity.
      3. Same phone cannot double-book same slot.
    Creates token with status=BOOKED. Token activates on the appointment day.
    """

    # 1. Verify OTP was completed
    otp_record = _otp_store.get(data.phone.strip())
    if not otp_record or not otp_record.get("verified"):
        raise HTTPException(
            400,
            "Phone number not verified. Please complete OTP verification first."
        )

    # 2. Load slot
    slot = db.query(AppointmentSlot).filter(
        AppointmentSlot.id == data.slot_id
    ).first()
    if not slot:
        raise HTTPException(404, "Slot not found.")
    if slot.booked_count >= slot.capacity:
        raise HTTPException(400, "This slot is full. Please choose another time.")
    if slot.status == SlotStatus.CLOSED:
        raise HTTPException(400, "This slot is no longer available.")

    # 3. Prevent duplicate booking (same phone + same slot)
    duplicate = db.query(Token).filter(
        Token.slot_id      == data.slot_id,
        Token.patient_phone == data.phone.strip(),
        Token.status.notin_([TokenStatus.CANCELLED, TokenStatus.EXPIRED])
    ).first()
    if duplicate:
        raise HTTPException(
            400,
            f"Phone {data.phone} already has a booking for this slot: {duplicate.token_number}"
        )

    # 4. Map priority
    priority_map = {
        "emergency": PriorityLevel.EMERGENCY,
        "senior":    PriorityLevel.HIGH,
        "normal":    PriorityLevel.NORMAL
    }

    # 5. Create token in BOOKED status
    token_id = generate_token(data.domain, data.department.upper()[:3])

    # Calculate appointment datetime
    appt_datetime = datetime.combine(
        slot.slot_date,
        datetime.strptime(slot.slot_time, "%H:%M").time()
    )

    # Estimate queue position within this slot
    slot_position = slot.booked_count + 1

    token = Token(
        token_number      = token_id,
        domain            = Domain(data.domain),
        status            = TokenStatus.BOOKED,
        priority          = priority_map.get(data.priority, PriorityLevel.NORMAL),
        slot_id           = data.slot_id,
        patient_name      = data.patient_name,
        patient_phone     = data.phone.strip(),
        symptoms          = data.reason,
        service_name      = data.department,
        appointment_time  = appt_datetime,
        estimated_wait_time = (slot_position - 1) * 8   # 8 min avg service time
    )

    # 6. Increment slot booking count
    slot.booked_count += 1
    if slot.booked_count >= slot.capacity:
        slot.status = SlotStatus.FULL

    db.add(token)
    db.commit()
    db.refresh(token)

    # 7. Clear OTP after successful booking (one-time use)
    _otp_store.pop(data.phone.strip(), None)

    return {
        "token_id":                token_id,
        "slot_time":               slot.slot_time,
        "slot_end":                slot.slot_end,
        "appointment_date":        slot.slot_date.strftime("%Y-%m-%d"),
        "appointment_date_display": slot.slot_date.strftime("%d %B %Y"),
        "department":              data.department,
        "slot_position":           slot_position,
        "estimated_queue_position": slot_position,
        "status":                  "booked",
        "message": (
            f"Appointment confirmed for {slot.slot_date.strftime('%d %b %Y')} "
            f"at {slot.slot_time}. You are #{slot_position} in this slot."
        )
    }


# ── Activate today's booked tokens ────────────────────────────────────────────

@router.post("/activate-today")
def activate_todays_tokens(db: Session = Depends(get_db)):
    """
    Called at midnight (or by APScheduler) to move today's
    BOOKED tokens → ACTIVE so they join the live queue.
    """
    today = date.today()
    booked_today = (
        db.query(Token)
        .join(AppointmentSlot)
        .filter(
            AppointmentSlot.slot_date == today,
            Token.status == TokenStatus.BOOKED
        )
        .all()
    )

    activated = 0
    for token in booked_today:
        token.status = TokenStatus.ACTIVE
        activated += 1

    db.commit()
    return {"activated": activated, "date": str(today)}


# ── Auto-expire no-shows ──────────────────────────────────────────────────────

@router.post("/expire-noshows")
def expire_noshows(db: Session = Depends(get_db)):
    """
    Called every 5 minutes by APScheduler.
    Expires ACTIVE tokens whose appointment_time + EXPIRY_MINUTES has passed
    with no service started.
    """
    cutoff = datetime.utcnow() - timedelta(minutes=EXPIRY_MINUTES)

    no_shows = db.query(Token).filter(
        Token.status             == TokenStatus.ACTIVE,
        Token.appointment_time   != None,
        Token.appointment_time   <  cutoff,
        Token.service_started_at == None
    ).all()

    count = 0
    for token in no_shows:
        token.status     = TokenStatus.EXPIRED
        token.expired_at = datetime.utcnow()
        count += 1

    db.commit()
    return {"expired": count, "checked_at": datetime.utcnow().isoformat()}


# ── Get booking details by token number ──────────────────────────────────────

@router.get("/booking/{token_number}")
def get_booking(token_number: str, db: Session = Depends(get_db)):
    """Get full booking details for a token (used on confirmation page)."""
    token = db.query(Token).filter(Token.token_number == token_number).first()
    if not token:
        raise HTTPException(404, "Token not found.")

    slot = token.slot
    return {
        "token_id":      token.token_number,
        "status":        token.status.value,
        "department":    token.service_name,
        "priority":      token.priority.value,
        "patient_name":  token.patient_name,
        "appointment_date": slot.slot_date.strftime("%d %B %Y") if slot else None,
        "slot_time":     slot.slot_time if slot else None,
        "slot_end":      slot.slot_end  if slot else None,
        "available_in_slot": max(0, slot.capacity - slot.booked_count) if slot else None,
        "estimated_wait": token.estimated_wait_time
    }
