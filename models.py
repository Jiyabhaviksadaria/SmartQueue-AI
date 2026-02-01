"""
Database Models for SmartQueue AI
SQLAlchemy ORM Models

SAVE THIS FILE AS: app/models.py
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database.db import Base

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

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    phone = Column(String)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    is_senior_citizen = Column(Boolean, default=False)
    is_vip = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tokens = relationship("Token", back_populates="user")
    doctor_profile = relationship("DoctorProfile", back_populates="user", uselist=False)

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

class Queue(Base):
    __tablename__ = "queues"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    domain = Column(Enum(Domain), nullable=False)
    department = Column(String)
    service_type = Column(String)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    counter_number = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    capacity = Column(Integer, default=50)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    doctor = relationship("DoctorProfile", back_populates="queues")
    tokens = relationship("Token", back_populates="queue")

class Token(Base):
    __tablename__ = "tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token_number = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    queue_id = Column(Integer, ForeignKey("queues.id"))
    domain = Column(Enum(Domain), nullable=False)
    status = Column(Enum(TokenStatus), default=TokenStatus.CREATED)
    priority = Column(Enum(PriorityLevel), default=PriorityLevel.NORMAL)
    position = Column(Integer)
    
    symptoms = Column(Text, nullable=True)
    consultation_type = Column(String, nullable=True)
    severity_score = Column(Integer, nullable=True)
    service_required = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    called_at = Column(DateTime, nullable=True)
    service_started_at = Column(DateTime, nullable=True)
    service_completed_at = Column(DateTime, nullable=True)
    expired_at = Column(DateTime, nullable=True)
    
    estimated_wait_time = Column(Integer, nullable=True)
    actual_wait_time = Column(Integer, nullable=True)
    actual_service_time = Column(Integer, nullable=True)
    
    user = relationship("User", back_populates="tokens")
    queue = relationship("Queue", back_populates="tokens")
    audit_logs = relationship("AuditLog", back_populates="token")

class ServiceHistory(Base):
    __tablename__ = "service_history"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(Enum(Domain), nullable=False)
    department = Column(String)
    service_type = Column(String)
    doctor_id = Column(Integer, nullable=True)
    counter_number = Column(String, nullable=True)
    service_time = Column(Integer)
    wait_time = Column(Integer)
    priority = Column(Enum(PriorityLevel))
    queue_length = Column(Integer)
    hour_of_day = Column(Integer)
    day_of_week = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

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

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token_id = Column(Integer, ForeignKey("tokens.id"), nullable=True)
    type = Column(String)
    subject = Column(String)
    message = Column(Text)
    sent_at = Column(DateTime, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
