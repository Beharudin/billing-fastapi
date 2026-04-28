from core.database import SessionLocal, Base, engine
from models.user import User
from core.security import hash_password
import os

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

if not ADMIN_EMAIL or not ADMIN_PASSWORD:
    print("ADMIN_EMAIL and ADMIN_PASSWORD must be set in environment to bootstrap admin")
    raise SystemExit(1)


db = SessionLocal()
try:
    existing = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if existing:
        print("Admin user already exists")
    else:
        # enforce bcrypt 72-byte limit
        if len(ADMIN_PASSWORD.encode("utf-8")) > 72:
            print("ADMIN_PASSWORD must be at most 72 bytes when encoded in UTF-8")
            raise SystemExit(1)

        user = User(
            email=ADMIN_EMAIL,
            password=hash_password(ADMIN_PASSWORD),
            role="admin",
            is_active=True
        )
        db.add(user)
        db.commit()
        print("Admin user created")
finally:
    db.close()
