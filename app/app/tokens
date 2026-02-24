from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas import TokenCreate, TokenResponse
from app.models import Token, TokenStatus
from app.utils.token_generator import generate_token
from app.auth.auth import get_current_active_user

router = APIRouter()


@router.post("/", response_model=TokenResponse)
def create_token(
    data: TokenCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    token_number = generate_token(data.domain.value, "S")

    token = Token(
        token_number=token_number,
        user_id=user.id,
        queue_id=data.queue_id,
        domain=data.domain,
        status=TokenStatus.ACTIVE
    )

    db.add(token)
    db.commit()
    db.refresh(token)
    return token
