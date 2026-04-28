from sqlalchemy.orm import Session
from models.user import User
from models.enums import RoleEnum
from core.security import hash_password, verify_password


def register_user(db: Session, email: str, password: str, is_active: bool):
    user = User(
        email=email,
        password=hash_password(password),
        role=RoleEnum.MEMBER,
        is_active=is_active,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def register_admin(db: Session, email: str, password: str, role: RoleEnum, is_active: bool):

    user = User(
        email=email,
        password=hash_password(password),
        role=role,
        is_active=is_active,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(db: Session, email: str, password: str):

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user