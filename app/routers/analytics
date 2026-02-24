from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.services.analytics_service import (
    average_wait_time,
    peak_hour_analysis,
    staff_performance
)
from app.auth.auth import get_admin_user

router = APIRouter()


@router.get("/average-wait/{queue_id}")
def avg_wait(queue_id: int, db: Session = Depends(get_db), _=Depends(get_admin_user)):
    return {"average_wait_time": average_wait_time(db, queue_id)}


@router.get("/peak-hours")
def peak_hours(db: Session = Depends(get_db), _=Depends(get_admin_user)):
    return peak_hour_analysis(db)


@router.get("/staff-performance")
def performance(db: Session = Depends(get_db), _=Depends(get_admin_user)):
    return staff_performance(db)
