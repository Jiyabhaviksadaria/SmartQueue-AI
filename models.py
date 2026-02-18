"""
Database Models for SmartQueue AI
SQLAlchemy ORM Models

SAVE THIS FILE AS: app/models.py
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, Float,
    Boolean, ForeignKey, Enum, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database.db import Base


# ======================================================
# ENUMS
# ======================================================

class UserRole(str, enum.Enum):
    PATIENT = "patient"
    CUSTOMER = "customer"
    ADMIN = "admin"
    DOCTOR = "doctor"
    BANK_STAFF = "bank_staff"
    COUNTER_OPERATOR = "counter_operator"


class TokenStatus(str, enum.Enum):
    CREATED = "created"
    ACTIVE = "active"
    IN_SERVICE = "in_service"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class PriorityLevel(str, enum.Enum):
    EMERGENCY = "emergency"
    HIGH = "high"
    MEDIUM = "medium"
    NORMAL = "normal"


class Domain(str, enum.Enum):
    HEALTHCARE = "healthcare"
    BANKING = "banking"


# ======================================================
# USER
# ======================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    full_name = Column(String)
    phone = Column(String)

    role = Column(Enum(UserRole), nullable=False, index=True)

    is_active = Column(Boolean, default=True)
    is_senior_citizen = Column(Boolean, default=False)
    is_vip = Column(Boolean, default=False)

    last_login = Column(DateTime)
    refresh_token = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    tokens = relationship("Token", back_populates="user")
    doctor_profile = relationship(
        "DoctorProfile",
        back_populates="user",
        uselist=False
    )


# ======================================================
# DOCTOR PROFILE
# ======================================================

class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    specialization = Column(String)
    department = Column(String)

    is_available = Column(Boolean, default=True)
    avg_consultation_time = Column(Integer, default=15)

    user = relationship("User", back_populates="doctor_profile")
    queues = relationship("Queue", back_populates="doctor")


# ======================================================
# QUEUE
# ======================================================

class Queue(Base):
    __tablename__ = "queues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    domain = Column(Enum(Domain), nullable=False, index=True)
    department = Column(String)

    service_name = Column(String)
    queue_type = Column(String)  # walk-in / appointment / emergency

    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id"), nullable=True)
    counter_number = Column(String, nullable=True)

    capacity = Column(Integer, default=50)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    doctor = relationship("DoctorProfile", back_populates="queues")
    tokens = relationship("Token", back_populates="queue")


# ======================================================
# TOKEN
# ======================================================

class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    token_number = Column(String, unique=True, index=True, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"))
    queue_id = Column(Integer, ForeignKey("queues.id"))

    domain = Column(Enum(Domain), nullable=False, index=True)
    status = Column(Enum(TokenStatus), default=TokenStatus.CREATED, index=True)
    priority = Column(Enum(PriorityLevel), default=PriorityLevel.NORMAL, index=True)

    position = Column(Integer)

    # Service details
    symptoms = Column(Text)
    consultation_type = Column(String)
    service_name = Column(String)
    severity_score = Column(Integer)

    appointment_time = Column(DateTime, nullable=True)

    # Time tracking
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    called_at = Column(DateTime)
    service_started_at = Column(DateTime)
    service_completed_at = Column(DateTime)
    expired_at = Column(DateTime)

    # AI Metrics
    estimated_wait_time = Column(Integer)
    actual_wait_time = Column(Integer)
    actual_service_time = Column(Integer)

    prediction_confidence = Column(Float)
    ml_model_version = Column(String)

    user = relationship("User", back_populates="tokens")
    queue = relationship("Queue", back_populates="tokens")
    audit_logs = relationship("AuditLog", back_populates="token")

    # ======================================================
    # FRONTEND COMPATIBILITY (DO NOT REMOVE)
    # ======================================================

    @property
    def frontend_id(self):
        # frontend expects: id
        return self.token_number

    @property
    def frontend_type(self):
        # frontend expects: type
        return self.domain.value if self.domain else None

    @property
    def estimatedWait(self):
        # frontend expects: estimatedWait
        return self.estimated_wait_time

    @property
    def frontend_priority(self):
        # frontend uses: emergency | senior | normal
        if self.priority == PriorityLevel.EMERGENCY:
            return "emergency"
        if self.priority in (PriorityLevel.HIGH, PriorityLevel.MEDIUM):
            return "senior"
        return "normal"

    @property
    def department(self):
        # frontend expects department directly
        return self.queue.department if self.queue else None

    @property
    def doctor(self):
        # frontend expects doctor as string
        if self.queue and self.queue.doctor and self.queue.doctor.user:
            return self.queue.doctor.user.full_name
        return "Any Available"


# ======================================================
# SERVICE HISTORY (AI TRAINING DATA)
# ======================================================

class ServiceHistory(Base):
    __tablename__ = "service_history"

    id = Column(Integer, primary_key=True, index=True)

    domain = Column(Enum(Domain), nullable=False, index=True)
    department = Column(String)
    service_name = Column(String)

    doctor_id = Column(Integer, nullable=True)
    counter_number = Column(String, nullable=True)

    service_time = Column(Integer)
    wait_time = Column(Integer)

    priority = Column(Enum(PriorityLevel))

    queue_length = Column(Integer)
    hour_of_day = Column(Integer)
    day_of_week = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# ======================================================
# AUDIT LOG
# ======================================================

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    token_id = Column(Integer, ForeignKey("tokens.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    action = Column(String, nullable=False)
    details = Column(Text)
    ip_address = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    token = relationship("Token", back_populates="audit_logs")
    user = relationship("User")


# ======================================================
# NOTIFICATION
# ======================================================

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    token_id = Column(Integer, ForeignKey("tokens.id"), nullable=True)

    type = Column(String)
    subject = Column(String)
    message = Column(Text)

    sent_at = Column(DateTime)
    status = Column(String, default="pending")

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    token = relationship("Token")
