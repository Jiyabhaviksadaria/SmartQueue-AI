from sqlalchemy.orm import Session
from app.models import Token, Queue, TokenStatus
from app.services.priority_engine import calculate_priority

def add_token_to_queue(db: Session, token: Token, queue: Queue):
    priority = calculate_priority(token, queue)
    token.priority = priority

    active_tokens = (
        db.query(Token)
        .filter(Token.queue_id == queue.id, Token.status == TokenStatus.ACTIVE)
        .order_by(Token.priority.desc(), Token.created_at)
        .all()
    )

    token.position = len(active_tokens) + 1
    db.add(token)
    db.commit()
