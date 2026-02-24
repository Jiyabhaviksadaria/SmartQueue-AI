from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models import Token
from app.auth.auth import get_admin_user

router = APIRouter()


@router.get("/live-tokens")
def live_tokens(db: Session = Depends(get_db), _=Depends(get_admin_user)):
    return db.query(Token).all()
