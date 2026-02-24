from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas import QueueCreate, QueueResponse
from app.models import Queue
from app.auth.auth import get_admin_user

router = APIRouter()


@router.post("/", response_model=QueueResponse)
def create_queue(
    data: QueueCreate,
    db: Session = Depends(get_db),
    _=Depends(get_admin_user)
):
    queue = Queue(**data.dict())
    db.add(queue)
    db.commit()
    db.refresh(queue)
    return queue


@router.get("/", response_model=list[QueueResponse])
def list_queues(db: Session = Depends(get_db)):
    return db.query(Queue).filter(Queue.is_active == True).all()
