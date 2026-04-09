"""
Run this once to fix all tokens in the database:
- Resets negative wait times to positive values
- Fixes null positions
- Recalculates queue order properly

Run with: python fix_tokens.py
"""
from app.database.db import SessionLocal, engine
from app.models import Base, Token, TokenStatus, PriorityLevel

Base.metadata.create_all(bind=engine)
db = SessionLocal()

print("Fixing tokens in database...")

# Get all active tokens
active_tokens = db.query(Token).filter(
    Token.status.in_([TokenStatus.ACTIVE, TokenStatus.CREATED])
).all()

print(f"Found {len(active_tokens)} active tokens")

if not active_tokens:
    print("No active tokens found!")
    print("\nAll tokens in DB:")
    all_tokens = db.query(Token).all()
    for t in all_tokens:
        print(f"  {t.token_number} | status={t.status} | position={t.position} | wait={t.estimated_wait_time}")
else:
    # Sort by priority then id (original creation order)
    priority_order = {
        PriorityLevel.EMERGENCY: 0,
        PriorityLevel.HIGH:      1,
        PriorityLevel.MEDIUM:    2,
        PriorityLevel.NORMAL:    3,
    }

    active_tokens.sort(key=lambda t: (
        priority_order.get(t.priority, 3),
        t.id  # use id for original order
    ))

    avg_service_time = 8  # minutes per person

    for new_position, token in enumerate(active_tokens, start=1):
        old_pos  = token.position
        old_wait = token.estimated_wait_time

        token.position           = new_position
        token.estimated_wait_time = max(0, (new_position - 1) * avg_service_time)

        print(f"  {token.token_number}: pos {old_pos}→{new_position} | wait {old_wait}→{token.estimated_wait_time} min")

    db.commit()
    print(f"\n✅ Fixed {len(active_tokens)} tokens successfully!")

db.close()
print("Done! Refresh your admin dashboard and tracking page.")
