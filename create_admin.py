from app.database.db import SessionLocal, engine
from app.models import Base, User
from app.auth.auth import get_password_hash

Base.metadata.create_all(bind=engine)
db = SessionLocal()

existing = db.query(User).filter(User.username == 'admin').first()
if existing:
    print("Admin user already exists!")
else:
    admin = User(
        username='admin',
        email='admin@smartqueue.com',
        hashed_password=get_password_hash('admin123'),
        full_name='Admin User',
        role='admin',
        is_active=True
    )
    db.add(admin)
    db.commit()
    print("Admin user created!")

db.close()