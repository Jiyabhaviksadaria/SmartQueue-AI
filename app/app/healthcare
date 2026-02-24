from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.database.db import get_db
from app.auth.auth import get_doctor_user
from app.models import DoctorProfile, Token, Queue, TokenStatus, PriorityLevel, Domain
from app.utils.token_generator import generate_token

router = APIRouter()


class HealthcareTokenCreate(BaseModel):
    patient_name: str
    phone: str
    department: str
    doctor_id: Optional[str] = None
    priority: str = "normal"
    age: Optional[int] = None
    gender: Optional[str] = None
    reason: Optional[str] = None


@router.post("/token")
def create_healthcare_token(data: HealthcareTokenCreate, db: Session = Depends(get_db)):
    """Create a new healthcare token without authentication"""
    try:
        # Generate token ID
        token_id = generate_token("healthcare", data.department.upper()[:3])
        
        # Calculate position
        position = db.query(Token).filter(
            Token.domain == Domain.HEALTHCARE,
            Token.status == TokenStatus.ACTIVE
        ).count() + 1
        
        # Priority-based wait time
        wait_times = {"emergency": 2, "senior": 8, "normal": 15}
        estimated_wait = wait_times.get(data.priority, 15)
        
        # Map priority string to enum
        priority_map = {
            "emergency": PriorityLevel.EMERGENCY,
            "senior": PriorityLevel.HIGH,
            "normal": PriorityLevel.NORMAL
        }
        
        # Create token
        token = Token(
            token_number=token_id,
            domain=Domain.HEALTHCARE,
            status=TokenStatus.ACTIVE,
            priority=priority_map.get(data.priority, PriorityLevel.NORMAL),
            position=position,
            estimated_wait_time=estimated_wait,
            symptoms=data.reason,
            service_name=data.department
        )
        
        db.add(token)
        db.commit()
        db.refresh(token)
        
        return {
            "token_id": token_id,
            "position": position,
            "estimated_wait_time": estimated_wait,
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue")
def get_healthcare_queue(department: Optional[str] = None, db: Session = Depends(get_db)):
    """Get healthcare queue status"""
    try:
        query = db.query(Token).filter(
            Token.domain == Domain.HEALTHCARE,
            Token.status == TokenStatus.ACTIVE
        )
        
        if department:
            query = query.filter(Token.service_name == department)
        
        count = query.count()
        
        return [{
            "department": department or "all",
            "count": count,
            "status": "active"
        }]
    except Exception as e:
        return []


@router.patch("/doctors/{doctor_id}/availability")
def update_availability(
    doctor_id: int,
    available: bool,
    db: Session = Depends(get_db),
    _=Depends(get_doctor_user)
):
    doctor = db.query(DoctorProfile).filter(DoctorProfile.id == doctor_id).first()
    if doctor:
        doctor.is_available = available
        db.commit()
    return {"status": "updated"}
